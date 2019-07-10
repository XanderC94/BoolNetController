import os
import math
import itertools
import numpy as np
import bncontroller.stubs.evaluation as evaluation
from pathlib import Path
from pandas import DataFrame
from collections import defaultdict
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.file.utils import iso8106, check_path
from bncontroller.collectionslib.utils import flat_tuple
from bncontroller.sim.config import generate_ad_hoc_config
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.sim.data import Point3D, r_point3d, Axis, Quadrant
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.stubs.utils import generate_webots_worldfile

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

    ### Load Test Model(s) from Template paths ##########################################################

    files, bns = collect_bn_models(template.bn_model_path)
    
    ### Generate ad hoc configuration for testing #################################

    config = generate_ad_hoc_config(template, keyword=f'rtest')
    
    ### Generate simulation world file for testing ################################

    generate_webots_worldfile(
        template.webots_world_path, 
        config.webots_world_path,
        config.sim_config_path
    )

    ### Test ######################################################################

    def aggr(f, lp, ap, ar):
        return eval(f, dict(lp=lp, ap=ap, ar=ar))

    go = get_params_order(config.test_params_aggr_func)

    if check_path(template.test_data_path) == 1:
        raise Exception('Test Data Path should be a directory.')
    
    for k in bns:
            
        for i in range(config.test_n_instances):

            config.fill_globals()

            print(i, k)

            test_data = defaultdict(list)

            test_params = itertools.product(
                *aggr(
                    config.test_params_aggr_func,
                    config.globals['light_spawn_points'],
                    config.globals['agent_spawn_points'], 
                    config.globals['agent_yrots']
                )
            )

            for tp in test_params:
                
                lpos, apos, yrot, *_ = tsort(flat_tuple(tp), go)
                
                config.sim_agent_yrot_rad = yrot
                config.sim_agent_position = apos
                config.sim_light_position = lpos
                  
                sim_data = evaluation.run_simulation(config, bns[k])
                new_score, rscore = evaluation.aggregate_sim_data(config.sim_light_position, sim_data)

                test_data['scores'].append(new_score)
                test_data['apos'].append(apos)
                test_data['lpos'].append(lpos)
                test_data['yrot'].append(yrot)
                test_data['idist'].append(apos.dist(lpos))
                test_data['fdist'].append(rscore)

            fname = files[k].with_suffix('').name
            DataFrame(test_data).to_json(config.test_data_path / f'rtest_data_{fname}_in{i}.json')

