import bncontroller.stubs.selector.constraints as constraints
from bncontroller.sim.config import Config
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.stubs.selector.utils import test_contraints

def step1_evaluation(bn: SelectiveBooleanNetwork, na: int, ataus: dict, nrho: float):
    
    i = max(map(len, bn.atm.attractors))*len(bn)*20

    return test_contraints(bn, [
            lambda o: constraints.test_attractors_number(o, na),
            lambda o: constraints.test_attractors_transitions(o, ataus),
            lambda o: constraints.test_bn_state_space_homogeneity(o, i, nrho)
        ])

def step2_evaluation(bn: SelectiveBooleanNetwork, phi: int, executor=None):

    if bn is not None:
        c4 = constraints.test_attraction_basins(
            bn, phi=phi, executor=executor
        )
        if c4:
            bn.attractors_input_map = c4
            return True

    return False
