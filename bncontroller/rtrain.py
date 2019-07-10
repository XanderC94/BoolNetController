'''
Generate or load a BN and run Stochastic Descent Search Algorithm
'''
import time
import os
import math
import numpy as np
from pathlib import Path
from bncontroller.stubs.bn import rbn_gen, is_obn_consistent
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.evaluation import search_bn_controller 
from bncontroller.stubs.utils import generate_webots_worldfile
from bncontroller.sim.config import generate_ad_hoc_config, SimulationConfig
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.file.utils import check_path
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory

####################################################################################

def generate_or_load_bn(
        path: Path, 
        N:int, K:int, P:float, I:int, O:int, 
        date:str):
    
    bn = None

    check_path(path)

    if path.is_dir():
        bng, I, O, *_ = rbn_gen(N, K, P, I, O)
        bn = bng.new_obn(I, O)

        while not is_obn_consistent(bn.nodes, I, O):
            logger.info('Regenerating...')
            bn = bng.new_obn(I, O)

        logger.info('BN generated.')

        p = path / f'virgin_bn_{date}.json'

        write_json(bn.to_json(), p)

        logger.info(f'Virgin BN saved to {p}')

    else:
        bn = OpenBooleanNetwork.from_json(read_json(path))

        logger.info('BN loaded.')

    return bn

####################################################################################

if __name__ == "__main__":
 
    ### Load Configuration #########################################################

    template = parse_args_to_config()
    
    ### Init logger ################################################################
    
    logger.instance = LoggerFactory.filelogger(
        template.app_output_path / 'exp_{date}.log'.format(
            date=template.globals['date']
        )
    )

    ### BN Generation / Loading ####################################################

    bn = generate_or_load_bn(
        path=template.bn_model_path, 
        N=template.bn_n,
        K=template.bn_k,
        P=template.bn_p,
        I=template.bn_n_inputs,
        O=template.bn_n_outputs,
        date=template.globals['date']
    )
    
    ### Generate ad hoc configuration for training ################################
    
    config = generate_ad_hoc_config(template, keyword=f'rtrain')
    
    ### Generate simulation world file for training ################################

    generate_webots_worldfile(
        template.webots_world_path, 
        config.webots_world_path,
        config.sim_config_path
    )

    ### Launch search algorithm ##############################################

    if not config.train_generate_only:
        
        config.fill_globals()

        t = time.perf_counter()

        search_bn_controller(config, bn)

        logger.info(f"Search time: {time.perf_counter()-t}s")
   
    logger.info('Closing...')

    logger.flush()

    exit(1)
