'''
Generate or load a BN and run Stochastic Descent Search Algorithm
'''
import time
import os
import math
import numpy as np
from bncontroller.stubs.bn import rbn_gen, is_obn_consistent
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.evaluation import search_bn_controller
from bncontroller.sim.config import parse_args_to_config
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.file.utils import check_path
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory

#########################################################################################################

if __name__ == "__main__":
 
    config = parse_args_to_config()

    config.fill_globals()

    date = config.globals['date']

    logger.instance = LoggerFactory.filelogger(config.app_output_path / f'exp_{date}.log')

    N = config.bn_n
    K = config.bn_k
    P = config.bn_p
    I = config.bn_n_inputs
    O = config.bn_n_outputs
    
    bn = None

    check_path(config.bn_model_path)
        
    if config.bn_model_path.is_dir():
        bng, I, O, *_ = rbn_gen(N, K, P, I, O)
        bn = bng.new_obn(I, O)

        while not is_obn_consistent(bn.nodes, I, O):
            logger.info('Regenerating...')
            bn = bng.new_obn(I, O)

        logger.info('BN generated.')

        p = config.bn_model_path / f'virgin_bn_{date}.json'

        write_json(bn.to_json(), p)

        logger.info(f'Virgin BN saved to {p}')

    else:
        bn = OpenBooleanNetwork.from_json(read_json(config.bn_model_path))
        config.bn_model_path = config.bn_model_path.parent

        logger.info('BN loaded.')

    if not config.train_generate_only:

        t = time.perf_counter()

        search_bn_controller(config, bn)

        logger.info(f"Search time: {time.perf_counter()-t}s")
    
    logger.info('Closing...')

    logger.flush()

    exit(1)
