'''
BN Evaluation utility module
'''
import re
import math
import pandas
import statistics
import subprocess
from itertools import product
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.sim.config import SimulationConfig
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
        raise Exception(f'Uncomparable values {type(new)} and {type(old)}')
        
###############################################################################################

def evaluation(config: SimulationConfig, bn: OpenBooleanNetwork):

    test_params = product(
        config.globals['agent_spawn_points'], 
        config.globals['light_spawn_points'], 
        config.globals['agent_yrots']
    )

    sim_config = generate_ad_hoc_sim_config(config)
    
    edit_webots_worldfile(sim_config)

    fscores = []
    dscores = []

    for apos, lpos, yrot in test_params:

        sim_config.sim_agent_position = apos
        sim_config.sim_light_position = lpos
        sim_config.sim_agent_yrot_rad = yrot

        data = run_simulation(sim_config, bn)

        fs, ds = aggregate_sim_data(lpos, data)

        logger.info(
            'iDistance:', sim_config.sim_light_position.dist(sim_config.sim_agent_position),
            f'yRot: {(sim_config.sim_agent_yrot_rad / math.pi * 180)}°',
            'fDistance:', ds,
            'score: ', fs,
        )

        fscores.append(fs)
        dscores.append(ds)

    new_score = statistics.mean(fscores), statistics.stdev(fscores)
    
    if compare_scores(new_score, config.globals['score']):
        sim_config.globals['score'] = new_score

        save_subopt_model(
            new_score,
            config,
            bn.to_json()
        )

    sim_config.globals['it'] += 1

    return new_score

def generate_ad_hoc_sim_config(config:SimulationConfig, keyword='sim'):
    
    model_fname = generate_file_name(f'{keyword}_bn', uniqueness_gen= lambda: config.globals['date'], ftype='json')
    data_fname = generate_file_name(f'{keyword}_data', uniqueness_gen= lambda: config.globals['date'], ftype='json')
    log_fname = generate_file_name(f'{keyword}_log', uniqueness_gen= lambda: config.globals['date'], ftype='json')
    config_fname = generate_file_name(f'{keyword}_config', uniqueness_gen= lambda: config.globals['date'], ftype='json')

    # Create Sim Config based on the Experiment Config
    sim_config = SimulationConfig.from_json(config.to_json())

    sim_config.bn_model_path /= model_fname
    sim_config.sim_data_path /= data_fname
    sim_config.sim_log_path /= log_fname
    sim_config.sim_config_path /= config_fname

    return sim_config

def edit_webots_worldfile(config:SimulationConfig):

    if config.sim_config_path.is_dir():
        raise Exception('Configuration path is not a file.')

    with open(config.webots_world_path, 'r+') as fp:

        wdata = fp.readlines()
        p = str(config.sim_config_path).replace('\\', '/')
        for i in range(len(wdata)):
            
            spaces = '  ' if wdata[i].startswith('  ') else '\t'
            if re.match(r'  controllerArgs \".*\"\n', wdata[i]) is not None:
                wdata[i] = f'  controllerArgs \"--config_path=\\\"{p}\\\"\"\n'
            elif re.match(r'\tcontrollerArgs \".*\"\n', wdata[i]) is not None:
                wdata[i] = f'\tcontrollerArgs \"--config_path=\\\"{p}\\\"\"\n'

        fp.seek(0)
        fp.write(''.join(wdata))

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

def save_subopt_model(new_score:float, sim_config:SimulationConfig, bnjson:dict):
        
    bnjson.update({'sim_info': dict()})

    bnjson['sim_info'].update({'eval_score':sim_config.globals['score']})
    bnjson['sim_info'].update({'idist':sim_config.sim_light_position.dist(sim_config.sim_agent_position)})
    bnjson['sim_info'].update({'n_it':sim_config.globals['it']})

    model_dir = sim_config.bn_model_path if sim_config.bn_model_path.is_dir() else sim_config.bn_model_path.parent

    if compare_scores(sim_config.globals['score'], sim_config.train_save_suboptimal_models): 
        # Save only if <sd_save_suboptimal_models> >= score
        write_json(bnjson, model_dir / sim_config.globals['top_model_name'].format(
            date=sim_config.globals['date'],
            subfix=sim_config.globals['subopt_suffix'].format(it=sim_config.globals['it'])
        ))
        
    # Always save the last suboptimal model (overwrite)
    write_json(bnjson, model_dir / sim_config.globals['top_model_name'].format(
        date=sim_config.globals['date'], 
        subfix=''
    ))

###############################################################################################

def search_bn_controller(config: SimulationConfig, bn: OpenBooleanNetwork):

    return parametric_vns(
        bn,
        evaluate=lambda bn: evaluation(config, bn),
        compare=lambda new, old: compare_scores(new, old),
        min_target=config.sd_minimization_target,
        max_iters=config.sd_max_iters,
        max_stalls=config.sd_max_stalls,
        max_stagnation=config.sd_max_stagnation
    )