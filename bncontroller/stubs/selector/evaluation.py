import bncontroller.stubs.selector.constraints as constraints
from bncontroller.sim.config import Config
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.stubs.selector.utils import test_contraints

def step1_evaluation(bn: SelectiveBooleanNetwork, tna: int, atpm: dict, n_rho: float):
    
    return test_contraints(bn, [
            lambda o: constraints.test_attractors_number(o, tna),
            lambda o: constraints.test_attractors_transitions(o, atpm),
            lambda o: constraints.test_bn_state_space_omogeneity(o, n_rho)
        ])

def step2_evaluation(bn: SelectiveBooleanNetwork, fixed_input_steps: int, executor=None):

    if bn is not None:
        c4 = constraints.test_attraction_basins(
            bn, fix_input_for=fixed_input_steps, executor=executor
        )
        if c4:
            bn.attractors_input_map = c4
            return True

    return False
