from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.bn import rbn_gen
from bncontroller.sim.config import SimulationConfig
from bncontroller.sim.data import Point3D, r_point3d, Axis, Quadrant
from bncontroller.boolnet.eval.search import incremental_stochastic_descent, parametric_vns
from bncontroller.json.utils import read_json, write_json
from bncontroller.file.utils import generate_file_name, iso8106
from pathlib import Path
import subprocess, pandas, math, random

dist = None

def evaluation(config: SimulationConfig, bn: OpenBooleanNetwork) -> float:

    light_position, data = run_simulation(config, bn)

    new_dist = aggregate_sim_data(light_position, data)

    if dist is None or new_dist < dist:
        write_json(bn.to_json(), config.bn_model_path / 'bn_model_top.json')

    return new_dist

def run_simulation(config : SimulationConfig, model: OpenBooleanNetwork) -> dict:

    date = iso8106()

    model_fname = generate_file_name('bn_model', uniqueness_gen= lambda: '', ftype='json')
    data_fname = generate_file_name('sim_data', uniqueness_gen= lambda: '', ftype='json')
    log_fname = generate_file_name('sim_log', uniqueness_gen= lambda: '', ftype='json')
    config_fname = generate_file_name('sim_config', uniqueness_gen= lambda: '', ftype='json')

    # Create Sim Config based on the Experiment Config
    sim_config = SimulationConfig.from_json(config.to_json())

    # sim_config.bn_inputs = model.input_nodes
    # sim_config.bn_outputs = model.output_nodes
    
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
    # sim_config.sim_agent_y_rot = math.pi # 

    sim_config.bn_model_path /= model_fname
    sim_config.sim_data_path /= data_fname
    sim_config.sim_log_path /= log_fname
    sim_config.sim_config_path /= config_fname

    # Save model (inside or outside of the config? mumble rumble)
    write_json(model.to_json(), sim_config.bn_model_path)
    write_json(sim_config.to_json(), sim_config.sim_config_path, indent=True)

    # Run Webots
    cmd = [str(config.webots_path), *config.webots_launch_args, str(config.webots_world_path)]
    subprocess.run(cmd)
        
    return (sim_config.sim_light_position, read_json(sim_config.sim_data_path))

def aggregate_sim_data(light_position: Point3D, sim_data: dict) -> float:

    df = pandas.DataFrame(sim_data['data'])

    # df['aggr_light_values'] = df['light_values'].apply(lambda lvs: sum(lvs))
    df['aggr_light_values'] = df['light_values'].apply(lambda lvs: max(lvs.values()))
    # df['aggr_light_values'] = df['light_values'].apply(lambda lvs: sum(lvs)/len(lvs))

    # total_sum = df['sum_light_values'].sum(axis=0, skipna=True) 

    key_max = df['n_step'].idxmax()

    last_value = df[
        df['n_step'] == key_max
    ]['aggr_light_values'].T.values[0]

    # df['dist'] = df['position'].apply(lambda p: sim_config.sim_light_position.dist(p))

    # nearest_step, nearest_value = df.iloc[
    #     df['dist'].idxmin()
    # ][['n_step','sum_light_values']].T.values

    # print(total_sum)
    # print(last_step, last_value)
    # print(nearest_step, nearest_value)
    # return round(math.sqrt(1 / last_value), 3) # Irradiance (E) is inverserly proportional to Squared Distance (d)
    return round(1 / last_value * 1000, 5) # Irradiance (E) is inverserly proportional to Squared Distance (d)

def stub_search(config : SimulationConfig, bn: OpenBooleanNetwork):

    return parametric_vns(
        bn,
        evaluate= lambda bn: evaluation(config, bn),
        max_iters= config.sd_max_iters,
        max_stalls= config.sd_max_stalls
    )