import os
import math
import itertools
import numpy as np
import bncontroller.stubs.evaluation as evaluation
from pathlib import Path
from pandas import DataFrame
from collections import defaultdict
from bncontroller.file.utils import iso8106, check_path, get_fname
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.collectionslib.utils import flat_tuple
from bncontroller.sim.data import generate_spawn_points
# from bncontroller.sim.config import generate_sim_config
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory
from bncontroller.parse.utils import parse_args_to_config
# from bncontroller.stubs.utils import generate_webots_worldfile
from bncontroller.plot.utils import get_simple_name, fname_pattern
# from bncontroller.plot.testdata import pattern
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork

#########################################################################################################

def tsort(t:tuple, go:dict, wo:dict = dict(lp=0, ap=1, ar=2)):

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

def collect_bn_models(path:Path, 
    ffilter=lambda f: f.is_file() and 'json' in f.suffix and 'rtest' not in f.name):
    
    files = dict()
    bns = defaultdict(list)

    if path.is_dir():
        
        for f in template.bn_model_path.iterdir():
            if ffilter(f):
                name = f.with_suffix('').name
                bns[name] = OpenBooleanNetwork.from_json(read_json(f))
                files[name] = f

    else:
        name = path.with_suffix('').name
        bns[name] = OpenBooleanNetwork.from_json(read_json(path))
        files[name] = path
    
    return files, bns

###################################################################################

if __name__ == "__main__":

    ### Load Configuration ########################################################

    template = parse_args_to_config()

    template.globals['mode'] = 'rtest'

    if not check_path(template.test_data_path):
        raise Exception(
            'Test dataset path in template configuration file should be a directory.'
        )
    
    logger.instance = LoggerFactory.filelogger(
        template.app_output_path / '{key}_{date}.log'.format(
            key=template.globals['mode']
            date=template.globals['date'],
        )
    )

    ### Load Test Model(s) from Template paths ####################################

    files, bns = collect_bn_models(template.bn_model_path)

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

            test_params = list(map( 
                lambda t: tsort(
                    flat_tuple(t), 
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
            ))

            fscores, dscores = evaluation.test_evaluation(template, bns[k], test_params)

            lpos, apos, yrot = tuple(list(t) for t in zip(*test_params))

            test_data['score'] = fscores
            test_data['fdist'] = dscores
            test_data['lpos'] = lpos
            test_data['apos'] = apos
            test_data['yrot'] = yrot
            test_data['idist'] = list(a.dist(b) for a, b in zip(lpos, apos))

            test_data.to_json(
                template.test_data_path / get_fname(
                    'rtest_data', 
                    get_simple_name(files[k].name, fname_pattern),
                    template='{name}'+f'_in{i}.json',
                )
            )
