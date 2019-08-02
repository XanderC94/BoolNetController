import subprocess
from pathlib import Path

import bncontroller.stubs.utils as stub_utils
from bncontroller.file.utils import cpaths
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.sim.utils import GLOBALS
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.rtest import find_bn_type

if __name__ == "__main__":
    
    if isinstance(GLOBALS.bn_ctrl_model_path, list) or GLOBALS.bn_ctrl_model_path.is_dir():
        raise Exception('Model path should be a file.')
    
    GLOBALS.app['mode'] = 'handcheck'
    
    bn = find_bn_type(read_json(GLOBALS.bn_ctrl_model_path))
    
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
    try:
        proc_closure = stub_utils.run_simulation(config, bn)
    except Exception:
        pass
        
    stub_utils.clean_dir(f'./webots/controllers/{GLOBALS.webots_agent_controller}/tmp')

    exit(proc_closure.returncode)
