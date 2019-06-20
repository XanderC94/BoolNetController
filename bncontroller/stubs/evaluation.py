from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.bn import rbn_gen
from bncontroller.sim.config import SimulationConfig
from bncontroller.sim.data import Point3D, r_point3d, Axis, Quadrant
from bncontroller.boolnet.eval.search.parametric import parametric_vns
# from bncontroller.boolnet.eval.search.incremental import incremental_stochastic_descent
from bncontroller.json.utils import read_json, write_json
from bncontroller.file.utils import generate_file_name, iso8106
from pathlib import Path
import subprocess, pandas, math, random

__globals = dict(
    date = iso8106(),
    score = -1.0,
    it = -1,
    top_model_name = f'bn_model_top_{iso8106()}.json',
)

def evaluation(config: SimulationConfig, bn: OpenBooleanNetwork) -> float:
    
    light_position, data = run_simulation(config, bn)

    new_score = aggregate_sim_data(light_position, data)

    __globals['it'] += 1

    if __globals['score'] < 0.0 or new_score < __globals['score']:

        __globals['score'] = new_score

        bnjson = bn.to_json()
        
        bnjson.update({'sim_info': dict()})
        bnjson['sim_info'].update({'eval_score':__globals['score']})
        # bnjson['sim_info'].update({'light_pos': light_position.to_json()})
        # bnjson['sim_info'].update({'agent_pos': agent_position.to_json()})
        # bnjson['sim_info'].update({'final_pos': agent_position.to_json()})
        # bnjson['sim_info'].update({'final_dist': abs(final_pos.dist(light_position))})
        bnjson['sim_info'].update({'n_it':__globals['it']})

        write_json(bnjson, config.bn_model_path / __globals['top_model_name'])

    return new_score

def run_simulation(config : SimulationConfig, bn: OpenBooleanNetwork) -> dict:

    model_fname = generate_file_name('bn_model', uniqueness_gen= lambda: '', ftype='json')
    data_fname = generate_file_name('sim_data', uniqueness_gen= lambda: '', ftype='json')
    log_fname = generate_file_name('sim_log', uniqueness_gen= lambda: '', ftype='json')
    config_fname = generate_file_name('sim_config', uniqueness_gen= lambda: '', ftype='json')

    # Create Sim Config based on the Experiment Config
    sim_config = SimulationConfig.from_json(config.to_json())
    
    sim_config.sim_light_position = r_point3d(
        O=config.sim_light_position, 
        R=config.sim_light_spawn_radius, 
        axis=Axis.Y, 
        quadrant=Quadrant.NPP
    )

    sim_config.sim_agent_position = r_point3d(
        O=config.sim_agent_position, 
        R=config.sim_agent_spawn_radius, 
        axis=Axis.Y, 
        quadrant=Quadrant.PPN
    )

    sim_config.sim_agent_y_rot = random.uniform(0, 2*math.pi) #

    sim_config.bn_model_path /= model_fname
    sim_config.sim_data_path /= data_fname
    sim_config.sim_log_path /= log_fname
    sim_config.sim_config_path /= config_fname

    # Save model (inside or outside of the config? mumble rumble)
    write_json(bn.to_json(), sim_config.bn_model_path)
    write_json(sim_config.to_json(), sim_config.sim_config_path, indent=True)

    # Run Webots
    cmd = [str(config.webots_path), *config.webots_launch_args, str(config.webots_world_path)]
    subprocess.run(cmd)
    
    data = read_json(sim_config.sim_data_path)

    return sim_config.sim_light_position, data

def aggregate_sim_data(light_position: Point3D, sim_data: dict) -> float:

    df = pandas.DataFrame(sim_data['data'])

    # df['aggr_light_values'] = df['light_values'].apply(lambda lvs: max(lvs.values()))

    # score = df['aggr_light_values'].sum(axis=0, skipna=True) 

    max_step = df['n_step'].max()

    final_pos = df[df['n_step'] == max_step]['position'].T.values[0]

    # return (1 / score if score > 0 else float('+inf'))
    return round(light_position.dist(final_pos), 5)

###############################################################################################

def search_bn_controller(config : SimulationConfig, bn: OpenBooleanNetwork):

    return parametric_vns(
        bn,
        evaluate=lambda bn: evaluation(config, bn),
        max_iters=config.sd_max_iters,
        max_stalls=config.sd_max_stalls,
        min_target=config.sd_minimization_target
    )