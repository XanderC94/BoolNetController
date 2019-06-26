from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.bn import rbn_gen
from bncontroller.sim.config import SimulationConfig
from bncontroller.sim.data import Point3D, r_point3d, Axis, Quadrant
from bncontroller.boolnet.eval.search.parametric import parametric_vns
from bncontroller.sim.logging.logger import staticlogger as logger
from bncontroller.json.utils import read_json, write_json
from bncontroller.file.utils import generate_file_name, iso8106
from pathlib import Path
import subprocess, pandas, math, random, re

__globals = dict(
    date = iso8106(ms=3),
    score = -1.0,
    it = -1,
    top_model_name = f'bn_{iso8106()}_'+'it{it}.json',
)

def evaluation(config: SimulationConfig, bn: OpenBooleanNetwork) -> float:
    
    sim_config = generate_ad_hoc_sim_config(config)

    data = run_simulation(sim_config, bn)

    new_score, rscore = aggregate_sim_data(sim_config.sim_light_position, data)

    logger.info(
        'boot distance:', sim_config.sim_light_position.dist(sim_config.sim_agent_position),
        'yrot:', sim_config.sim_agent_y_rot_rad / math.pi * 180,
        'real distance:', rscore
    )

    __globals['it'] += 1

    if __globals['score'] < 0.0 or new_score < __globals['score']:

        __globals['score'] = new_score

        bnjson = bn.to_json()
        
        bnjson.update({'sim_info': dict()})
        bnjson['sim_info'].update({'eval_score':__globals['score']})
        bnjson['sim_info'].update({'y_rot':sim_config.sim_agent_y_rot_rad})
        bnjson['sim_info'].update({'n_it':__globals['it']})

        write_json(bnjson, config.bn_model_path / __globals['top_model_name'].format(
            it=__globals['it']) if config.sd_save_suboptimal_models else ''
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

    with open(sim_config.webots_world_path, 'r+') as fp:

        wdata=fp.readlines()
        p = str(sim_config.sim_config_path).replace('\\', '\\\\')
        for i in range(len(wdata)):
            
            spaces = '  ' if wdata[i].startswith('  ') else '\t'
            if re.match(r'  controllerArgs \".*\"\n', wdata[i]) is not None:
                wdata[i] = f'  controllerArgs \"--config_path=\\\"{p}\\\"\"\n'
            elif re.match(r'\tcontrollerArgs \".*\"\n', wdata[i]) is not None:
                wdata[i] = f'\tcontrollerArgs \"--config_path=\\\"{p}\\\"\"\n'

        fp.seek(0)
        fp.write(''.join(wdata))

    return sim_config

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

###############################################################################################

def search_bn_controller(config : SimulationConfig, bn: OpenBooleanNetwork):

    return parametric_vns(
        bn,
        evaluate=lambda bn: evaluation(config, bn),
        max_iters=config.sd_max_iters,
        max_stalls=config.sd_max_stalls,
        min_target=config.sd_minimization_target
    )