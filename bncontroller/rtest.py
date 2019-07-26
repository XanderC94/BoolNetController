import re
import time
from pathlib import Path
from collections import defaultdict
from collections.abc import Iterable

import bncontroller.file.utils as futils
from bncontroller.sim.config import Config
from bncontroller.sim.utils import GLOBALS
from bncontroller.jsonlib.utils import read_json
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory

#########################################################################################################

MODEL_NAME_PATTERN = r'(?:(?:rtrain|renhance)?_?output_)?bn_(?:subopt_)?'+futils.FNAME_PATTERN+'.json'

def collect_bn_models(
        paths: Iterable or Path, 
        ffilter=lambda x: x.is_file() and re.search(MODEL_NAME_PATTERN, x.name)
    ):

    files = dict()
    bns = defaultdict(list)

    for path in futils.cpaths(paths):
        if path.is_dir():

            f, bn, *_ = collect_bn_models(
                path.iterdir(),
                ffilter=ffilter
            )

            bns.update(**bn)
            files.update(**f)

        elif ffilter(path):
            
            name = path.with_suffix('').name
            bns[name] = OpenBooleanNetwork.from_json(read_json(path))
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

    files, bns = collect_bn_models(GLOBALS.bn_ctrl_model_path)

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

            test_data.to_json(GLOBALS.test_data_path / name)

            logger.info(f'Test data saved into {str(GLOBALS.test_data_path / name)}')

    logger.info(f"Test time: {time.perf_counter() - t}s")

    logger.flush()
    
    exit(1)
