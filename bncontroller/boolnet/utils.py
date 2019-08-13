import random
import re
import asyncio
from bncontroller.typeslib.utils import isnotnone
from bncontroller.collectionslib.utils import flat
from bncontroller.boolnet.structures import BooleanNode, BooleanNetwork, OpenBooleanNetwork

def bnstates_distance(s1:dict, s2:dict, comp = lambda v1, v2: v1 == v2, crit = lambda ds: ds.count(0)):
    '''
    Return the distance between 2 states of a BN.
    The default criterium count the number of states 
    that don't hold the same value.
    '''
    ds = [comp(s2[k1], v1) for k1, v1 in s1.items()]
    return crit(ds)

################################################################################################

def compact_state(state: dict):
    return [int(v) for k, v in sorted(state.items(), key=lambda x: int(x[0]))]

def binstate(state: dict or list) -> str:
    '''
    Return a compact string representation for the given BN state.

    Input can either be an dict or a list.
    '''
    return ''.join(str(x) for x in (compact_state(state) if isinstance(state, dict) else state))
    
################################################################################################

def random_neighbors_generator(node: BooleanNode, nodes:list, self_loops=True):
    '''
    Plain Random generator of neighbors for a single given node
    '''
    predecessors = list()
    excluded = set([] if self_loops else [node.label])

    for _ in range(node.arity):
        predecessors.append(
            random.choice([
                n.label
                for n in nodes 
                if n.label not in excluded.union(predecessors)
            ])
        )

    return predecessors
    
def get_terminal_nodes(bn:BooleanNetwork):

    excluded = set(bn.output_nodes) if isinstance(bn, OpenBooleanNetwork) else set()

    return [
        n.label 
        for n in bn.nodes 
        if not (
            n.label in excluded 
            or any(n.label in x.predecessors for x in bn.nodes)
        )
    ]

async def async_search_attractors(states: list, attractors: dict) -> str:
    '''
    Search and return which of the specified attractors is found inside the state trajectory.

    Attractors are such that they are present more than once inside a single trajectory, 
    usually consecutively in absence noise.

    returns:
        * a list containing the attractors found in the state sequence,
        * for each element of the list are specified:
            - attractor name,
            - number of (continous) matches found
            - length of the longest match
            - length of the shortest match

    '''
    attrpatterns = dict(
        (ak, r'(?:{pattern},?)+'.format(
            pattern=r','.join(map(binstate, attractors[ak])))
        )
        for ak in attractors
    )

    ststring = ','.join(map(binstate, states))

    async def search_pattern(label: str, pattern: str, string: str):
        m = re.findall(pattern, string)
        
        sizes = list(map(len, m))
        pattern_len = len(pattern.replace('(?:', '').replace(',?)+', ''))
        maxlm = int(max(sizes, default=0) / pattern_len)
        minlm = int(min(sizes, default=0) / pattern_len)

        res = label, len(m), maxlm, minlm

        return res if m != None and maxlm > 1 else None

    return list(filter(
            bool,
            await asyncio.gather(*[
                search_pattern(l, p, ststring) 
                for l, p in attrpatterns.items()
            ])
        ))

#####################################################################

############################################################################################

def search_attractors(states: list, attractors: dict) -> str:
    '''
    Search and return which of the specified attractors is found inside the state trajectory.

    Attractors are such that they are present more than once inside a single trajectory, 
    usually consecutively in absence noise.

    returns:
        * a list containing the attractors found in the state sequence,
        * for each element of the list are specified:
            - attractor name,
            - number of (continous) matches found
            - length of the longest match
            - length of the shortest match

    '''
    attrpatterns = dict(
        (ak, r'(?:{pattern},?)+'.format(
            pattern=r','.join(map(binstate, attractors[ak])))
        )
        for ak in attractors
    )

    ststring = ','.join(map(binstate, states))

    def search_pattern(label: str, pattern: str, string: str):
        m = re.findall(pattern, string)
        
        sizes = list(map(len, m))
        pattern_len = len(pattern.replace('(?:', '').replace(',?)+', ''))
        maxlm = int(max(sizes, default=0) / pattern_len)
        minlm = int(min(sizes, default=0) / pattern_len)

        res = label, len(m), maxlm, minlm

        return res if m != None and maxlm > 1 else None

    return list(filter(bool, [
        search_pattern(l, p, ststring) 
        for l, p in attrpatterns.items()
    ]))
    