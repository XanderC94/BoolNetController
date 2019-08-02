import time
import itertools
from pandas import DataFrame
import bncontroller.stubs.selector.constraints as constraints
from bncontroller.file.utils import get_dir, FROZEN_DATE, cpaths
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.utils import GLOBALS

from bncontroller.stubs.selector.utils import template_selector_generator
from bncontroller.boolnet.selector import SelectiveBooleanNetwork

########################################################################### 

if __name__ == "__main__":
    
    for path in cpaths(GLOBALS.bn_ctrl_model_path):
        
        print(path)
        bnjson = read_json(path)
        
        bn = SelectiveBooleanNetwork.from_json(bnjson)
        # print(2**len(bn))
        # print(bnjson['gen_params'])
        
        t = time.perf_counter()
        c1 = constraints.test_attractors_number(bn, GLOBALS.slct_target_n_attractors)
        c2 = constraints.test_attractors_transitions(bn, GLOBALS.slct_target_transition_rho)
        c3 = constraints.test_bn_state_space_omogeneity(bn, GLOBALS.slct_noise_rho)
        print(time.perf_counter() - t)
        
        t = time.perf_counter()
        c4 = constraints.test_attraction_basins(bn, GLOBALS.slct_fix_input_steps)
        print(time.perf_counter() - t)

        print(c1, c2, c3, bool(c4), end='\n\n')
            
