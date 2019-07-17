from bncontroller.boolnet.structures import OpenBooleanNetwork, BooleanNode

class BoolNetSelector(OpenBooleanNetwork):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.get_atm()

        self.__attractors_mapping = list()

    @property
    def attractors_input_map(self):
        return self.__attractors_mapping

    @attractors_input_map.setter
    def attractors_input_map(self, mapping):
        self.__attractors_mapping = mapping

    
    def to_json(self):
        __json = super().to_json()

        __json.update({
            "attractors_input_map": self.attractors_input_map
        })

        return __json

    @staticmethod
    def from_json(json:dict):
        
        nodes = [BooleanNode.from_json(node) for node in json['nodes']]
        bnsel = BoolNetSelector(nodes, json['inputs'], json['outputs'])
        bnsel.attractors_input_map = list(tuple(i) for i in json['attractors_input_map'])

        return  bnsel
