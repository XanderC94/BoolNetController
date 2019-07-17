import random
from bncontroller.boolnet.structures import BooleanNode

def bnstates_distance(s1:dict, s2:dict, comp = lambda v1, v2: v1 == v2, crit = lambda ds: ds.count(0)):
    '''
    Return the distance between 2 states of a BN.
    The default criterium count the number of states 
    that don't hold the same value.
    '''
    ds = [comp(s2[k1], v1) for k1, v1 in s1.items()]
    return crit(ds)

################################################################################################

def compact_state(state:dict):
    return [int(v) for k, v in sorted(state.items())]

def binstate(state:dict or list):
    return ''.join(str(x) for x in (state.values() if isinstance(state, dict) else state))

################################################################################################

def random_neighbors_generator(node: BooleanNode, nodes:list):

    return [random.choice([
        n.label for n in nodes if n.label != node.label
    ]) for _ in range(node.arity)]
