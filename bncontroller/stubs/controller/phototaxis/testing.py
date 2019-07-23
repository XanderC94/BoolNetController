import itertools
from collections.abc import Iterable
from pandas import DataFrame
from bncontroller.stubs.controller.phototaxis.evaluation import pt_evaluation_for_test
from bncontroller.jsonlib.utils import read_json
from bncontroller.collectionslib.utils import flat
from bncontroller.sim.data import generate_spawn_points, Point3D
from bncontroller.sim.config import SimulationConfig
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger

def generate_test_params(template):
    return map( 
        lambda t: flat(t, to=tuple, exclude=Point3D),
        itertools.product(
                template.globals['light_spawn_points'],
                zip(
                    template.globals['agent_spawn_points'],
                    template.globals['agent_yrots']
                )
            )
        )

def test_bncontrollers(template: SimulationConfig, bns: dict):
    '''
    Test each BN in the collection on the same set of points.

    Return the collected evaluation data for each test.
    '''

    template.globals.update(
        **generate_spawn_points(template)
    )
    
    data = dict()

    for k in bns:
        
        logger.info(f"Boolean Network {k}")

        test_params = generate_test_params(template)

        data[k] = test_bncontroller(template, bns[k], test_params)
    
    return data

def test_bncontroller(template: SimulationConfig, bn: OpenBooleanNetwork, test_params: Iterable):
    '''
    Test a single bn on the given test points\parameters.

    Return the collected evaluation data
    '''
    test_data = DataFrame()

    sim_data = pt_evaluation_for_test(template, bn, test_params)

    fscores, dscores, lpos, apos, yrot, *_ = sim_data

    test_data['score'] = fscores
    test_data['fdist'] = dscores
    test_data['lpos'] = lpos
    test_data['apos'] = apos
    test_data['yrot'] = yrot
    test_data['idist'] = list(a.dist(b) for a, b in zip(lpos, apos))

    return test_data