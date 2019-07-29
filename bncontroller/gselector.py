import time

from bncontroller.sim.utils import GLOBALS
from bncontroller.file.utils import get_dir, FROZEN_DATE
from bncontroller.jsonlib.utils import write_json
from bncontroller.boolnet.atm import DEFAULT_ATM_WS_PATH
from bncontroller.stubs.selector.generation import generate_consistent_bnselector

########################################################################### 

if __name__ == "__main__":
   
    t = time.perf_counter()
    
    bn = generate_consistent_bnselector()
    
    print(time.perf_counter() - t, end='\n\n')
        
    print(bn.attractors_input_map)
    print(bn.atm.dtableau)
    print(bn.atm.dattractors)

    if not bn.attractors_input_map or None in bn.attractors_input_map:
        print('Failure.')
    else:
        path = get_dir(GLOBALS.bn_slct_model_path, create_if_dir=True) / 'bn_selector_{date}.json'.format(
            date=FROZEN_DATE
        )
        write_json(bn, path, indent=True)
        print(f'BN Selector saved in {path}.')
    
    DEFAULT_ATM_WS_PATH.unlink()

    exit(1)


