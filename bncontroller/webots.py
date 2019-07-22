import subprocess
from pathlib import Path

import bncontroller.stubs.utils as stub_utils
from bncontroller.file.utils import cpaths
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.config import SimulationConfig, generate_sim_config
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.boolnet.structures import OpenBooleanNetwork

if __name__ == "__main__":

    template = parse_args_to_config()
    
    if isinstance(template.bn_ctrl_model_path, list) or template.bn_ctrl_model_path.is_dir():
        raise Exception('Model path should be a file.')
   
    bn = OpenBooleanNetwork.from_json(read_json(template.bn_ctrl_model_path))

    config = generate_sim_config(template, keyword='handcheck')

    ### Generate simulation world file for training ################################

    stub_utils.generate_webots_worldfile(
        template.webots_world_path, 
        config.webots_world_path,
        stub_utils.ArenaParams(
            floor_size=(30, 30),
            controller_args=template.sim_config_path
        )
    )

    stub_utils.generate_webots_props_file(
        template.webots_world_path,
        config.webots_world_path
    )

    proc_closure = stub_utils.run_simulation(config, bn)

    exit(proc_closure.returncode)
