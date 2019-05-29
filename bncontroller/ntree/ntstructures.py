from bncontroller.json_utils import check_to_json_existence
from apted.helpers import Tree
from apted import APTED

class NTree(Tree):
    """
    A linked objects representation of a nTree wrapping the Tree implementation
    from apted library for backward compatibility.
    Each node can hold any different number of children.
    """
    def __init__(self, label, children: list, value):
        super().__init__(label, *children)
        self.__label = label
        self.__child_are_ntrees = all(map(lambda n: isinstance(n, NTree), children))
        # self.__children = children
        # self.__depth = 0

        if self.__child_are_ntrees:
            for child in self.children: 
                child.set_parent(self)

        self.__value = value
        self.__parent = None

    def parent(self):
        return self.__parent
        
    def label(self):
        return self.__label

    def value(self):
        return self.__value

    # def depth(self):
    #     return self.__depth
        
    def set_value(self, value):
        self.__value = value

    # def set_depth(self, depth):
    #     self.__depth = depth
    #     if self.__child_are_trees:
    #         for child in self.children:
    #             child.set_depth(self.__depth + 1)
    
    def set_parent(self, parent):
        self.__parent = parent
    #     self.set_depth(self.parent().depth() + 1)

    def is_leaf(self):
        return len(self) == 0

    def is_empty(self):
        return self.__label == None

    def is_not_empty(self):
        return not self.is_empty()

    @staticmethod
    def empty():
        return NTree(None, [], None)

    def to_json(self) -> dict:

        nid = check_to_json_existence(self.label())
        value = check_to_json_existence(self.value())

        return {
                'label': nid, 
                'children': list(map(lambda c: c.to_json(), self.children)), 
                'value': value,
                # 'parent': self.parent()
                # 'depth': self.depth()
            }

    @staticmethod
    def from_json(json:dict, value_deserializer = lambda t: int(t)):

        return NTree(
            json['label'], 
            list(NTree.from_json(c, value_deserializer) for c in json['children']), 
            value_deserializer(json['value'])
        )

    def __str__(self):
        return str(self.to_json())

    def __len__(self):
        return len(self.children)

    def __eq__(self, that):

        if isinstance(that, NTree):
            return APTED(self, that).compute_edit_distance() == 0
        else:
            return False

############################################################################################

class DNTree(object):
    """
    A dictionary-like implementation of an NTree.
    
    Faster data access and low-level nesting.

    * N: the number of node or a list of node ids
    * K: the (global) number of children of each node (randomly chosen) or 
        a list or dictionary containing the children for each node
    """
    def __init__(self, N, K, V):
        pass

###########################################################################################