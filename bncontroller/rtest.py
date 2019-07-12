import itertools
import re
from pathlib import Path
from collections import defaultdict
from collections.abc import Iterable
from pandas import DataFrame
import bncontroller.stubs.evaluation as evaluation
from bncontroller.file.utils import check_path, get_fname, cpaths
from bncontroller.jsonlib.utils import read_json
from bncontroller.collectionslib.utils import flat
from bncontroller.sim.data import generate_spawn_points, Point3D
from bncontroller.sim.config import SimulationConfig
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.plot.utils import get_simple_name, FNAME_PATTERN
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork

#########################################################################################################

MODEL_NAME_PATTERN = r'bn_(?:subopt_)?'+FNAME_PATTERN+'.json'

def sort(t:Iterable, go:dict, wo=dict(lp=0, ap=1, ar=2)):

    r = list(t)
    
    for gk, wk in dict((go[k], wo[k]) for k in wo).items():
        
        r[wk] = t[gk] 

    return r

def get_params_order(string:str, lp='lp', ap='ap', ar='ar'):

    lpi = string.find(lp)
    api = string.find(ap)
    ari = string.find(ar)

    ix = sorted([lpi, api, ari])

    return {
        lp: ix.index(lpi),
        ap: ix.index(api),
        ar: ix.index(ari),
    }

def collect_bn_models(
        paths:Iterable, 
        ffilter=lambda x: x.is_file() and re.match(MODEL_NAME_PATTERN, x.name)
    ):

    files = dict()
    bns = defaultdict(list)

    for path in paths:
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

    elif not check_path(template.test_data_path):
        raise Exception(
            'Test dataset path in template configuration file should be a directory.'
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

    files, bns = collect_bn_models(
        cpaths(template.bn_model_path)
    )

    ### Prepare aggregation function evaluator ####################################

    def aggregate(f, lp, ap, ar):
        return eval(f, dict(lp=lp, ap=ap, ar=ar))

    ### Test ######################################################################
    
    for i in range(template.test_n_instances):

        template.globals.update(
            **generate_spawn_points(template)
        )
        
        for k in bns:
            
            logger.info(i, k)

            test_data = DataFrame()

            test_params = map( 
                lambda t: sort(
                    flat(t, to=tuple, exclude=Point3D), 
                    get_params_order(template.test_params_aggr_func)
                ),
                itertools.product(
                    *aggregate(
                        template.test_params_aggr_func,
                        template.globals['light_spawn_points'],
                        template.globals['agent_spawn_points'], 
                        template.globals['agent_yrots']
                    )
                )
            )

            sim_data = evaluation.test_evaluation(template, bns[k], test_params)

            fscores, dscores, lpos, apos, yrot, *_ = sim_data

            test_data['score'] = fscores
            test_data['fdist'] = dscores
            test_data['lpos'] = lpos
            test_data['apos'] = apos
            test_data['yrot'] = yrot
            test_data['idist'] = list(a.dist(b) for a, b in zip(lpos, apos))

            test_data.to_json(
                template.test_data_path / get_fname(
                    'rtest_data', 
                    get_simple_name(files[k].name, FNAME_PATTERN),
                    template='{name}'+f'_in{i}.json',
                )
            )
