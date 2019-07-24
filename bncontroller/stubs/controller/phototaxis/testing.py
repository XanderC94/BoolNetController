import itertools
from pandas import DataFrame
from collections.abc import Iterable
from bncontroller.collectionslib.utils import flat
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.data import Point3D
from bncontroller.sim.utils import GLOBALS
from bncontroller.sim.logging.logger import staticlogger as logger
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.stubs.controller.phototaxis.evaluation import pt_evaluation_for_test

def generate_test_params(spawn_points: dict):
    return map( 
        lambda t: flat(t, to=tuple, exclude=Point3D),
        itertools.product(
                spawn_points['light_spawn_points'],
                zip(
                    spawn_points['agent_spawn_points'],
                    spawn_points['agent_yrots']
                )
            )
        )

def test_bncontrollers(bns: dict):
    '''
    Test each BN in the collection on the same set of points.

    Return the collected evaluation data for each test.
    '''

    spawn_points = GLOBALS.generate_spawn_points()
    
    data = dict()

    for k in bns:
        
        logger.info(f"Boolean Network {k}")

        test_params = generate_test_params(spawn_points)

        data[k] = test_bncontroller(bns[k], test_params)
    
    return data

def test_bncontroller(bn: OpenBooleanNetwork, test_params: Iterable):
    '''
    Test a single bn on the given test points\parameters.

    Return the collected evaluation data
    '''
    test_data = DataFrame()

    sim_data = pt_evaluation_for_test(bn, test_params)

    fscores, dscores, lpos, apos, yrot, *_ = sim_data

    test_data['score'] = fscores
    test_data['fdist'] = dscores
    test_data['lpos'] = lpos
    test_data['apos'] = apos
    test_data['yrot'] = yrot
    test_data['idist'] = list(a.dist(b) for a, b in zip(lpos, apos))

    return test_data