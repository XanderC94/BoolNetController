from bncontroller.boolnet.bnstructures import BooleanNetwork
from bncontroller.custom.bn import experiment_rbng
from bncontroller.sim.config import SimulationConfig
from bncontroller.sim.data import Point3D
from bncontroller.boolnet.eval.parametric import parametric_vns, default_scramble_strategy
from bncontroller.json_utils import read_json, write_json
from bncontroller.utils import generate_file_name, iso8106
from pathlib import Path
import subprocess, datetime, argparse, copy, pandas, math, random

def evaluation(config: SimulationConfig, bn: BooleanNetwork, input_nodes: list, output_nodes: list) -> float:

    sim, data = run_simulation(config, bn, input_nodes, output_nodes)

    return aggregate_sim_data(sim, data)

def run_simulation(config : SimulationConfig, model: BooleanNetwork, input_nodes: list, output_nodes: list) -> dict:

    date = iso8106()

    model_fname = generate_file_name('bn_model', f'n{config.bn_n}', f'k{config.bn_k}', f'p{config.bn_p}', uniqueness_gen= lambda: date)
    data_fname = generate_file_name('sim_data', uniqueness_gen= lambda: date)
    log_fname = generate_file_name('sim_log', uniqueness_gen= lambda: date)
    # Create Sim Config based on the Experiment Config
    sim_config = SimulationConfig.from_json(config.to_json())

    sim_config.bn_inputs = input_nodes
    sim_config.bn_outputs = output_nodes
    sim_config.bn_model_path /= f'{model_fname}.json'
    sim_config.sim_data_path /= f'{data_fname}.json'
    sim_config.sim_log_path /= f'{log_fname}.json'

    # Save model (inside or outside of the config? mumble rumble)
    write_json(model.to_json(), sim_config.bn_model_path)
    write_json(sim_config.to_json(), sim_config.sim_config_path)

    # Run Webots
    subprocess.run(
        [str(config.webots_path), *config.webots_launch_args, str(config.webots_world_path)]
    )
        
    return (sim_config, read_json(sim_config.sim_data_path))

def aggregate_sim_data(sim_config: SimulationConfig, sim_data: dict) -> float:

    df = pandas.DataFrame(sim_data['data'])

    df['sum_light_values'] = df['light_values'].apply(lambda lvs: sum(lvs))
    # df['max_light_values'] = df['light_values'].apply(lambda lvs: max(lvs))

    # total_sum = df['sum_light_values'].sum(axis=0, skipna=True) 

    last_step, last_value = df.iloc[
        df['n_step'].idxmax()
    ][['n_step','sum_light_values']].T.values

    # df['dist'] = df['position'].apply(lambda p: sim_config.sim_light_position.dist(p))

    # nearest_step, nearest_value = df.iloc[
    #     df['dist'].idxmin()
    # ][['n_step','sum_light_values']].T.values

    # print(total_sum)
    # print(last_step, last_value)
    # print(nearest_step, nearest_value)

    return 1 / last_value # Irradiance (E) is inverserly proportional to Squared Distance (d)

def custom_search(config, bng, I, O):
    return parametric_vns(
        bng,
        evaluation_strategy= lambda bn: evaluation(config, bn, I, O),
        scramble_strategy= lambda bn, n_flips, last_flips: default_scramble_strategy(bn, n_flips, last_flips + I),
        max_iters= 100,
        max_stalls= -1
    )