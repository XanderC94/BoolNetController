from bncontroller.boolnet.bnstructures import BooleanNode
from bncontroller.boolnet.bnutils import RBNFactory
from bncontroller.boolnet.boolean import r_bool
from bncontroller.utils import collection_diff
import random

def experiment_predecessors_fun(node: BooleanNode, nodes: list, bn_inputs: list, bn_outputs: list):

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

def experiment_rbng(N, K, P, I, O) -> RBNFactory:
    """
    Generates a Random Boolean Network Generator which bn have the following properties:

    * input nodes (I) have only 1 (external) predecessor.
        That is, they are only predecessors to other nodes 
    * hidden nodes (N - I) and outputs (O) have k predecessors
    * outputs nodes (O) can't have another output node as predecessor
    """
    return RBNFactory(
        list(range(N)), # labels 
        dict((l, K) if l not in I else (l, 1) for l in range(N)), # arities
        predecessors_fun=lambda node, nodes: experiment_predecessors_fun(node, nodes, I, O),
        bf_init=lambda *args: args[0] if len(args) == 1 else r_bool(P), 
        node_init=lambda label: False
    )