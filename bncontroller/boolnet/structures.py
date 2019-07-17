import json
from pathlib import Path
from bncontroller.boolnet.function import BooleanFunction
from bncontroller.boolnet.boolean import Boolean, r_bool
from bncontroller.boolnet.atm import AttractorsTransitionMatrix as ATM
from bncontroller.jsonlib.utils import Jsonkin, jsonrepr

class BooleanNode(Jsonkin):

    def __init__(self, label:str, predecessors: list, bf: BooleanFunction, init_state=r_bool()):
        self.__label = str(label)
        self.__predecessors = sorted(predecessors)
        self.__boolfun = bf
        self.__hash = hash(str(self.__label))
        self.__init_state = bool(init_state)
        self.__state = Boolean(init_state)
    
    @property
    def label(self) -> str:
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
        self.__predecessors = sorted(nodes)

    @property
    def state(self) -> bool:
        '''
        Return the current state (bool) of the Boolean Node.
        This does not evaluate the Boolean Function (e.g.: Probabilistic Booleans) 
        so it returns always the same value between successive evaluations.  
        '''
        return bool(self.__state)

    @state.setter
    def state(self, new_state):
        '''
        Set the state for the current Boolean Node 
        that will be used to evaluate final network state.
        '''
        self.__state.bias = bool(new_state)
    
    def evaluate(self, params: tuple) -> bool:
        '''
        Evaluate the encapsulated boolean function for the given bool tuple.
        Equivalent to call the <BooleanNode.__call__> property.
        '''
        return self(params)

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

    def to_json(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object
        """
        return {
            'id':self.label, 
            'inputs': self.predecessors, 
            'bf':self.bf.to_json(), 
            'istate': self.__init_state, 
            'cstate': self.state
        }

    @staticmethod
    def from_json(json:dict):
        return BooleanNode(json['id'], json['inputs'], BooleanFunction.from_json(json['bf']), json['istate'])

    def to_ebnf(self):
        return self.bf.as_logic_expr([f'n{x}' for x in self.predecessors])

##########################################################################################################

class BooleanNetwork(Jsonkin):

    '''
    An simple implementation of a BN using the <Boolean> wrappers for bool values which implements both
    Determinstic and Probabilistic Boolean variables.
    '''
    def __init__(self, nodes: list):

        self.__nodes = {}
        self.__atm = None

        for node in nodes:
            self[node.label] = node 
  
    @property
    def keys(self):
        return list(self.__nodes.keys())
        
    @property
    def nodes(self):
        return list(self.__nodes.values())

    @property
    def state(self) -> dict:
        '''
        Return the current state of the BN as a dictionary where the keys are the Nodes Id
        while the value are the current node state.
        See <BooleanNode.state> for more info. 
        '''
        return dict((k, v.state) for k, v in self.to_pairlist())

    def to_pairlist(self):
        return self.__nodes.items()
    
    def step(self):
        '''
        Evaluate the new network state.

        S(bn) = (s(x0), ..., s(xi)) : i in N(bn)

        Equivalent to <__call__>
        '''
        return self()
    
    def __setitem__(self, node_label:str, new_node: BooleanNode):
        self.__nodes[str(node_label)] = new_node

    def __getitem__(self, node_label) -> BooleanNode:
        return self.__nodes[str(node_label)]

    def __len__(self):
        return len(self.__nodes)
    
    def __iter__(self):
        for p in self.to_pairlist():
            yield p

    def __call__(self):
        '''
        Evaluate the new network state.

        S(bn) = (s(x0), ..., s(xi)) : i in N(bn)

        Equivalent to <step>
        '''
        oldstate = dict(self.state) # Copy old state

        for node in self.nodes:
            if node.predecessors:
                fparams = [oldstate[node.predecessors[i]] for i in range(node.arity)]
                node.evaluate(tuple(fparams))

        return self.state

    def to_json(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object.
        """
        return dict(nodes=[jsonrepr(v) for v in self.nodes])

    @staticmethod
    def from_json(json:dict):

        nodes = [BooleanNode.from_json(node) for node in json['nodes']]

        return BooleanNetwork(nodes)
    
    def to_ebnf(self):

        expr_format = '{target}, {factor}'

        return '''targets, factors\n{expressions}\n'''.format(
            expressions='\n'.join(
                [expr_format.format(
                    target=f'n{k}',
                    factor=node.to_ebnf()
                ) for k, node in self]
            )
        )

    def get_atm(self, atm_ws_path=Path('./atm-workspace.txt'), encoding='UTF-8', from_cache=False):
        if from_cache and self.__atm:
            return self.__atm
        else:      
            self.__atm = ATM(self.to_ebnf(), atm_ws_path=atm_ws_path, encoding=encoding)
            return self.__atm

    def set_atm(self, atm:ATM):
        self.__atm = atm

#############################################################################

class OpenBooleanNetwork(BooleanNetwork):

    def __init__(self, nodes: list, input_nodes = [], output_nodes = []):
        super().__init__(nodes)
    
        self.__input_nodes = sorted(list(set(input_nodes)))
        self.__output_nodes = sorted(list(set(output_nodes)))

    @property
    def input_nodes(self):
        return self.__input_nodes

    @property
    def output_nodes(self):
        return self.__output_nodes
    
    def to_json(self):
        __json = super().to_json()

        __json.update({
            'inputs': self.input_nodes,
            'outputs': self.output_nodes
        })

        return __json

    @staticmethod
    def from_json(json:dict):

        nodes = [BooleanNode.from_json(node) for node in json['nodes']]
        
        return OpenBooleanNetwork(nodes, json['inputs'], json['outputs'])
        