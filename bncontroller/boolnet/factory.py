import random
from typing import Callable
from bncontroller.boolnet.structures import BooleanNode, BooleanNetwork, OpenBooleanNetwork
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.boolnet.function import BooleanFunction
from bncontroller.boolnet.boolean import Boolean, r_bool
from bncontroller.boolnet.utils import random_neighbors_generator

class RBNFactory(object):
    """
    A Random Boolean Network factory

    * N = Number of node in the BN or a list of node ids 
    * K = Number of Neighbors of each node or a list/map of the Number of neighbors for each single node
    * P = probability or function to set True/False the entry of the Truth Table,
    * Q = probability or function to set True/False the initial state of a node,
    * I = number or list of input nodes,
    * O = number or list of output nodes,
    * f = predecessor function that returns the k neighbors for the node i among the ns available
    """
    def __init__(self,
            n: int or list, 
            k: int or list or dict,
            p: float or Callable[[object], bool] = 0.5,
            q: float or Callable[[object], bool] = 0.5,
            i: int or list = [], 
            o: int or list = [], 
            f = lambda node, nodes: random_neighbors_generator(node, nodes)
            ): 
        
        self.node_labels = list()
        self.node_arities = dict()
        self.input_nodes = list()
        self.output_nodes = list()
        self.predecessors_fun = f
        self.bf_init = p if callable(p) else lambda *args: r_bool(p)
        self.node_init = q if callable(q) else lambda *args: r_bool(q)

        if isinstance(n, int): 
            self.node_labels = list(map(str, range(n)))
        elif isinstance(n, list):
            self.node_labels = n
        else:
            raise Exception(f'Boolean Network does not accept {type(n)} as node ids. Use List or Int (0 ot N-1).')

        if isinstance(i, int): 
            self.input_nodes = list(map(str, range(i)))
        elif isinstance(o, list):
            self.input_nodes = i
        else:
            raise Exception(f'Boolean Network does not accept {type(i)} as node ids. Use List or Int (0 ot N-1).')

        if isinstance(o, int): 
            self.output_nodes = list(map(str, range(i, i+o))) 
        elif isinstance(o, list):
            self.output_nodes = o
        else:
            raise Exception(f'Boolean Network does not accept {type(o)} as node ids. Use List or Int (0 ot N-1).')

        if isinstance(k, int): 
            self.node_arities = dict([(label, k) for label in self.node_labels])
        elif isinstance(k, list):
            self.node_arities = dict(zip(self.node_labels, k))
        elif isinstance(k, dict):
            self.node_arities = k
        else:
            raise Exception(f'Boolean Network does not accept {type(k)} as node neighbors number. Use List, Dict or Int (each node has K neighbors).')

    def __build_nodes(self):
        nodes = [
            BooleanNode(
                label, 
                [], 
                BooleanFunction(self.node_arities[label], result_generator=self.bf_init), 
                self.node_init(label)
            ) for label in self.node_labels
        ]

        return nodes

    def __connect_nodes(self, nodes):
        for node in nodes: 
            node.predecessors = self.predecessors_fun(node, nodes)
        return nodes

    def __r_connect_nodes(self, nodes):
        
        scrambled_nodes = list(nodes)

        random.shuffle(scrambled_nodes)

        for node in scrambled_nodes:
            node.predecessors = self.predecessors_fun(node, nodes)

        return nodes

    def new(self) -> BooleanNetwork:

        nodes = self.__connect_nodes(self.__build_nodes())

        return BooleanNetwork(nodes)

    def new_obn(self) -> OpenBooleanNetwork:

        nodes = self.__r_connect_nodes(self.__build_nodes())

        return OpenBooleanNetwork(nodes, input_nodes=self.input_nodes, output_nodes=self.output_nodes)

    def new_selector(self) -> SelectiveBooleanNetwork:

        nodes = self.__r_connect_nodes(self.__build_nodes())

        return SelectiveBooleanNetwork(nodes, input_nodes=self.input_nodes, output_nodes=self.output_nodes)

#######################################################################################

def generate_rbn(generator: Callable[[], BooleanNetwork], force_consistency=False):
    '''
    Generate an RBN from the given generator.

    This is simply a "joint" method useful to generate consistents RBN, 
    based on their definition of consistency.
    '''
    bn = generator()
    
    while force_consistency and not bn.is_consistent:
        bn = generator()
    
    return bn