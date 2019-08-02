'''
Generate or load a BN and run Stochastic Descent Search Algorithm
'''
import time
from pathlib import Path

from bncontroller.boolnet.factory import generate_rbn
from bncontroller.stubs.controller.utils import template_controller_generator
from bncontroller.sim.config import Config
from bncontroller.sim.utils import GLOBALS
from bncontroller.sim.data import BNParams
from bncontroller.file.utils import check_path, get_dir, FROZEN_DATE
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory

####################################################################################

def generate_or_load_bn(params: BNParams, path: Path, save_virgin=False):

    __bn = None

    if check_path(path, create_if_dir=True):

        generator = template_controller_generator(*params)

        __bn = generate_rbn(generator.new_obn, force_consistency=True)

        if save_virgin:
            p = path / 'virgin_bn_{date}.json'.format(
                date=FROZEN_DATE
            )

            write_json(__bn.to_json(), p)

            logger.info(f'Virgin BN saved to {p}.')

    else:
        __bn = OpenBooleanNetwork.from_json(read_json(path))
        logger.info(f'BN loaded from {path}.')

    return __bn

def check_config(config: Config):

    if isinstance(config.bn_ctrl_model_path, list):
        raise Exception('Model path should be a dir or file')
    elif config.webots_world_path.is_dir():
        raise Exception('Simulation world GLOBALS should be a file not a dir.') 

####################################################################################

if __name__ == "__main__":

    ### Load Configuration #########################################################
    
    load_global_config()

    check_config(GLOBALS)

    GLOBALS.app['mode'] = (
        'generate' 
        if check_path(GLOBALS.bn_ctrl_model_path, create_if_dir=True) 
        else 'enhance' 
    )
    
    ### Init logger ################################################################
    
    logger.instance = LoggerFactory.filelogger(
        get_dir(GLOBALS.app_output_path, create_if_dir=True) / '{key}_{date}.log'.format(
            key=GLOBALS.app['mode'],
            date=FROZEN_DATE,
        )
    )

    ### BN Generation / Loading ####################################################

    bn = generate_or_load_bn(
        params=GLOBALS.bn_params,
        path=GLOBALS.bn_ctrl_model_path, 
        save_virgin=True
    )
    
    ### Launch search algorithm ##############################################

    if not GLOBALS.train_generate_only:
        
        t = time.perf_counter()

        bn, ctx = GLOBALS.app_core_function(bn)

        logger.info(f"Search time: {time.perf_counter() - t}s")
    
        logger.info(ctx)

        savepath = GLOBALS.bn_ctrl_model_path / '{mode}_ctrl_bn_{date}.json'.format(
            mode=GLOBALS.app['mode'],
            date=FROZEN_DATE
        )

        write_json(bn, savepath)

        logger.info(f'Output model saved to {savepath}.')
   
    logger.info('Closing...')

    logger.flush()

    exit(1)
