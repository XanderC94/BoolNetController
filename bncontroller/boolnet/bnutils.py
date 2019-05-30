import random
from bncontroller.boolnet.bnstructures import BooleanNode, BooleanNetwork
from bncontroller.boolnet.bfunction import BooleanFunction
from bncontroller.boolnet.boolean import Boolean, r_bool

def bnstate_distance(s1:dict, s2:dict, comp = lambda v1, v2: v1 == v2, crit = lambda ds: ds.count(0)):
    '''
    Return the distance between 2 states of a BN.
    The default criterium count the number of states 
    that don't hold the same value.
    '''
    ds = [comp(s2[k1], v1) for k1, v1 in s1.items()]
    return crit(ds)

def default_neighbors_generator(node: BooleanNode, nodes:list):

    return [random.choice([
        n.label for n in nodes if n.label != node.label
    ]) for _ in range(node.arity)]

################################################################################################

class RBNFactory(object):
    """
    A Random Boolean Network factory

    * N = Number of node in the BN or a list of node ids 
    * K = (global) Number of Neighbors of each node or a list/map of the NUMBER of neighbors for each single node
    * predecessors_fun = Returns the k neighbors for the node i among the ns available
    * bf_init = Decides whether the BN is going to be a simple BN or a RBN. 
        Takes a vararg as input since it receives the the truth table entries 
        of the boolean function (tuple of length k)
    * node_init = Decides the initial state value of each node
    """
    def __init__(self,
            n: int or list, 
            k: int or list or dict, 
            predecessors_fun = lambda node, nodes: default_neighbors_generator(node, nodes), 
            bf_init = lambda *args: r_bool(), 
            node_init = lambda label: r_bool()):
        
        self.node_labels = list()
        self.node_arities = dict()
        self.predecessors_fun = predecessors_fun
        self.bf_init = bf_init
        self.node_init = node_init

        if isinstance(n, int): 
            self.node_labels = list(range(n)) 
        elif isinstance(n, list):
            self.node_labels = n
        else:
            raise Exception(f'Boolean Network does not accept {type(n)} as node ids. Use List or Int (0 ot N-1).')

        if isinstance(k, int): 
            self.node_arities = dict([(label, k) for label in self.node_labels])
        elif isinstance(k, list):
            
            self.node_arities = dict([(label, k) for label in zip(self.node_labels, k)])
        elif isinstance(k, dict):
            self.node_arities = k
        else:
            raise Exception(f'Boolean Network does not accept {type(k)} as node neighbors number. Use List, Dict or Int (each node has K neighbors).')

    def new(self):

        nodes = [
            BooleanNode(
                label, 
                [], 
                BooleanFunction(self.node_arities[label], result_generator = self.bf_init), 
                self.node_init(label)
            ) for label in self.node_labels
        ]

        for node in nodes: 
            node.predecessors = self.predecessors_fun(node, nodes)

        return BooleanNetwork(nodes)

#################################################################################################

if __name__ == "__main__":
    
    import time

    # bfg = lambda: Boolean(random.choice([0.2, 0.35, 0.5, 0.65, 0.8]))
    n, k, p = 10, 3, 0.6
    bn = RBNFactory(n, k, bf_init=lambda *args: r_bool(p), node_init=lambda i:False).new()

    # print('Saving BN...')
    # with open('bn.json', 'w') as fp:
    #     json.dump(bn.to_json(), fp, indent=4)
    
    print(bn)

    print('Performance test...')
    s1 = bn.state
    d, maxIter, it = -1, 1000, 0
    
    print('s0:', s1)
    t = time.perf_counter()
    
    while d != 0 and it < maxIter:
        s2 = bn()
        
        print(s2)
        d = bnstate_distance(s1, s2)
        print(d)

        s1 = s2
        it += 1
    
    print(time.perf_counter() - t)