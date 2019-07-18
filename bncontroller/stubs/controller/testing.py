import itertools
from collections.abc import Iterable
from pandas import DataFrame
from bncontroller.stubs.controller.evaluation import test_evaluation
from bncontroller.file.utils import check_path, gen_fname, cpaths, get_simple_fname, FNAME_PATTERN
from bncontroller.jsonlib.utils import read_json
from bncontroller.collectionslib.utils import flat
from bncontroller.sim.data import generate_spawn_points, Point3D
from bncontroller.sim.config import SimulationConfig
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger

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

def generate_test_params(template, aggregator):
    return map( 
        lambda t: sort(
            flat(t, to=tuple, exclude=Point3D), 
            get_params_order(template.test_params_aggr_func)
        ),
        itertools.product(
            *aggregator(
                template.test_params_aggr_func,
                template.globals['light_spawn_points'],
                template.globals['agent_spawn_points'], 
                template.globals['agent_yrots']
            )
        )
    )


def test_bncontrollers(template:SimulationConfig, boolnets:dict):
    '''
    Test each BN in the collection on the same set of points.

    Return the collected evaluation data for each test.
    '''

    def aggregate(f, lp, ap, ar):
        return eval(f, dict(lp=lp, ap=ap, ar=ar))

    template.globals.update(
        **generate_spawn_points(template)
    )
    
    data = dict()

    for k in boolnets:
        
        logger.info(f"Boolean Network {k}")

        test_params = generate_test_params(template, aggregator=aggregate)

        data[k] = test_bncontroller(template, boolnets[k], test_params)
    
    return data

def test_bncontroller(template:SimulationConfig, bn:OpenBooleanNetwork, test_params: Iterable):
    '''
    Test a single bn on the given test points\parameters.

    Return the collected evaluation data
    '''
    test_data = DataFrame()

    sim_data = test_evaluation(template, bn, test_params)

    fscores, dscores, lpos, apos, yrot, *_ = sim_data

    test_data['score'] = fscores
    test_data['fdist'] = dscores
    test_data['lpos'] = lpos
    test_data['apos'] = apos
    test_data['yrot'] = yrot
    test_data['idist'] = list(a.dist(b) for a, b in zip(lpos, apos))

    return test_data