from bncontroller.stubs.bn import rbn_gen, is_obn_consistent
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.evaluation import search_bn_controller
from bncontroller.sim.config import parse_args_to_config
from bncontroller.json.utils import read_json, write_json
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory
from pathlib import Path
import time
from bncontroller.stubs.globals import app_globals as __globals

#########################################################################################################

if __name__ == "__main__":
 
    config = parse_args_to_config()
    
    date = __globals['date']

    logger.instance = LoggerFactory.filelogger(config.app_output_path / f'exp_{date}.log')

    N = config.bn_n
    K = config.bn_k
    P = config.bn_p
    I = config.bn_inputs
    O = config.bn_outputs
    
    bn = None

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

        if config.train_generate_only:
            exit(1)

    else: 
        bn = OpenBooleanNetwork.from_json(read_json(config.bn_model_path))
        config.bn_model_path = config.bn_model_path.parent

        logger.info('BN loaded.')

    t = time.perf_counter()

    search_bn_controller(config, bn)

    logger.info(f"Search time: {time.perf_counter()-t}s")
    
    logger.flush()

    exit(1)