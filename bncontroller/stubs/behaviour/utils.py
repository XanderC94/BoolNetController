import random
from typing import Callable
from bncontroller.boolnet.structures import BooleanNode
from bncontroller.boolnet.factory import RBNFactory
from bncontroller.boolnet.boolean import r_bool
from bncontroller.boolnet.structures import OpenBooleanNetwork, BooleanNetwork
from bncontroller.sim.config import Config

##################################################################################

def predecessors(node: BooleanNode, N: list, I: list, O: list, pp=0.8):
    '''
    This predecessor function create a BN with the given properties:

    * input nodes (I) have only 1 (external) predecessor.
        That is, they are only predecessors to other nodes
        which are not input nodes.
    * No self-loops
    * hidden nodes (N - I) and outputs (O) have k predecessors.
    * outputs nodes (O) can't have another output node as predecessor.
    
    Moreover, Input have connectivity priority, 
    that is the are chosen to be connected before any other node.

    As such, Inputs nodes have at least one exiting edge.
    '''
    predecessors = list()

    # inputs node must not be connected by other nodes
    if node.label in I: 
        return predecessors

    # Exclude from the predecessor choice the node itself (no self-loops) 
    exclusions = [node.label] # + O
    priority = []
    
    # # outputs node should not interfer with one another
    # # Outputs should not be directly connected to inputs (?)
    if node.label in O:
        exclusions += O
    #     exclusions += I
    
    # Each node must be at least predecessor to another node
    # priority = [
    #     n1.label 
    #     for n1 in N 
    #     if n1.label not in exclusions # no-self loops
    #     if not any(
    #         n1.label in n2.predecessors 
    #         for n2 in N
    #     )
    # ]

    # if len(priority) > 0:
    #     predecessors += random.choices(priority, k=1)

    others = [
        n.label 
        for n in N 
        if n.label not in exclusions + predecessors
    ]

    k = node.arity - len(predecessors)

    predecessors += random.sample(others, k=k)

    return predecessors

######################################################################################################

def template_behaviour_generator(N: int, K: int, P: float, Q: float, I:int, O:int, F=predecessors) -> RBNFactory:
    """
    Generates a Random Boolean Network Generator which bn have the following properties:

    * input nodes (I) have only 1 (external) predecessor.
        That is, they are only predecessors to other nodes 
    * hidden nodes (N - I) and outputs (O) have k predecessors
    * outputs nodes (O) can't have another output node as predecessor 
        nor be directly connected to input nodes.
    """

    _N = list(map(str, range(N)))
    _I = list(map(str, range(I))) 
    _O = list(map(str, range(I, I + O))) 
    _K = dict(
        (l, K) 
        if l not in _I else (l, 1)
        # if l not in _I else (l, 0)
        for l in _N
    )

    return RBNFactory(
        n=_N, # labels 
        k=_K, # arities
        p=lambda *args: args[0] if len(args) == 1 else r_bool(P), 
        q=lambda label: r_bool(Q),
        i=_I,
        o=_O,
        f=lambda node, nodes: F(node, nodes, _I, _O)
    )
