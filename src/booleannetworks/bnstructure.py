from booleanfunction import BooleanFunction
from boolean import Boolean, r_bool
from ntree import NTree
import json, time, random

class BooleanNode(object):

    def __init__(self, label, neighbors:list, bf : BooleanFunction, init_state=r_bool):
        self.__label = label
        self.__neighbors = neighbors
        self.boolfun = bf
        self.__hash = hash(str(self.__label))
        self.__state = init_state
    
    def label(self):
        return self.__label

    def neighbors(self) -> list:
        return self.__neighbors

    def state(self) -> bool:
        '''
        Return the state (bool) of the encapsulated Boolean Variable.
        This does not evaluate the Boolean Function (e.g.: Probabilistic Booleans) 
        so it returns always the same value between successive evaluations.  
        '''
        return self.__state

    def __setitem__(self, params: tuple, new_value: Boolean):
        self.boolfun[params] = new_value

    def __getitem__(self, params: tuple) -> Boolean:
        return self.boolfun[params]

    def __hash__(self):
        return self.__hash
    
    def __call__(self, params: tuple) -> bool:
        '''
        Evaluate the encapsulated boolean function for the given bool tuple.
        Equivalent to call the <BooleanNode.evaluate> method
        '''
        self.__state = self.boolfun(params) 
        return self.__state
    
    def evaluate(self, params: tuple) -> bool:
        '''
        Evaluate the encapsulated boolean function for the given bool tuple.
        Equivalent to call the <BooleanNode.__call__> property.
        '''
        return self(params)

    def to_json(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object
        """
        return {'id':self.label(), 'inputs': self.neighbors(), 'bf':self.boolfun.to_json()}

    def __str__(self):
        return str(self.to_json())

    @staticmethod
    def from_json(json:dict):
        return BooleanNode(json['id'], json['inputs'], BooleanFunction.from_json(json['bf']))

###############################################################################################################

class BooleanNetwork(object):

    '''
    An simple implementation of a BN using the <Boolean> wrappers for bool values which implements both
    Determinstic and Probabilistic Boolean variables.

    * N = Number of node in the BN or a list of node ids 
    * K = (global) Number of Neighbors of each node or a list/map of the NUMBER of neighbors for each single node
    * neighborFun = Returns the k neighbors for the node i among the ns available
    * bfInit = Decides whether the BN is going to be a simple BN or a RBN. 
        Takes a vararg as input since it receives the the truth table entries 
        of the boolean function (tuple of length k)
    * nInit = Decides the initial state value of each node

    '''
    def __init__(self, N, K, 
    neighborFun = lambda i, k, ns: [ns[(i + j + 1) % len(ns)] for j in range(k)], 
    bfInit = lambda *args: Boolean(r_bool()), 
    nInit = lambda nid: r_bool()):

        nids = list()
        nks = dict()

        if isinstance(N, int): 
            nids = list(range(N)) 
        elif isinstance(N, list):
            nids = N
        else:
            raise Exception(f'Boolean Network does not accept {type(N)} as node ids. Use List or Int (0 ot N-1).')

        if isinstance(K, int): 
            nks = dict([(nid, K) for nid in nids])
        elif isinstance(K, list):
            
            nks = dict([(nid, K) for nid in zip(nids, K)])
        elif isinstance(K, dict):
            nks = K
        else:
            raise Exception(f'Boolean Network does not accept {type(K)} as node neighbors number. Use List, Dict or Int (each node has K neighbors).')

        self.__bn = dict({})

        for nid in nids:
            self[str(nid)] = BooleanNode(nid, neighborFun(nid, nks[nid], nids), BooleanFunction(nks[nid], result_generator = bfInit), nInit(nid))

    def __setitem__(self, nodeId, newNode: BooleanNode):
        self.__bn[str(nodeId)] = newNode

    def __getitem__(self, nodeId) -> BooleanNode:
        return self.__bn[str(nodeId)]

    def __len__(self):
        return len(self.keys())

    def to_pairlist(self):
        return list(self.__bn.items())

    def keys(self):
        return list(self.__bn.keys())
    
    def nodes(self):
        return list(self.__bn.values())

    def state(self) -> dict:
        '''
        Return the current state of the BN as a dictionary where the keys are the Nodes Id
        while the value are the current node state.
        See <BooleanNode.state> for more info. 
        '''
        return dict([(k, v.state()) for k, v  in self.__bn.items()])

    def __call__(self):
        
        oldstate = self.state()

        for _, node in self.__bn.items():
            nparams = tuple([oldstate[str(nn)] for nn in node.neighbors()])
            node.evaluate(nparams)

        return self.state()

    def step(self):
        '''
        Evaluate the new network state.

        S(bn) = (s(x0), ..., s(xi)) : i in N(bn)
        '''
        return self()

    def to_json(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object.
        """
        return dict([(k, v.to_json()) for k, v  in self.__bn.items()])

    @staticmethod
    def from_json(json:dict):

        bn = BooleanNetwork(0, 0)

        for nid, node in json.items:
            bn[nid] = BooleanNode.from_json(node)

        return bn

    def __str__(self):
        return str(self.to_json())

####################################################################################################

def bnstate_distance(s1:dict, s2:dict, comp = lambda v1, v2: v1 == v2, crit = lambda ds: ds.count(0)):
    '''
    Return the distance between 2 states of a BN.
    The default criterium count the number of states 
    that haven't hold the same value.
    '''
    ds = [comp(s2[k1], v1) for k1, v1 in s1.items()]
    return crit(ds)

#####################################################################################################

if __name__ == "__main__":
    
    # bfg = lambda: Boolean(random.choice([0.2, 0.35, 0.5, 0.65, 0.8]))

    bn = BooleanNetwork(10, 3, bfInit= lambda *args: Boolean(r_bool()), nInit=lambda i:False)

    print('Saving BN...')
    with open('bn.json', 'w') as fp:
        json.dump(bn.to_json(), fp, indent=4)

    print('Performance test...')
    s1 = bn.state()
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