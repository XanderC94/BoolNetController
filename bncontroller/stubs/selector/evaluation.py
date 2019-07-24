import bncontroller.stubs.selector.tests as selector_tests
from bncontroller.sim.config import Config
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.stubs.selector.utils import test_contraints

def step1_evaluation(bn: BoolNetSelector, tna: int, atpm: dict, n_rho: float):
    
    return test_contraints(bn, [
            lambda o: selector_tests.test_attractors_number(o, tna),
            lambda o: selector_tests.test_attractors_transitions(o, atpm),
            lambda o: selector_tests.test_bn_state_space_omogeneity(o, n_rho)
        ])

def step2_evaluation(bn: BoolNetSelector, fixed_input_steps: int):

    return selector_tests.test_attraction_basins(
        bn, fix_input_for=fixed_input_steps
    ) if bn is not None else False
