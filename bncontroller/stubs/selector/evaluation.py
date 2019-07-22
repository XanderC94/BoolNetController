import bncontroller.stubs.selector.tests as selector_tests
from bncontroller.sim.config import SimulationConfig
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.stubs.selector.utils import test_contraints

def step1_evaluation(template: SimulationConfig, bn: BoolNetSelector):
    
    tna = template.slct_target_n_attractors
    atpm = template.slct_target_transition_rho
    n_rho = template.slct_noise_rho

    return test_contraints(bn, [
            lambda o: selector_tests.test_attractors_number(o, tna),
            lambda o: selector_tests.test_attractors_transitions(o, atpm),
            lambda o: selector_tests.test_bn_state_space_omogeneity(o, n_rho)
        ])

def step2_evaluation(template: SimulationConfig, bn: BoolNetSelector):

    return selector_tests.test_attraction_basins(
        bn, fix_input_for=template.slct_fix_input_steps
    ) if bn is not None else False
