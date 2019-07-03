from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.bn import rbn_gen
from bncontroller.sim.config import SimulationConfig
from bncontroller.sim.data import Point3D, r_point3d, Axis, Quadrant
from bncontroller.boolnet.eval.search.parametric import parametric_vns
from bncontroller.sim.logging.logger import staticlogger as logger
from bncontroller.json.utils import read_json, write_json
from bncontroller.file.utils import generate_file_name
from pathlib import Path
import subprocess, pandas, math, random, re
from bncontroller.stubs.globals import app_globals as __globals

def evaluation(config: SimulationConfig, bn: OpenBooleanNetwork) -> float:
    
    sim_config = generate_ad_hoc_sim_config(config)

    edit_webots_worldfile(sim_config)

    data = run_simulation(sim_config, bn)

    new_score, rscore = aggregate_sim_data(sim_config.sim_light_position, data)

    logger.info(
        'iDistance:', sim_config.sim_light_position.dist(sim_config.sim_agent_position),
        f'yRot: {(sim_config.sim_agent_y_rot_rad / math.pi * 180)}°',
        'fDistance:', rscore
    )

    save_subopt_model(
        new_score, 
        rscore,
        sim_config,
        bn.to_json()
    )

    return new_score

def generate_ad_hoc_sim_config(config:SimulationConfig, keyword='sim', p_quads=[Quadrant.NPP, Quadrant.PPN]):
    
    model_fname = generate_file_name(f'{keyword}_bn', uniqueness_gen= lambda: __globals['date'], ftype='json')
    data_fname = generate_file_name(f'{keyword}_data', uniqueness_gen= lambda: __globals['date'], ftype='json')
    log_fname = generate_file_name(f'{keyword}_log', uniqueness_gen= lambda: __globals['date'], ftype='json')
    config_fname = generate_file_name(f'{keyword}_config', uniqueness_gen= lambda: __globals['date'], ftype='json')

    # Create Sim Config based on the Experiment Config
    sim_config = SimulationConfig.from_json(config.to_json())
    
    sim_config.sim_light_position = r_point3d(
        O=config.sim_light_position, 
        R=config.sim_light_spawn_radius, 
        axis=Axis.Y, 
        quadrant=p_quads[0]
    )

    sim_config.sim_agent_position = r_point3d(
        O=config.sim_agent_position, 
        R=config.sim_agent_spawn_radius, 
        axis=Axis.Y, 
        quadrant=p_quads[-1]
    )

    sim_config.sim_agent_y_rot_rad = random.uniform(0, 2*math.pi) #

    sim_config.bn_model_path /= model_fname
    sim_config.sim_data_path /= data_fname
    sim_config.sim_log_path /= log_fname
    sim_config.sim_config_path /= config_fname

    return sim_config


def edit_webots_worldfile(config:SimulationConfig):

    if config.sim_config_path.is_dir():
        raise Exception('Configuration path is not a file.')

    with open(config.webots_world_path, 'r+') as fp:

        wdata=fp.readlines()
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
    excode = subprocess.run([
        str(config.webots_path), *config.webots_launch_args, str(config.webots_world_path)
    ])
    
    data = read_json(config.sim_data_path)

    return data

def aggregate_sim_data(light_position: Point3D, sim_data: dict) -> float:

    df = pandas.DataFrame(sim_data['data'])

    df['aggr_light_values'] = df['light_values'].apply(lambda lvs: max(lvs.values()))
    # df['aggr_light_values'] = df['light_values'].apply(lambda lvs: sum(lvs.values()))

    score = df['aggr_light_values'].sum(axis=0, skipna=True) 

    max_step = df['n_step'].max()

    final_pos = df[df['n_step'] == max_step]['position'].T.values[0]

    return (1 / score if score > 0 else float('+inf')), round(light_position.dist(final_pos), 5)


def save_subopt_model(new_score:float, fdist:float, sim_config:SimulationConfig, bnjson:dict):

    __globals['it'] += 1

    if new_score < __globals['score']:

        __globals['score'] = new_score
        
        bnjson.update({'sim_info': dict()})

        bnjson['sim_info'].update({'eval_score':__globals['score']})
        bnjson['sim_info'].update({'fdist':fdist})
        bnjson['sim_info'].update({'idist':sim_config.sim_light_position.dist(sim_config.sim_agent_position)})
        bnjson['sim_info'].update({'n_it':__globals['it']})
        bnjson['sim_info'].update({'y_rot':sim_config.sim_agent_y_rot_rad})

        model_dir = sim_config.bn_model_path if sim_config.bn_model_path.is_dir() else sim_config.bn_model_path.parent

        if __globals['score'] <= sim_config.sd_save_suboptimal_models: 
            # Save only if <sd_save_suboptimal_models> > score
            write_json(bnjson, model_dir / __globals['top_model_name'].format(
                subfix=__globals['subopt_suffix'].format(it=__globals['it'])
            ))
        elif not sim_config.sd_save_suboptimal_models: 
            # Save only if <sd_save_suboptimal_models> = 0.0
            write_json(bnjson, model_dir / __globals['top_model_name'].format(subfix=''))
    
        return 1
    else:
        return 0

###############################################################################################

def search_bn_controller(config : SimulationConfig, bn: OpenBooleanNetwork):

    return parametric_vns(
        bn,
        evaluate=lambda bn: evaluation(config, bn),
        max_iters=config.sd_max_iters,
        max_stalls=config.sd_max_stalls,
        min_target=config.sd_minimization_target
    )