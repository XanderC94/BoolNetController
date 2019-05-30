from bncontroller.boolnet.bfunction import BooleanFunction
from bncontroller.boolnet.boolean import Boolean, r_bool
from bncontroller.ntree.ntstructures import NTree
from bncontroller.json_utils import Jsonkin
import json

class BooleanNode(Jsonkin):

    def __init__(self, label, predecessors: list, bf: BooleanFunction, init_state=r_bool()):
        self.__label = label
        self.__predecessors = predecessors
        self.__boolfun = bf
        self.__hash = hash(str(self.__label))
        self.__state = Boolean(init_state)
    
    @property
    def label(self):
        return self.__label
    
    @property
    def bf(self) -> BooleanFunction:
        return self.__boolfun

    @bf.setter
    def bf(self, new_bf: BooleanFunction):
        self.__boolfun = new_bf

    @property
    def arity(self):
        return self.bf.arity

    @property
    def predecessors(self) -> list:
        return self.__predecessors
    
    @predecessors.setter
    def predecessors(self, nodes: list):
        self.__predecessors = nodes

    @property
    def state(self) -> bool:
        '''
        Return the current state (bool) of the Boolean Node.
        This does not evaluate the Boolean Function (e.g.: Probabilistic Booleans) 
        so it returns always the same value between successive evaluations.  
        '''
        return self.__state()

    @state.setter
    def state(self, new_state):
        '''
        Set the state for the current Boolean Node 
        that will be used to evaluate final network state.
        '''
        self.__state.bias = new_state
    
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
        return {'id':self.label, 'inputs': self.predecessors, 'bf':self.bf.to_json()}

    def __setitem__(self, params: tuple, new_value: Boolean):
        self.bf[params] = new_value

    def __getitem__(self, params: tuple) -> Boolean:
        return self.bf[params]

    def __hash__(self):
        return self.__hash
    
    def __call__(self, params: tuple) -> bool:
        '''
        Evaluate the encapsulated boolean function for the given bool tuple.

        Returns the current node state.
        
        Equivalent to call the <BooleanNode.evaluate> method
        '''
        self.state = self.bf(params) 
        return self.state

    @staticmethod
    def from_json(json:dict):
        return BooleanNode(json['id'], json['inputs'], BooleanFunction.from_json(json['bf']))

##########################################################################################################

class BooleanNetwork(Jsonkin):

    '''
    An simple implementation of a BN using the <Boolean> wrappers for bool values which implements both
    Determinstic and Probabilistic Boolean variables.
    '''
    def __init__(self, nodes: list):

        self.__bn = {}

        for node in nodes:
            self[str(node.label)] = node 
  
    @property
    def keys(self):
        return list(self.__bn.keys())
    @property
    def nodes(self):
        return list(self.__bn.values())

    @property
    def state(self) -> dict:
        '''
        Return the current state of the BN as a dictionary where the keys are the Nodes Id
        while the value are the current node state.
        See <BooleanNode.state> for more info. 
        '''
        return dict((k, v.state) for k, v  in self.to_pairlist())

    def to_pairlist(self):
        return list(self.__bn.items())
    
    def step(self):
        '''
        Evaluate the new network state.

        S(bn) = (s(x0), ..., s(xi)) : i in N(bn)
        '''
        return self()
    
    def __setitem__(self, node_label, new_node: BooleanNode):
        self.__bn[str(node_label)] = new_node

    def __getitem__(self, node_label) -> BooleanNode:
        return self.__bn[str(node_label)]

    def __len__(self):
        return len(self.__bn)

    def __call__(self):
        
        oldstate = self.state

        for _, node in self.to_pairlist():
            nparams = tuple([oldstate[str(nn)] for nn in node.predecessors])
            node.evaluate(nparams)

        return self.state

    def to_json(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object.
        """
        return dict((k, v.to_json()) for k, v  in self.to_pairlist())

    @staticmethod
    def from_json(json:dict):

        bn = BooleanNetwork([])

        for nid, node in json.items():
            bn[nid] = BooleanNode.from_json(node)

        return bn