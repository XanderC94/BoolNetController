import time
import itertools
from pathlib import Path
from bncontroller.sim.utils import GLOBALS
from bncontroller.file.utils import get_dir, iso8106
from bncontroller.jsonlib.utils import write_json
from bncontroller.boolnet.atm import DEFAULT_ATM_WS_PATH
from bncontroller.stubs.selector.generation import generate_consistent_bnselector

########################################################################### 

if __name__ == "__main__":
    
    toiter = lambda x: x if isinstance(x, (list, tuple)) else list([x])

    Ns, Ks, Ps, Qs, Is, Os = tuple(map(toiter, GLOBALS.bn_params))

    tRhos = toiter(GLOBALS.slct_target_transition_rho)
    
    params = itertools.product(Ns, Ks, Ps, Qs, Is, Os, tRhos)

    FOLDER = get_dir(GLOBALS.bn_slct_model_path, create_if_dir=True)
    
    for N, K, P, Q, I, O, tRho in params:

        GLOBALS.bn_n, GLOBALS.bn_k, GLOBALS.bn_p, GLOBALS.bn_q, GLOBALS.bn_n_inputs, GLOBALS.bn_n_outputs = N, K, P, Q, I, O
        if not isinstance(tRho, dict):
            GLOBALS.slct_target_transition_rho = {
                "a0": {"a0": tRho, "a1": tRho},
                "a1": {"a0": tRho, "a1": tRho}
            }
        
        t = time.perf_counter()
        bn = GLOBALS.app_core_function()
        print(time.perf_counter() - t, end='\n\n')

        while bn is None or not bn.attractors_input_map or None in bn.attractors_input_map:
            print('Failure. Retrying...')
            t = time.perf_counter()
            bn = GLOBALS.app_core_function()
            print(time.perf_counter() - t, end='\n\n')

        print(bn.attractors_input_map)
        print(bn.atm.dtableau)
        print(bn.atm.dattractors)

        path = FOLDER / f'bn_selector_{iso8106()}.json'

        write_json(bn, path, indent=True)

        print(f'BN Selector saved in {path}.')

    
    DEFAULT_ATM_WS_PATH.unlink()
    
    exit(1)


