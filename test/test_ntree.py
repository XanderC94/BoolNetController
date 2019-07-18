import unittest, apted
from bncontroller.boolnet.boolean import Boolean
from bncontroller.ntree.structures import NTree
from bncontroller.ntree.utils import tree_edit_distance, tree_histogram_distance, tree_level_arities

class TestNTree(unittest.TestCase):
    
    def test_creation(self):
        t1 = NTree(1, [ 
            NTree(2, [], 2)
        ], 1)

        self.assertEqual(t1.label, 1)
        self.assertEqual(t1.children[0].label, 2)
        self.assertEqual(t1.value, 1)
        self.assertEqual(t1.children[0].value, 2)
        # self.assertEqual(t1.depth(), 0)
        # self.assertEqual(t1.children[0].depth(), 1)
        # self.assertEqual(t1, t1.children[0].parent())
    
    def test_edit(self):
        t1 = NTree(1, [], 1)

        self.assertEqual(len(t1), 0)

        t1.value = Boolean(True)

        self.assertIsInstance(t1.value, Boolean)

        t1.children = [
            NTree(2, [], 2),
            NTree(3, [], 3)
        ]

        self.assertEqual(len(t1), 2)

    def test_serialization(self):
        t1 = NTree(1, [  
            NTree(2, [
                NTree(3, [], 3)
            ], 2) 
        ], 1)

        t1_json = {
            'label': 1, 
            'children': [
                {
                    'label': 2, 
                    'children': [
                        {
                            'label': 3, 
                            'children': [], 
                            'value': 3
                        }
                    ], 
                    'value': 2
                }
            ], 
            'value': 1
        }

        # print(t1.to_json())

        self.assertDictEqual(t1.to_json(), t1_json)
    
    def test_deserialization(self):
        t1 = NTree(1, [  
            NTree(2, [
                NTree(3, [], 3)
            ], 2) 
        ], 1)

        t1_json = {
            'label': 1, 
            'children': [
                {
                    'label': 2, 
                    'children': [
                        {
                            'label': 3, 
                            'children': [], 
                            'value': 3
                        }
                    ], 
                    'value': 2
                }
            ], 
            'value': 1
        }

        # print(NTree.from_json(t1_json))

        self.assertEqual(t1, NTree.from_json(t1_json))

class TestNTreeUtils(unittest.TestCase):

    def test_edit_distance(self):
        t1 = NTree(1, [  
            NTree(2, [
                NTree(3, [], 3)
            ], 2) 
        ], 1)

        t2 = NTree(1, [ 
                NTree(2, [], 2), 
                NTree(3, [
                    # NTree(4, [], 4)
                ], 3) 
            ], 1)
        
        # Remove Node + Add Node = 2 ops

        self.assertEqual(apted.APTED(t1, t2).compute_edit_distance(), 2)

    def test_histogram_distance(self):
        t1 = NTree(1, [ 
            NTree(2, [
                NTree(3, [], 3)
            ], 2) 
        ], 1)
        # l0: [1k -> 1n], l1: [1k -> 1n], l2: [0k -> 1n]

        t2 = NTree(1, [ 
                NTree(2, [], 2), 
                NTree(3, [
                    # NTree(4, [], 4)
                ], 3) 
            ], 1)
        # l0: [2k -> 1n], l1: [0k -> 2n]

        self.assertEqual(tree_histogram_distance(t1, t2), 6)
    
    def test_level_arities(self):

        t1 = NTree(1, [ 
            NTree(2, [
                NTree(3, [], 3)
            ], 2) 
        ], 1)

        t2 = NTree(1, [ 
                NTree(2, [], 2), 
                NTree(3, [
                    # NTree(4, [], 4)
                ], 3) 
            ], 1)


        self.assertDictEqual(tree_level_arities([t1]), {1:1})
        self.assertDictEqual(tree_level_arities(t1.children), {1:1})
        self.assertDictEqual(tree_level_arities(t1.children[0].children), {0:1})

        self.assertDictEqual(tree_level_arities([t2]), {2:1})
        self.assertDictEqual(tree_level_arities(t2.children), {0:2})