import subprocess
from pathlib import Path

import bncontroller.stubs.utils as stub_utils
from bncontroller.file.utils import cpaths
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.utils import GLOBALS
from bncontroller.boolnet.structures import OpenBooleanNetwork

if __name__ == "__main__":
    
    if isinstance(GLOBALS.bn_ctrl_model_path, list) or GLOBALS.bn_ctrl_model_path.is_dir():
        raise Exception('Model path should be a file.')
   
    bn = OpenBooleanNetwork.from_json(read_json(GLOBALS.bn_ctrl_model_path))

    GLOBALS.app['mode'] = 'handcheck'

    config = GLOBALS.generate_sim_config()

    ### Generate simulation world file for training ################################

    stub_utils.generate_webots_worldfile(
        GLOBALS.webots_world_path, 
        config.webots_world_path,
        config.arena_params
    )

    stub_utils.generate_webots_props_file(
        GLOBALS.webots_world_path,
        config.webots_world_path
    )

    proc_closure = stub_utils.run_simulation(config, bn)

    exit(proc_closure.returncode)
