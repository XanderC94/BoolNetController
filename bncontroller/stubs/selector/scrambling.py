from typing import Callable
import bncontroller.stubs.selector as selector_utils
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.search.utils import bn_scramble_strategy
from bncontroller.sim.config import SimulationConfig

######################################################################

def selector_step1_scramble_strategy(bn:BoolNetSelector, n_flips: int, excluded: set):
    
    do_not_flip = excluded.union(bn.input_nodes)

    return bn_scramble_strategy(bn, n_flips, do_not_flip)

def selector_step2_scramble_strategy(
        bn: BoolNetSelector, step1: Callable[[object], tuple], 
        generator: Callable[[object], BoolNetSelector]):
    
    score, atm = False, None

    if bn is not None:
        bn, (it, score, *_) = step1(bn)
    
    while not score or bn is None:
        bn = generator()
        bn, (it, score, *_) = step1(bn)
        
    return bn, set(), set()