import math
import itertools
import numpy as np
from pandas import DataFrame
from collections import defaultdict
from bncontroller.json.utils import read_json, write_json
from bncontroller.file.utils import iso8106
from bncontroller.collections.utils import flat_tuple
from bncontroller.sim.config import parse_args_to_config
from bncontroller.sim.data import Point3D, r_point3d, Axis, Quadrant
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
import bncontroller.stubs.evaluation as evaluation

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

###########################################################################################################

if __name__ == "__main__":

    config = parse_args_to_config()

    def aggr(f, lp, ap, ar):

        return eval(f, dict(lp=lp, ap=ap, ar=ar))

    go = get_params_order(config.test_params_aggr_func)

    files = dict()
    bns = defaultdict(list)
    data = defaultdict(DataFrame)

    if config.bn_model_path.is_dir():
        
        for f in config.bn_model_path.iterdir():
            if f.is_file() and 'json' in f.suffix and 'rtest' not in f.name:
                
                name = f.with_suffix('').name
                bns[name] = OpenBooleanNetwork.from_json(read_json(f))
                files[name] = f

    else:
        f = config.bn_model_path
        config.bn_model_path = config.bn_model_path.parent

        name = f.with_suffix('').name
        bns[name] = OpenBooleanNetwork.from_json(read_json(f))
        files[name] = f

    for i in range(config.test_n_instances):

        config.fill_globals()

        for k in bns:
            print(i, k)

            _d = defaultdict(list)

            test_params = itertools.product(
                # zip(config.globals['agent_spawn_points'], config.globals['agent_yrots']), 
                # config.globals['light_spawn_points'],
                *aggr(
                    config.test_params_aggr_func,
                    config.globals['light_spawn_points'],
                    config.globals['agent_spawn_points'], 
                    config.globals['agent_yrots']
                )
            )

            for tp in test_params:
                
                lpos, apos, yrot, *_ = tsort(flat_tuple(tp), go) 
                
                sim_config = evaluation.generate_ad_hoc_sim_config(config, keyword=f'rtest')

                sim_config.sim_agent_yrot_rad = yrot
                sim_config.sim_agent_position = apos
                sim_config.sim_light_position = lpos

                evaluation.edit_webots_worldfile(sim_config)

                data = evaluation.run_simulation(sim_config, bns[k])
                new_score, rscore = evaluation.aggregate_sim_data(sim_config.sim_light_position, data)

                _d['scores'].append(new_score)
                _d['apos'].append(sim_config.sim_agent_position)
                _d['lpos'].append(sim_config.sim_light_position)
                _d['yrot'].append(sim_config.sim_agent_yrot_rad)
                _d['idist'].append(_d['apos'][-1].dist(_d['lpos'][-1]))
                _d['fdist'].append(rscore)

            df = DataFrame(_d)

            data[k] = df

            if not config.test_data_path.exists():
                config.test_data_path.mkdir()

            fname = files[k].with_suffix('').name
            df.to_json(config.test_data_path / f'rtest_data_{fname}_in{i}.json')
