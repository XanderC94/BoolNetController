import time
import itertools
from pandas import DataFrame
import bncontroller.stubs.selector.constraints as constraints
from bncontroller.filelib.utils import get_dir, FROZEN_DATE, cpaths
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.utils import GLOBALS, load_global_config

from bncontroller.stubs.selector.utils import template_selector_generator
from bncontroller.boolnet.selector import SelectiveBooleanNetwork

from multiprocessing import Pool, cpu_count

########################################################################### 
    
########################################################################### 

if __name__ == "__main__":
    
    load_global_config()

    NP = cpu_count()

    pool = Pool(processes=NP)
    
    mapper = lambda f, p: pool.imap_unordered(f, p, chunksize=2*NP)

    for path in cpaths(GLOBALS.bn_model_path, recursive=3):
        
        print(path)

        bnjson = read_json(path)
        
        bn = SelectiveBooleanNetwork.from_json(bnjson)
        # print(2**len(bn))
        # print(bnjson['gen_params'])
        
        i = max(map(len, bn.atm.attractors))*len(bn)*20

        t = time.perf_counter()
        
        if isinstance(GLOBALS.slct_target_transition_tau, list):
            tTau_map = {
                'a0': {'a1':max(GLOBALS.slct_target_transition_tau)},
                'a1': {'a0':max(GLOBALS.slct_target_transition_tau)}
            }
        else:
            tTau_map = GLOBALS.slct_target_transition_tau

        print(bn.atm.dtableau)

        c1 = constraints.test_attractors_number(bn, GLOBALS.slct_target_n_attractors)
        c2 = constraints.test_attractors_transitions(bn, tTau_map)
        c3 = constraints.test_bn_state_space_homogeneity(bn, i, GLOBALS.slct_noise_rho)
        print(time.perf_counter() - t)
        
        t = time.perf_counter()
        c4 = constraints.test_attraction_basins(bn, GLOBALS.slct_input_steps_phi, executor=mapper)
        print(time.perf_counter() - t)

        print(c1, c2, c3, bool(c4), end='\n\n')
    
    pool.close()
