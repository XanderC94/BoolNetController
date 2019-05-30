
from bncontroller.custom.bn import experiment_rbng
from bncontroller.custom.evaluation import custom_search
from bncontroller.sim.config import SimulationConfig
from bncontroller.json_utils import read_json, write_json
from pathlib import Path
import argparse

#########################################################################################################

if __name__ == "__main__":
 
    parser = argparse.ArgumentParser('Run batch simulations.')

    parser.add_argument('config_path', type=Path)

    args = parser.parse_args()

    config = SimulationConfig(read_json(args.config_path))
    
    N = config.bn_n
    K = config.bn_k
    P = config.bn_p

    I = list(range(config.bn_inputs)) # list of input nodes labels
    O = list(range(config.bn_inputs, config.bn_outputs)) # list of output nodes label

    bng = experiment_rbng(N, K, P, I, O)

    # bn = bng.new()

    # write_json(bn.to_json(), config.bn_model_path / 'test_bn.json')

    custom_search(config, bng, I, O)
