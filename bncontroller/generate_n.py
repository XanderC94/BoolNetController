from pathlib import Path
from pandas import DataFrame
from bncontroller.sim.utils import GLOBALS
from bncontroller.file.utils import get_dir, FROZEN_DATE
from bncontroller.stubs.selector.utils import template_selector_generator
from bncontroller.stubs.selector.generation import generate_consistent_bnselector as generate_consistent_bnselector

if __name__ == "__main__":

    N, K, P, I, O = GLOBALS.bn_n, GLOBALS.bn_k, GLOBALS.bn_p, GLOBALS.bn_n_inputs, GLOBALS.bn_n_outputs
        
    path = get_dir(Path('./tmp/thousand_bns/'), create_if_dir=True)
    
    for l in range(GLOBALS.sd_max_iters):

        bn = GLOBALS.app_core_function()

        Path(path / f'{l}_bn_n{N}_k{K}_p{int(P*100)}_{FROZEN_DATE}.ebnf').write_text(
            bn.to_ebnf()
        )

        df = DataFrame(bn.atm.dtableau)
        
        df.to_csv(str(path / f'{l}_atm_{FROZEN_DATE}.csv'))
    
    exit(1)


