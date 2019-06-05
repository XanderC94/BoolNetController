
from bncontroller.stubs.bn import rbn_gen
from bncontroller.stubs.evaluation import stub_search
from bncontroller.sim.config import parse_args_to_config
from bncontroller.json.utils import read_json, write_json
from pathlib import Path
import argparse

#########################################################################################################

if __name__ == "__main__":
 
    config = parse_args_to_config()
    
    N = config.bn_n
    K = config.bn_k
    P = config.bn_p

    I = config.bn_inputs
    
    O = config.bn_outputs

    bng, I, O, *_ = rbn_gen(N, K, P, I, O)

    stub_search(config, bng, I, O)
