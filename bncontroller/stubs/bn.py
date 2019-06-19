from bncontroller.boolnet.bnstructures import BooleanNode
from bncontroller.boolnet.bnutils import RBNFactory
from bncontroller.boolnet.boolean import r_bool
from bncontroller.file.utils import collection_diff
from bncontroller.json.utils import write_json
import random

def predecessors_t1(node: BooleanNode, N: list, I: list, O: list):
    '''
    This predecessor function create a BN with the given properties:

    * input nodes (I) have only 1 (external) predecessor.
        That is, they are only predecessors to other nodes
        which are not input nodes.
    * hidden nodes (N - I) and outputs (O) have k predecessors
    * outputs nodes (O) can't have another output node as predecessor 
        nor be directly connected to input nodes.
    
    Moreover, Input have connectivity priority, 
    that is the are chosen to be connected before any other node.
    
    As such, Inputs nodes have at least one exiting edge.
    '''
    predecessors = []

    # inputs node must not be connected by other nodes
    if node.label not in I: 
        
        # Exclude from the predecessor choice the node itself (no self-loops) 
        exclusions = [node.label] #+ [n.label for n in nodes if len(n.predecessors) == n.arity]
        priority = []
     
        # outputs nod should not interfer with one another
        # Outputs should not be directly connected to inputs
        if node.label in O:
            exclusions += O
            exclusions += I
        else:
            # First connect other nodes to Input
            priority = [li for li in I if not any(li in n.predecessors for n in N)]

        others = [n.label for n in N if n.label not in priority + exclusions]

        pf = 0.8/len(priority) if len(priority) > 0 else 0
        po = (0.2 if len(priority) > 0 else 1.0)/len(others)

        choices = dict(
            [(k, pf) for k in priority] +
            [(k, po) for k in others]
        )
        
        for _ in range(node.arity):
            predecessors += random.choices(list(choices.keys()), weights=list(choices.values()))
            choices[predecessors[len(predecessors) - 1]] = 0.0

    return predecessors

def predecessors_t2(node: BooleanNode, N: list, I: list, O: list):
    '''
    This predecessor function create a BN with the given properties:

    * input nodes (I) have only 1 (external) predecessor.
        That is, they are only predecessors to other nodes
        which are not input nodes.
    * hidden nodes (N - I) and outputs (O) have k predecessors.
    * outputs nodes (O) can't have another output node as predecessor.
    
    Moreover, Input have connectivity priority, 
    that is the are chosen to be connected before any other node.

    As such, Inputs nodes have at least one exiting edge.
    '''
    predecessors = []

    # inputs node must not be connected by other nodes
    if node.label not in I: 
        
        # Exclude from the predecessor choice the node itself (no self-loops) 
        exclusions = [node.label] #+ [n.label for n in nodes if len(n.predecessors) == n.arity]
        priority = []
     
        # outputs nod should not interfer with one another
        # Outputs should not be directly connected to inputs
        if node.label in O:
            exclusions += O
        else:
            # First connect other nodes to Input
            priority = [li for li in I if not any(li in n.predecessors for n in N)]

        others = [n.label for n in N if n.label not in priority + exclusions]

        pf = 0.8/len(priority) if len(priority) > 0 else 0
        po = (0.2 if len(priority) > 0 else 1.0)/len(others)

        choices = dict(
            [(k, pf) for k in priority] +
            [(k, po) for k in others]
        )
        
        for _ in range(node.arity):
            predecessors += random.choices(list(choices.keys()), weights=list(choices.values()))
            choices[predecessors[len(predecessors) - 1]] = 0.0

    return predecessors

def rbn_gen(N:int, K:int, P:float, I:int, O:int) -> (RBNFactory, list, list):
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
    _O = list(map(str, range(I, I+O))) 
    _K = dict((l, K) if l not in _I else (l, 1) for l in _N)

    return RBNFactory(
        _N, # labels 
        _K, # arities
        predecessors_fun=lambda node, nodes: predecessors_t2(node, nodes, _I, _O),
        bf_init=lambda *args: args[0] if len(args) == 1 else r_bool(P), 
        node_init=lambda label: False
    ), _I, _O

if __name__ == "__main__":
    
    n, k, p, i, o = 20, 3, 0.5, 8, 2
    bng, ia, oa, *_ = rbn_gen(n, k, p, i, o)

    bn = bng.new()

    print('Saving BN...')
    
    write_json(bn.to_json(), './bn_test_model.json', indent=True)