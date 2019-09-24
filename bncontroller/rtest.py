import re
import time
from pathlib import Path
from collections import defaultdict
from collections.abc import Iterable

import bncontroller.filelib.utils as futils
from bncontroller.sim.config import Config
from bncontroller.sim.utils import GLOBALS, load_global_config
from bncontroller.jsonlib.utils import read_json, jsonrepr
from bncontroller.boolnet.structures import OpenBooleanNetwork, BooleanNetwork
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory

#########################################################################################################

MODEL_NAME_PATTERN = r'(?:behavioural_|selective_)?bn_(?:last_|subopt_|selector_|controller_)?' + futils.FNAME_PATTERN + '(?:.json)'

def find_bn_type(jsonrepr: dict):

    def go(jsonrepr: set):
        if 'attractors_input_map' in jsonrepr:
            return SelectiveBooleanNetwork
        elif 'inputs' in jsonrepr and 'outputs' in jsonrepr:
            return OpenBooleanNetwork
        else:
            return BooleanNetwork

    return go(jsonrepr.keys()).from_json(jsonrepr)

def collect_bn_models(
        paths: Iterable or Path,
        bn_deserializer=find_bn_type,
        ffilter=lambda x: x.is_file() and re.search(MODEL_NAME_PATTERN, x.name)
    ):

    files = dict()
    bns = defaultdict(list)

    for path in futils.cpaths(paths, recursive=3):
        # print(path.is_file(), re.search(MODEL_NAME_PATTERN, path.name))
        
        if path.is_dir():

            f, bn, *_ = collect_bn_models(
                path.iterdir(),
                bn_deserializer=bn_deserializer,
                ffilter=ffilter
            )

            bns.update(**bn)
            files.update(**f)

        elif ffilter(path):
            # print(path)
            name = path.with_suffix('').name
            bns[name] = bn_deserializer(read_json(path))
            files[name] = path
  
    return files, bns

###################################################################################

def check_config(config: Config):
    
    if config.webots_world_path.is_dir():
        raise Exception('Simulation world template should be a file not a dir.')

    elif not futils.check_path(config.test_data_path, create_if_dir=True):
        raise Exception(
            'Test dataset path in configuration file should be a directory.'
        )

if __name__ == "__main__":

    ### Load Configuration ########################################################

    load_global_config()

    check_config(GLOBALS)

    GLOBALS.app['mode'] = 'rtest'

    logger.instance = LoggerFactory.filelogger(
        futils.get_dir(
                GLOBALS.app_output_path, create_if_dir=True
            ) / '{key}_{date}.log'.format(
                key=GLOBALS.app['mode'],
                date=futils.FROZEN_DATE,
            )
    )

    ### Load Test Model(s) from Template paths ####################################

    files, bns = collect_bn_models(GLOBALS.bn_model_path)

    ### Test ######################################################################
    t = time.perf_counter()
    
    for i in range(GLOBALS.test_n_instances):

        logger.info(f'Test instance n°{i}')

        instance_data = GLOBALS.app_core_function(bns)

        for k, test_data in instance_data.items():

            name = futils.gen_fname( 
                futils.get_simple_fname(files[k].name, futils.FNAME_PATTERN, uniqueness=2),
                template='rtest_data_{name}' + f'_in{i}.json',
            )
            
            test_data.to_json(GLOBALS.test_data_path / name, default_handler=jsonrepr)

            logger.info(f'Test data saved into {str(GLOBALS.test_data_path / name)}')

    logger.info(f"Test time: {time.perf_counter() - t}s")

    logger.flush()
    
    exit(1)
