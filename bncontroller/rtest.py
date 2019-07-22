import re
from pathlib import Path
from collections import defaultdict
from collections.abc import Iterable
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.config import SimulationConfig
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.stubs.controller.testing import test_bncontrollers
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory
from bncontroller.file.utils import check_path, gen_fname, cpaths, get_simple_fname, FNAME_PATTERN

#########################################################################################################

MODEL_NAME_PATTERN = r'(?:(?:rtrain|renhance)?_?output_)?bn_(?:subopt_)?'+FNAME_PATTERN+'.json'

def collect_bn_models(
        paths: Iterable or Path, 
        ffilter=lambda x: x.is_file() and re.search(MODEL_NAME_PATTERN, x.name)
    ):

    files = dict()
    bns = defaultdict(list)

    for path in cpaths(paths):
        if path.is_dir():

            f, bn, *_ = collect_bn_models(
                path.iterdir(),
                ffilter=ffilter
            )

            bns.update(**bn)
            files.update(**f)

        elif ffilter(path):
            print(path)
            name = path.with_suffix('').name
            bns[name] = OpenBooleanNetwork.from_json(read_json(path))
            files[name] = path
  
    return files, bns

###################################################################################

def check_config(config:SimulationConfig):

    if config.webots_world_path.is_dir():
        raise Exception('Simulation world template should be a file not a dir.')

    elif not check_path(template.test_data_path, create_if_dir=True):
        raise Exception(
            'Test dataset path in template configuration file should be a directory.'
        )

    if not all(p in config.test_params_aggr_func for p in ('lp', 'ar', 'ap')):
        raise Exception(
            '''
            Aggregation function params must be named 
            lp: light_points, ap: agent_points and ar: agent rotation
            '''
        )

if __name__ == "__main__":

    ### Load Configuration ########################################################

    template = parse_args_to_config()

    check_config(template)

    template.globals['mode'] = 'rtest'

    logger.instance = LoggerFactory.filelogger(
        template.app_output_path / '{key}_{date}.log'.format(
            key=template.globals['mode'],
            date=template.globals['date'],
        )
    )

    ### Load Test Model(s) from Template paths ####################################

    files, bns = collect_bn_models(template.bn_ctrl_model_path)

    ### Test ######################################################################
    
    for i in range(template.test_n_instances):

        logger.info(f'Test instance n°{i}')

        instance_data = test_bncontrollers(template, bns)

        for k, test_data in instance_data.items():
            test_data.to_json(
                template.test_data_path / gen_fname(
                    'rtest_data', 
                    get_simple_fname(files[k].name, FNAME_PATTERN, uniqueness=2),
                    template='{name}'+f'_in{i}.json',
                )
            )

    exit(1)
