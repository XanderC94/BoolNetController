'''
Testing utils for Boolean Network Selector constraints
'''
import itertools
import random
from collections import defaultdict
from multiprocessing import cpu_count
from bncontroller.boolnet.boolean import TRUTH_VALUES
from bncontroller.boolnet.utils import search_attractors, binstate
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.boolnet.structures import OpenBooleanNetwork, BooleanNetwork
from bncontroller.collectionslib.utils import first, flat
from bncontroller.stubs.selector.utils import noisy_update

NP = cpu_count()

def test_attractors_number(bn: BooleanNetwork, target_n_attractors: int):
    '''
    Check if the number of attractors expressed by the BN 
    matches the number of wanted attractors
    '''
    return len(bn.atm.attractors) == target_n_attractors

def test_attractors_transitions(bn: BooleanNetwork, at_taus: dict):
    '''
    Check if the transition probability from (some) attractors to another
    matches the ones specified in the given threshold map.
    '''

    return all(
        bn.atm.dtableau[i][j] > at_taus[i][j] 
        for i in at_taus
        for j in at_taus[i]
    )

def test_bn_state_space_omogeneity(bn: BooleanNetwork, i: int, noise_rho:float):
    '''
    Checks whether the attractor space is:
        * Deaf to inputs values in presence of "ambient" noise.

            That is, setting an input node state to a certain value 
            doesn't lock the trajectory of the BN to a single attractor.

        * Displays, to some degree of alternance, all the attractors (see ATM).
    '''
    states = noisy_update(bn, i, noise_rho)

    # print(f'Finding attractor in {len(states)} states')

    found_attrs = search_attractors(states, bn.atm.dattractors)

    return len(set(found_attrs)) == len(bn.atm.attractors)

def get_attraction_basin(bn: OpenBooleanNetwork, phi: int, bninput: dict):
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
    it = 0

    while not attractor_keys:

        if it < phi:
            it += 1
            for k in bn.input_nodes:
                bn[k].state = bninput[k]

        states.append(bn.update())
        
        # Search which attractors have developed in the run
        attractor_keys = search_attractors(states, bn.atm.dattractors)
        
    return attractor_keys

##############################################

def __test_state(params: tuple):
    
    bnjson, s, i, phi = params

    if 'bn' not in globals():
        global bn, virgin
        virgin = bnjson
        bn = SelectiveBooleanNetwork.from_json(bnjson)
    elif bnjson != virgin:
        virgin = bnjson
        bn = SelectiveBooleanNetwork.from_json(bnjson)
        
    for j, node in enumerate(bn.nodes):
        node.state = s[j]

    a = get_attraction_basin(bn, phi=phi, bninput=i)
  
    # Only one attractor shall appear for each input in absence of noise
    return binstate(i), a[0][0] if len(a) == 1 else None

def test_attraction_basins(bn: SelectiveBooleanNetwork, phi: int, executor=None):
    '''
    Test whether the given Boolean Network fixate itself
    on a specific attractor once a input value is settled
    '''
    
    inputs = map(
        lambda x: dict(zip(bn.input_nodes, x)),
        itertools.product(TRUTH_VALUES, repeat=len(bn.input_nodes))
    )

    states = itertools.product(TRUTH_VALUES, repeat=len(bn))
    
    params = itertools.product(states, inputs)

    attrs = dict()
    
    if executor is None or 2**len(bn) / NP < 2**5: #

        for s, i in params:
            # Set initial network state
            for j, node in enumerate(bn.nodes):
                node.state = s[j]

            a = get_attraction_basin(bn, phi=phi, bninput=i)

            # Only one attractor shall appear for each input in absence of noise
            if len(a) > 1 or binstate(i) in attrs and attrs[binstate(i)] != a[0][0]:
                return False
            elif binstate(i) not in attrs:
                attrs[binstate(i)] = a[0][0]

    else:   
        
        params = map(
            lambda x: (bn.to_json(), x[0], x[1], phi),
            params
        )

        for s, a in set(executor(__test_state, params)):

            if a is None or s in attrs and attrs[s] != a:
                return False
            elif s not in attrs:
                attrs[s] = a
    
    # An attractor should appear for at least 1 set of inputs
    # # that is, even if there are repeated keys, all key shall appears at least once
    return attrs if len(set(attrs.values())) == len(bn.atm.attractors) else False 

##############################################################################