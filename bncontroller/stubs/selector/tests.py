'''
Testing utils for Boolean Network Selector constraints
'''
import itertools
import random
from bncontroller.boolnet.boolean import TRUTH_VALUES
from bncontroller.boolnet.utils import search_attractors, binstate
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.boolnet.structures import OpenBooleanNetwork, BooleanNetwork
from bncontroller.type.utils import first
from bncontroller.stubs.selector.utils import noisy_update

def test_attractors_number(bn: BooleanNetwork, target_n_attractors: int):
    '''
    Check if the number of attractors expressed by the BN 
    matches the number of wanted attractors
    '''
    return len(bn.atm.attractors) == target_n_attractors

def test_attractors_transitions(bn: BooleanNetwork, at_threshold_map: dict):
    '''
    Check if the transition probability from (some) attractors to another
    matches the ones specified in the given threshold map.
    '''
    return all(
        bn.atm.dtableau[ki][kj] >= at_threshold_map[ki][kj] 
        for ki in at_threshold_map
        for kj in at_threshold_map[ki]
    )

def test_bn_state_space_omogeneity(bn: BooleanNetwork, noise_rho:float):
    '''
    Checks whether the attractor space is:
        * Deaf to inputs values in presence of "ambient" noise.

            That is, setting an input node state to a certain value 
            doesn't lock the trajectory of the BN to a single attractor.

        * Displays, to some degree of alternance, all the attractors (see ATM).
    '''
    states = noisy_update(
        bn,
        max(map(len, bn.atm.attractors))*len(bn)*20,
        noise_rho
        # input_step=max(map(len, atm.attractors)) * 2,
    )

    # print(f'Finding attractor in {len(states)} states')

    found_attrs = search_attractors(states, bn.atm.dattractors)

    return len(set(found_attrs)) == len(bn.atm.attractors)

def get_attraction_basin(bn: OpenBooleanNetwork, fix_input_for: int, bninput: dict):
    '''
    Search indefinitely for matching attractors for the given input values.
    and returns the first matching attractors found

    Input values can be fixed for a certain number of update step, 
    that is, they are superposed, not taking in consideration the value 
    given from the update procedure.
    After this lapse of steps they set free to use the state value 
    given by the update procedure.
    '''
    attractor_keys = list()
    states = []
    input_fixed_for = 0

    while not attractor_keys:

        if input_fixed_for < fix_input_for:
            # print('Fixing input...')
            for k in bn.input_nodes:
                bn[k].state = bninput[k]
            input_fixed_for += 1

        states.append(bn.update())

        # Search which attractractors have developed in the run
        attractor_keys = search_attractors(states, bn.atm.dattractors)

    return attractor_keys

def test_attraction_basins(bn: BoolNetSelector, fix_input_for: int):
    '''
    Test whether the given Boolean Network fixate itself
    on a specific attractor once a input value is settled
    '''
    inputs = map(
        lambda x: dict(zip(bn.input_nodes, x)),
        itertools.product(TRUTH_VALUES, repeat=len(bn.input_nodes))
    )

    for i in inputs:

        for node in bn.nodes:
            node.state = random.choice(TRUTH_VALUES)

        attrs = get_attraction_basin(bn, fix_input_for=fix_input_for, bninput=i)

        # Only one attractor shall appear for each input in absence of noise
        if len(attrs) == 1:
            bn.attractors_input_map.append((first(attrs), i))
        else:
            return False

    # An attractor should appear for at least 1 set of inputs
    # # that is, even if there are repeated keys, all key shall appears at least once
    return len(set(map(first, bn.attractors_input_map))) == len(bn.atm.attractors)

##############################################################################