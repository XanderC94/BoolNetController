from pathlib import Path
from pandas import DataFrame
from bncontroller.sim.utils import GLOBALS, load_global_config
from bncontroller.filelib.utils import get_dir, FROZEN_DATE
from bncontroller.stubs.selector.utils import template_selector_generator
from bncontroller.stubs.selector.generation import generate_consistent_bnselector as generate_consistent_bnselector

if __name__ == "__main__":

    load_global_config()

    N, K, P, I, O = GLOBALS.bn_n, GLOBALS.bn_k, GLOBALS.bn_p, GLOBALS.bn_n_inputs, GLOBALS.bn_n_outputs
        
    path = get_dir(Path(GLOBALS.bn_model_path), create_if_dir=True)
    
    for l in range(GLOBALS.sd_max_iters):

        bn = GLOBALS.app_core_function()

        Path(path / f'{l}_bn_n{N}_k{K}_p{int(P*100)}_{FROZEN_DATE}.ebnf').write_text(
            bn.to_ebnf()
        )

        Path(path / f'{l}_bn_n{N}_k{K}_p{int(P*100)}_{FROZEN_DATE}.json').write_text(
            bn.to_json()
        )

        df = DataFrame(bn.atm.dtableau)
        
        df.to_csv(str(path / f'{l}_atm_{FROZEN_DATE}.csv'))
    
    exit(1)


