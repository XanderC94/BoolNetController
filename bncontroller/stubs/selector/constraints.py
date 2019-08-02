'''
Testing utils for Boolean Network Selector constraints
'''
import itertools
import random
import time
from multiprocessing import Manager, Pool, cpu_count
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

def test_attractors_transitions(bn: BooleanNetwork, at_threshold_map: dict):
    '''
    Check if the transition probability from (some) attractors to another
    matches the ones specified in the given threshold map.
    '''

    # print(at_threshold_map)

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
    it = 0

    while not attractor_keys:

        if input_fixed_for < fix_input_for:
            input_fixed_for += 1
            for k in bn.input_nodes:
                bn[k].state = bninput[k]

        states.append(bn.update())
        
        # Search which attractractors have developed in the run
        attractor_keys = search_attractors(states, bn.atm.dattractors)
        
    return attractor_keys

##############################################

def __test_state(data: tuple):

    s, i = data

    for j, node in enumerate(bn.nodes):
        node.state = s[j]

    a = get_attraction_basin(bn, fix_input_for=fi, bninput=i)
  
    # Only one attractor shall appear for each input in absence of noise
    return binstate(i), a[0][0] if len(a) == 1 else None

def __init_process(d: dict):
    global bn, fi

    bn = SelectiveBooleanNetwork.from_json(d['bn'])
    fi = d['fi']

def test_attraction_basins(bn: SelectiveBooleanNetwork, fix_input_for: int):
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

    attrs = set()
    
    if 2**len(bn) / NP < 1: # 2**8-1: #

        for s, i in params:
        
            for j, node in enumerate(bn.nodes):
                node.state = s[j]

            a = get_attraction_basin(bn, fix_input_for=fix_input_for, bninput=i)

            # Only one attractor shall appear for each input in absence of noise
            if len(a) == 1:
                attrs.add((binstate(i), a[0][0]))
            else:
                return False
    else:   

        man = Manager()

        # Shared json repr of the BN 
        # in order to not waste compute time
        # by serializing and deserializing the BN
        d = man.dict(
            bn=bn.to_json(),
            fi=fix_input_for
        )

        with Pool(processes=NP, initializer=__init_process, initargs=(d, )) as executor:

            attrs = set(executor.map(
                __test_state, 
                params,
                chunksize=NP
            ))
        
        man.shutdown()
    
    # An attractor should appear for at least 1 set of inputs
    # # that is, even if there are repeated keys, all key shall appears at least once
    return dict(attrs) if len(attrs) == len(bn.atm.attractors) else False 

##############################################################################