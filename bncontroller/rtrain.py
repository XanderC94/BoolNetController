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
from bncontroller.sim.config import SimulationConfig
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.file.utils import check_path
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory
from bncontroller.sim.data import generate_spawn_points

####################################################################################

def generate_or_load_bn(
        path: Path, 
        N:int, K:int, P:float, I:int, O:int, 
        date:str):
    
    bn = None

    if check_path(path):
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

    template.globals['mode'] = 'rtrain'
    
    ### Init logger ################################################################
    
    logger.instance = LoggerFactory.filelogger(
        template.app_output_path / '{key}_{date}.log'.format(
            key=template.globals['mode'],
            date=template.globals['date'],
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
    
    ### Launch search algorithm ##############################################

    if not template.train_generate_only:
        
        template.globals.update(
            **generate_spawn_points(template)
        )

        t = time.perf_counter()

        search_bn_controller(template, bn)

        logger.info(f"Search time: {time.perf_counter()-t}s")
   
    logger.info('Closing...')

    logger.flush()

    exit(1)
