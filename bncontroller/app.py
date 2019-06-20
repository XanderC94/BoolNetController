
from bncontroller.stubs.bn import rbn_gen
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.evaluation import search_bn_controller
from bncontroller.sim.config import parse_args_to_config
from bncontroller.json.utils import read_json, write_json
from pathlib import Path
import argparse, time

#########################################################################################################

if __name__ == "__main__":
 
    config = parse_args_to_config()
    
    N = config.bn_n
    K = config.bn_k
    P = config.bn_p

    I = config.bn_inputs
    
    O = config.bn_outputs
    
    bn = None

    if config.bn_model_path.is_dir():
        bng, I, O, *_ = rbn_gen(N, K, P, I, O)
        bn = bng.new_obn(I, O)
    else: 
        bn = OpenBooleanNetwork.from_json(read_json(config.bn_model_path))
        config.bn_model_path = config.bn_model_path.parent

    t = time.perf_counter()

    search_bn_controller(config, bn)

    print(f"Search time: {time.perf_counter()-t}s")
    
    exit(1)