import random
from bncontroller.stubs.bn import bn_generator, is_obn_consistent
from bncontroller.type.utils import first
from bncontroller.boolnet.utils import binstate, compact_state, search_attractors
from bncontroller.boolnet.atm import AttractorsTransitionMatrix as ATM
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.boolnet.structures import OpenBooleanNetwork, BooleanNetwork

def generate_selector(template):

    bng, I, O, *_ = bn_generator(
        N=template.bn_n,
        K=template.bn_k,
        P=template.bn_p,
        I=template.bn_n_inputs,
        O=template.bn_n_outputs
    )

    bn = bng.new_selector(I, O)

    while not is_obn_consistent(bn.nodes, I, O):
        bn = bng.new_selector(I, O)
    
    return bn

def noisy_run(bn: OpenBooleanNetwork, steps:int, input_step=1):

    states = []
    __input_step = 0

    for i in range(steps):

        if input_step + __input_step == i:
            __input_step += input_step
            for k in bn.input_nodes:
                bn[k].state = random.choice([True, False])

        if random.choice([True, False, False, False, False]):
            
            pop = set(bn.keys) # .difference(bn.input_nodes)
            noisy_nodes = random.sample(
                pop, 
                random.choice([1, len(pop)])
            )
            
            for k in noisy_nodes:
                bn[k].state = random.choice([True, False])

        states.append(compact_state(bn.update()))

    return states

def is_attractor_space_omogeneous(bn: BooleanNetwork, atm: ATM, n_attractors: int):
    '''
    Checks whether the attractor space is:
        * Deaf to inputs values in presence of "ambient" noise.
            
            That is, setting an input node state to a certain value 
            doesn't lock the trajectory of the BN to a single attractor.

        * Displays, to some degree of alternance, all the attractors (see ATM).
    '''
    states = noisy_run(
        bn, 
        max(map(len, atm.attractors))*len(bn)*10, 
        input_step=max(map(len, atm.attractors)) * 2,
    )

    found_attrs = search_attractors(states, atm.dattractors)
    
    return len(set(found_attrs)) == n_attractors

def is_bnselector_consistent(bn: BoolNetSelector, atm: ATM, n_attractors:int, trans_biases:dict):
    '''
    Return True if:
        * the number of attractors expressed by the BN matches the number of wanted attractors

        * the transition probability from (some) attractors to others matches 
            the ones specified in the given threshold map.

        * the expressed attractor space is omogeneous. That is:
        
            - The BN is deaf to inputs values in presence of "ambient" noise.
            
                That is, setting an input node state to a certain value 
                doesn't lock the trajectory of the BN to a single attractor.

            - The BN display, to some degree of alternance, all the attractors.

    '''
    return (
        len(atm.attractors) == n_attractors 
        and all(
            atm.dtableau[ki][kj] >= trans_biases[ki][kj] 
            for ki in trans_biases
            for kj in trans_biases[ki]
        )
        and is_attractor_space_omogeneous(bn, atm, n_attractors) # True
    )