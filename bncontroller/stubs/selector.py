import re
import asyncio
import random
from bncontroller.stubs.bn import rbn_gen, is_obn_consistent
from bncontroller.type.utils import isnotnone, first
from bncontroller.boolnet.utils import binstate, compact_state
from bncontroller.boolnet.atm import AttractorsTransitionMatrix as ATM
from bncontroller.boolnet.selector import BoolNetSelector

def generate_selector(template):

    bng, I, O, *_ = rbn_gen(
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

def noisy_run(bn: BoolNetSelector, steps:int, input_step=1):

    states = []
    __input_step = 0

    for i in range(steps):

        if input_step + __input_step == i:
            __input_step += input_step
            for k in bn.input_nodes:
                bn[k].state = random.choice([True, False])

        if random.choice([True, False, False, False, False]):
            
            pop = set(bn.keys).difference(bn.input_nodes)
            noisy_nodes = random.sample(
                pop, 
                random.choice([1, len(pop)])
            )
            
            for k in noisy_nodes:
                bn[k].state = random.choice([True, False])

        states.append(compact_state(bn.step()))

    return states

def search_attractors(states: list, attractors: dict) -> str:
   
    attrpatterns = dict(
        (apattern, r','.join(map(binstate, attractors[apattern])))
        for apattern in attractors
    )

    ststring = ','.join(map(binstate, states))
    
    async def search_pattern(label, pattern, string):
        m = re.findall(pattern, string)
        return label if  m != None and len(m) > 1 else None

    async def asynctask(string, patterns):
        return list(filter(
            isnotnone,
            await asyncio.gather(*[search_pattern(l, p, string) for l, p in patterns.items()])
        ))
    
    return asyncio.run(asynctask(ststring, attrpatterns))

def is_attractor_space_omogeneous(bn, atm, n_attractors):

    states = noisy_run(
        bn, 
        max(map(len, atm.attractors))*len(bn)*10, 
        input_step=max(map(len, atm.attractors)) * 2,
    )
    found_attrs = search_attractors(states, atm.dattractors)
    
    return len(set(found_attrs)) == n_attractors

def is_bnselector_consistent(bn: BoolNetSelector, atm: ATM, n_attractors:int, trans_biases:dict):

    return (
        len(atm.attractors) == n_attractors 
        and all(
            atm.dtableau[ki][kj] >= trans_biases[ki][kj] 
            for ki in trans_biases
            for kj in trans_biases[ki]
        )
        and is_attractor_space_omogeneous(bn, atm, n_attractors) # True
    )