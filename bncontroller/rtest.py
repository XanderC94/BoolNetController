import re
from pathlib import Path
from collections import defaultdict
from collections.abc import Iterable
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.config import SimulationConfig
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory
from bncontroller.file.utils import check_path, get_dir, gen_fname, cpaths, get_simple_fname, FNAME_PATTERN

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

if __name__ == "__main__":

    ### Load Configuration ########################################################

    template = parse_args_to_config()

    check_config(template)

    template.globals['mode'] = 'rtest'

    logger.instance = LoggerFactory.filelogger(
        get_dir(template.app_output_path, create_if_dir=True) / '{key}_{date}.log'.format(
            key=template.globals['mode'],
            date=template.globals['date'],
        )
    )

    ### Load Test Model(s) from Template paths ####################################

    files, bns = collect_bn_models(template.bn_ctrl_model_path)

    ### Test ######################################################################
    
    for i in range(template.test_n_instances):

        logger.info(f'Test instance n°{i}')

        instance_data = template.app_core_function(template, bns)

        for k, test_data in instance_data.items():

            name = gen_fname( 
                get_simple_fname(files[k].name, FNAME_PATTERN, uniqueness=2),
                template='rtest_data_{name}' + f'_in{i}.json',
            )

            test_data.to_json(template.test_data_path / name)

            logger.info(f'Test data saved into {str(template.test_data_path / name)}')

    exit(1)
