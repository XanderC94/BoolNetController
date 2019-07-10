'''
BN Evaluation utility module
'''
import re
import math
import pandas
import statistics
import subprocess
from pathlib import Path
from itertools import product
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.sim.config import SimulationConfig, CONFIG_CLI_NAMES
from bncontroller.sim.data import Point3D, r_point3d, Axis, Quadrant
from bncontroller.boolnet.eval.search.parametric import parametric_vns
from bncontroller.sim.logging.logger import staticlogger as logger
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.file.utils import generate_file_name

def compare_scores(minimize, maximize):

    if isinstance(minimize, (float, int, bool)) and isinstance(maximize, (float, int, bool)):
        return minimize < maximize
    # elif isinstance(new, list) and isinstance(old, list):
    #     nmean, nstdev = statistics.mean(new), statistics.stdev(new)
    #     omean, ostdev = statistics.mean(old), statistics.stdev(old)

    #     return nstdev < ostdev if nmean == omean else nmean < omean
    elif isinstance(minimize, tuple) and isinstance(maximize, tuple):
        minmean, minstdev, *_ = minimize
        maxmean, maxstdev, *_ = maximize

        return minstdev < maxstdev if minmean == maxmean else minmean < maxmean
    # elif isinstance(new, list) and isinstance(old, float):
    #     return statistics.mean(new) < old
    # elif isinstance(new, float) and isinstance(old, list):
    #     return new < statistics.mean(old)
    elif isinstance(minimize, tuple) and isinstance(maximize, float):
        return minimize[0] < maximize
    elif isinstance(minimize, float) and isinstance(maximize, tuple):
        return minimize < maximize[0]
    else:
        raise Exception(f'Uncomparable values {type(minimize)} and {type(maximize)}')
        
###############################################################################################

def evaluation(config: SimulationConfig, bn: OpenBooleanNetwork, compare = compare_scores):

    test_params = product(
        config.globals['agent_spawn_points'], 
        config.globals['light_spawn_points'], 
        config.globals['agent_yrots']
    )

    fscores = []
    dscores = []

    for apos, lpos, yrot in test_params:

        config.sim_agent_position = apos
        config.sim_light_position = lpos
        config.sim_agent_yrot_rad = yrot

        data = run_simulation(config, bn)

        fs, ds = aggregate_sim_data(lpos, data)

        logger.info(
            'iDistance:', config.sim_light_position.dist(config.sim_agent_position),
            f'yRot: {(config.sim_agent_yrot_rad / math.pi * 180)}°',
            'fDistance:', ds,
            'score: ', fs,
        )

        fscores.append(fs)
        dscores.append(ds)

    new_score = statistics.mean(fscores), statistics.stdev(fscores)
    
    if compare(new_score, config.globals['score']):
        config.globals['score'] = new_score

        save_subopt_model(
            new_score,
            config,
            bn.to_json()
        )

    config.globals['it'] += 1

    return new_score
    
def run_simulation(config : SimulationConfig, bn: OpenBooleanNetwork) -> dict:

    # Save model (inside or outside of the config? mumble rumble)
    write_json(bn.to_json(), config.bn_model_path) # BN Model
    write_json(config.to_json(), config.sim_config_path, indent=True) # Simulation Configuration

    # Run Webots    
    subprocess.run([
        str(config.webots_path), *config.webots_launch_args, str(config.webots_world_path)
    ])

    return read_json(config.sim_data_path)

def aggregate_sim_data(light_position: Point3D, sim_data: dict) -> float:

    df = pandas.DataFrame(sim_data['data'])

    df['aggr_light_values'] = df['light_values'].apply(lambda lvs: max(lvs.values()))

    score = df['aggr_light_values'].sum(axis=0, skipna=True) 

    max_step = df['n_step'].max()

    final_pos = df[df['n_step'] == max_step]['position'].T.values[0]

    return (1 / score if score > 0 else float('+inf')), round(light_position.dist(final_pos), 5)

def save_subopt_model(new_score:float, config:SimulationConfig, bnjson:dict):
        
    bnjson.update({'sim_info': dict()})

    bnjson['sim_info'].update({'eval_score':config.globals['score']})
    bnjson['sim_info'].update({'idist':config.sim_light_position.dist(config.sim_agent_position)})
    bnjson['sim_info'].update({'n_it':config.globals['it']})

    model_dir = config.bn_model_path if config.bn_model_path.is_dir() else config.bn_model_path.parent

    if compare_scores(config.globals['score'], config.train_save_suboptimal_models): 
        # Save only if <sd_save_suboptimal_models> >= score
        write_json(bnjson, model_dir / config.globals['top_model_name'].format(
            date=config.globals['date'],
            subfix=config.globals['subopt_suffix'].format(it=config.globals['it'])
        ))
        
    # Always save the last suboptimal model (overwrite)
    write_json(bnjson, model_dir / config.globals['top_model_name'].format(
        date=config.globals['date'], 
        subfix=''
    ))

###############################################################################################

def search_bn_controller(config: SimulationConfig, bn: OpenBooleanNetwork):

    return parametric_vns(
        bn,
        evaluate=lambda bn: evaluation(config, bn, compare=compare_scores),
        compare=lambda minimize, maximize: compare_scores(minimize, maximize),
        min_target=config.sd_minimization_target,
        max_iters=config.sd_max_iters,
        max_stalls=config.sd_max_stalls,
        max_stagnation=config.sd_max_stagnation
    )