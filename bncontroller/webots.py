from bncontroller.parse.utils import parse_args_to_config
from bncontroller.sim.config import SimulationConfig
import subprocess
from pathlib import Path

def is_runnable_config(config: SimulationConfig):
    
    return (
        config.bn_model_path.is_file()
        and config.sim_data_path.suffix != str()
        and config.sim_log_path.suffix != str()
        and config.sim_config_path.suffix != str()
    )

if __name__ == "__main__":

    config = parse_args_to_config()

    if not is_runnable_config(config):
        raise Exception('Given config is not usable by the simulation, try complete sim_<path>s with a file.')
    
    excode = subprocess.run([
        str(config.webots_path), 
        *config.webots_launch_opts, 
        str(config.webots_world_path)
    ])

    exit(excode.returncode)