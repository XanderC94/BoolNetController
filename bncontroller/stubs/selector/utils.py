'''
'''
import random
from bncontroller.boolnet.utils import random_neighbors_generator
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.boolnet.boolean import r_bool
from bncontroller.boolnet.factory import RBNFactory

def template_selector_generator(
        N: int, K: int, P: float, Q: float, I: int, O: int,
        F=lambda n, o: random_neighbors_generator(n, o, self_loops=False)):
    
    _N = list(map(str, range(N)))
    _I = list(map(str, range(I))) 
    _O = list(map(str, range(I, I + O))) 
    _K = list(K for _ in _N)

    return RBNFactory(_N, _K, P, Q, _I, _O, F)

###################################################################################

def noisy_update(bn: OpenBooleanNetwork, steps: int, noise_rho: float):

    states = []
    # __input_step = 0

    for _ in range(steps):

        # if input_step + __input_step == i:
        #     __input_step += input_step
        #     for k in bn.input_nodes:
        #         bn[k].state = random.choice([True, False])

        if random.choices([True, False], [noise_rho, 1.0 - noise_rho])[0]:

            node = random.choice(bn.keys)

            bn[node].state = not bn[node].state

        states.append(bn.update())

    return states

##############################################################################

def test_contraints(obj: object, constraints_tests: list) -> bool:
    '''
    Sequentially checks constraints satisfaction tests on the given object.

    Test order is important, each test is applied if and only if
    the previous one was successful.

    Empty test list always hold success (True)

    '''

    # Recursive
    # if not constraints_tests:
    #     return True

    # return (
    #     test_contraints(obj, constraints_tests[1:]) 
    #     if constraints_tests[0](obj) 
    #     else False
    # )

    res = bool(constraints_tests)

    while constraints_tests and res:
        res = res and constraints_tests[0](obj)
        constraints_tests = constraints_tests[1:]

    return res