from typing import Callable
import bncontroller.stubs.selector as selector_utils
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.search.parametric import default_scramble_strategy
from bncontroller.sim.config import SimulationConfig

def train_scramble_strategy(bn: OpenBooleanNetwork, n_flips:int, excluded:set={}):
    '''
    Default scrambling strategy for vns algorithm.
    Scrambling = flips generation + boolean network edit

    returns the modified bn, the applied flips and their hashset
    '''
    terminal_nodes = list(
        n.label 
        for n in bn.nodes 
        if n.label not in bn.output_nodes and not any(n.label in x.predecessors for x in bn.nodes)
    )

    do_not_flip = excluded.union(set(map(hash, bn.input_nodes + terminal_nodes)))

    return default_scramble_strategy(bn, n_flips, do_not_flip)

def selector_step1_scramble_strategy(bn, n_flips:int, excluded:set):
    
    do_not_flip = excluded.union(set(map(hash, bn.input_nodes)))

    return default_scramble_strategy(bn, n_flips, do_not_flip)


def selector_step2_scramble_strategy(
        bn: BoolNetSelector, 
        step1: Callable[[object], tuple], 
        generator: Callable[[object], BoolNetSelector]):
    
    score, atm = False, None

    if bn is not None:
        bn, (it, score, *_) = step1(bn)
    
    while not score or bn is None:
        bn = generator()
        bn, (it, score, *_) = step1(bn)

    return bn, set(), set()