from bncontroller.json.utils import jsonrepr, objrepr, Jsonkin
from apted.helpers import Tree
from apted import APTED

class NTree(Tree, Jsonkin):
    """
    A linked objects representation of a nTree wrapping the Tree implementation
    from apted library for backward compatibility.
    Each node can hold any different number of children.
    """
    def __init__(self, label, children: list, value):
        super().__init__(label, *children)
        self.__child_are_ntrees = all(map(lambda n: isinstance(n, NTree), children))
        # self.__depth = 0

        if self.__child_are_ntrees:
            for child in self.children: 
                child.parent = self

        self.__value = value
        self.__parent = None

    @property
    def parent(self):
        return self.__parent
    
    @property
    def label(self):
        return self.name

    @property
    def value(self):
        return self.__value

    # def depth(self):
    #     return self.__depth

    @label.setter
    def label(self, new_label):
        self.name = new_label

    @value.setter
    def value(self, value):
        self.__value = value

    # def set_depth(self, depth):
    #     self.__depth = depth
    #     if self.__child_are_trees:
    #         for child in self.children:
    #             child.set_depth(self.__depth + 1)
    
    @parent.setter
    def parent(self, parent):
        self.__parent = parent
    #     self.set_depth(self.parent().depth() + 1)

    def is_leaf(self):
        return len(self) == 0

    def is_empty(self):
        return self.label == None

    def is_not_empty(self):
        return not self.is_empty()

    @staticmethod
    def empty():
        return NTree(None, [], None)

    def to_json(self) -> dict:

        return {
                'label': jsonrepr(self.label), 
                'children': list(map(lambda c: jsonrepr(c), self.children)), 
                'value': jsonrepr(self.value),
                # 'parent': self.parent()
                # 'depth': self.depth()
            }

    @staticmethod
    def from_json(json:dict):

        return NTree(
            json['label'], 
            list(NTree.from_json(c) for c in json['children']), 
            json['value']
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