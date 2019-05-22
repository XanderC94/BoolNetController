from boolean_function import BooleanFunction
from boolean import Boolean, rBool
import json, time, random

class BooleanNode(object):

    def __init__(self, nodeId, neighbors:list, bf : BooleanFunction, initState=rBool):
        self.__nodeId = nodeId
        self.__neighbors = neighbors
        self.bf = bf
        self.__hash = hash(str(self.__nodeId))
        self.__state = initState
    
    def nid(self):
        return self.__nodeId

    def neighbors(self) -> list:
        return self.__neighbors

    def state(self) -> bool:
        '''
        Return the state (bool) of the encapsulated Boolean Variable.
        This does not evaluate the Boolean Function (e.g.: Probabilistic Booleans) 
        so it returns always the same value between successive evaluations.  
        '''
        return self.__state

    def __setitem__(self, params: tuple, newValue: Boolean):
        self.bf[params] = newValue

    def __getitem__(self, params: tuple) -> Boolean:
        return self.bf[params]

    def __hash__(self):
        return self.__hash
    
    def __call__(self, params: tuple) -> bool:
        '''
        Evaluate the encapsulated boolean function for the given bool tuple.
        Equivalent to call the <BooleanNode.evaluate> method
        '''
        self.__state = self.bf(params) 
        return self.__state
    
    def evaluate(self, params: tuple) -> bool:
        '''
        Evaluate the encapsulated boolean function for the given bool tuple.
        Equivalent to call the <BooleanNode.__call__> property.
        '''
        return self(params)

    def toJson(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object
        """
        return {'id':self.nid(), 'inputs': self.neighbors(), 'bf':self.bf.toJson()}

    def __str__(self):
        return str(self.toJson())

    @staticmethod
    def fromJson(json:dict):
        return BooleanNode(json['id'], json['inputs'], BooleanFunction.fromJson(json['bf']))

class BooleanNetwork(object):
    '''
    An simple implementation of a BN using the <Boolean> wrappers for bool values which implements both
    Determinstic and Probabilistic Boolean variables.
    '''
    def __init__(self, N, K,
        neighborFun = lambda i, k, ns: [ns[(i + j + 1) % len(ns)] for j in range(k)], 
        bfInit = lambda *args: Boolean(rBool()),
        nInit = lambda nid: rBool()):

        nids = list()
        nks = list()

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
            self[str(nid)] = BooleanNode(nid, neighborFun(nid, nks[nid], nids), BooleanFunction(nks[nid], generator = bfInit), nInit(nid))

    def __setitem__(self, nodeId, newNode: BooleanNode):
        self.__bn[str(nodeId)] = newNode

    def __getitem__(self, nodeId) -> BooleanNode:
        return self.__bn[str(nodeId)]

    def items(self):
        return list(self.__bn.items())

    def state(self) -> dict:
        '''
        Return the current state of the BN as a dictionary where the keys are the Nodes Id
        while the value are the current node state.
        See <BooleanNode.state> for more info. 
        '''
        return dict([(k, v.output()) for k, v  in self.__bn.items()])

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

    def toJson(self):
        """
        Return a (valid) json representation (dict) of this object.
        """
        return dict([(k, v.toJson()) for k, v  in self.__bn.items()])

    @staticmethod
    def fromJson(json:dict):

        bn = BooleanNetwork(0, 0)

        for nid, node in json.items:
            bn[nid] = BooleanNode.fromJson(node)

        return bn

    def __str__(self):
        return str(self.toJson())


def stateDistance(s1:dict, s2:dict, crit = lambda ds: ds.count(False)):
    '''
    Return the distance between 2 states of a BN.
    The default criterium count the number of states 
    that haven't hold the same value.
    '''
    ds = [abs(s2[k1] == v1) for k1, v1 in s1.items()]
    return crit(ds)

if __name__ == "__main__":
    
    # bfg = lambda: Boolean(random.choice([0.2, 0.35, 0.5, 0.65, 0.8]))

    bn = BooleanNetwork(10, 3, bfInit= lambda *args: Boolean(rBool()), nInit=lambda i:False)

    print('Saving BN...')
    with open('bn.json', 'w') as fp:
        json.dump(bn.toJson(), fp, indent=4)

    print('Performance test...')
    s1 = bn.state()
    d, maxIter, it = -1, 1000, 0
    
    print('s0:', s1)
    t = time.perf_counter()
    
    while d != 0 and it < maxIter:
        s2 = bn()
        
        print(s2)
        d = stateDistance(s1, s2)
        print(d)

        s1 = s2
        it += 1
    
    print(time.perf_counter() - t)