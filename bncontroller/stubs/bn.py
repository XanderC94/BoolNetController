from bncontroller.boolnet.bnstructures import BooleanNode
from bncontroller.boolnet.bnutils import RBNFactory
from bncontroller.boolnet.boolean import r_bool
from bncontroller.file.utils import collection_diff
from bncontroller.json.utils import write_json
import random

def predecessors(node: BooleanNode, nodes: list, bn_inputs: list, bn_outputs: list):

    predecessors = []

    # inputs node must not be connected by other nodes (?)
    if node.label not in bn_inputs: 
        
        labels = [n.label for n in nodes]
        
        # Exclude from the predecessor choice the node itself (no self-loops) 
        # and all the other nodes with enough predecessors (len(p) == k)

        exclusions = [node.label] #+ [n.label() for n in nodes if len(n.predecessors()) == arity or n.label() in bn_inputs]

        # outputs nod should not interfer with one another
        if node.label in bn_outputs:
            exclusions += bn_outputs
        # if node.label() in bn_inputs:
        #     exclusions += bn_inputs
        
        for _ in range(node.arity):
            
            predecessors.append(
                random.choice(
                    collection_diff(labels, exclusions + predecessors)
                )
            )
    
    return predecessors

def rbn_gen(N:int, K:int, P:float, I:int, O:int) -> (RBNFactory, list, list):
    """
    Generates a Random Boolean Network Generator which bn have the following properties:

    * input nodes (I) have only 1 (external) predecessor.
        That is, they are only predecessors to other nodes 
    * hidden nodes (N - I) and outputs (O) have k predecessors
    * outputs nodes (O) can't have another output node as predecessor
    """

    _N = list(map(str, range(N)))
    _I = list(map(str, range(I))) 
    _O = list(map(str, range(I, O))) 
    _K = dict((l, K) if l not in _I else (l, 1) for l in _N)


    return RBNFactory(
        _N, # labels 
        _K, # arities
        predecessors_fun=lambda node, nodes: predecessors(node, nodes, _I, _O),
        bf_init=lambda *args: args[0] if len(args) == 1 else r_bool(P), 
        node_init=lambda label: False
    ), _I, _O

if __name__ == "__main__":
    
    n, k, p, i, o = 20, 2, 0.5, 8, 2
    bng, ia, oa, *_ = rbn_gen(n, k, p, i, o)

    bn = bng.new()

    print('Saving BN...')
    
    write_json(bn.to_json(), './bn_test_model.json', indent=True)