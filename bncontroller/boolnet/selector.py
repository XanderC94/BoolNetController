from collections import defaultdict
from bncontroller.boolnet.structures import OpenBooleanNetwork, BooleanNode

class SelectiveBooleanNetwork(OpenBooleanNetwork):
    '''
    A BN that is trained to associate 1 or more sets of input values to a specific attractor
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__attractors_input_map = defaultdict(type(None))

    @property
    def attractors_input_map(self):
        return self.__attractors_input_map

    @attractors_input_map.setter
    def attractors_input_map(self, mapping: dict):
        self.__attractors_input_map = defaultdict(type(None), **mapping)
    
    def to_json(self):
        __json = super().to_json()

        __json.update({
            "attractors_input_map": self.attractors_input_map
        })

        return __json

    @staticmethod
    def from_json(json:dict):
        
        nodes = [BooleanNode.from_json(node) for node in json['nodes']]
        bnsel = SelectiveBooleanNetwork(nodes, json['inputs'], json['outputs'])
        bnsel.attractors_input_map = json['attractors_input_map']


        return  bnsel
