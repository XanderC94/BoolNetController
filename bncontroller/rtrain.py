'''
Generate or load a BN and run Stochastic Descent Search Algorithm
'''
import time
from pathlib import Path

from bncontroller.stubs.controller.training import train_bncontroller
from bncontroller.stubs.bn import generate_bncontroller
from bncontroller.sim.config import SimulationConfig
from bncontroller.file.utils import check_path
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory
from bncontroller.boolnet.structures import OpenBooleanNetwork

####################################################################################

def generate_or_load_bn(template: SimulationConfig, save_virgin=False):
    
    path=template.bn_ctrl_model_path

    __bn = None

    if check_path(path, create_if_dir=True):
        __bn = generate_bncontroller(template)

        if save_virgin:
            p = path / 'virgin_bn_{date}.json'.format(
                date=template.globals['date']
            )

            write_json(__bn.to_json(), p)

            logger.info(f'Virgin BN saved to {p}.')

    else:
        __bn = OpenBooleanNetwork.from_json(read_json(path))
        logger.info(f'BN loaded from {path}.')

    return __bn

def check_config(config:SimulationConfig):

    if isinstance(config.bn_ctrl_model_path, list):
        raise Exception('Model path should be a dir or file')
    elif config.webots_world_path.is_dir():
        raise Exception('Simulation world template should be a file not a dir.') 

####################################################################################

if __name__ == "__main__":

    ### Load Configuration #########################################################

    template = parse_args_to_config()

    check_config(template)

    template.globals['mode'] = (
        'rtrain' 
        if check_path(template.bn_ctrl_model_path, create_if_dir=True) 
        else 'renhance' 
    )
    ### Init logger ################################################################
    
    logger.instance = LoggerFactory.filelogger(
        template.app_output_path / '{key}_{date}.log'.format(
            key=template.globals['mode'],
            date=template.globals['date'],
        )
    )

    ### BN Generation / Loading ####################################################

    bn = generate_or_load_bn(template, save_virgin=True)
    
    ### Launch search algorithm ##############################################

    if not template.train_generate_only:
        
        t = time.perf_counter()

        bn, ctx = train_bncontroller(template, bn)

        logger.info(f"Search time: {time.perf_counter() - t}s")
    
        logger.info(ctx)

        savepath = template.bn_ctrl_model_path / '{mode}_output_bn_{date}.json'.format(
            mode=template.globals['mode'],
            date=template.globals['date']
        )

        write_json(bn, savepath)

        logger.info(f'Output model saved to {savepath}.')
   
    logger.info('Closing...')

    logger.flush()

    exit(1)
