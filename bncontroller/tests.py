import unittest, copy, random, apted
from bncontroller.boolnet.boolean import Boolean
from bncontroller.boolnet.bfunction import BooleanFunction
from bncontroller.ntree.ntstructures import NTree
from bncontroller.ntree.ntutils import tree_edit_distance, tree_histogram_distance, tree_level_arities

class TestBoolean(unittest.TestCase):

    def test_creation(self):
        b1 = Boolean(True)
        b2 = Boolean(0.5)

        self.assertIsInstance(b1.bias, float)
        self.assertIsInstance(b2.bias, float)
        self.assertTrue(b1())
        self.assertIsInstance(b1(), bool)
        self.assertIsInstance(b2(), bool)
    
    def test_edit(self):
        b1 = Boolean(True)
        b2 = Boolean(0.5)

        tmp1 = copy.deepcopy(b1)
        tmp2 = copy.deepcopy(b2)

        b1.bias = 0.5
        b2.bias = False

        self.assertIsInstance(b1.bias, float)
        self.assertIsInstance(b2.bias, float)
        self.assertNotEqual(b1.bias, tmp1.bias)
        self.assertNotEqual(b2.bias, tmp2.bias)
        self.assertFalse(b2())
        self.assertIsInstance(b1(), bool)
        self.assertIsInstance(b2(), bool)
    
    def test_evaluation(self):
        b1 = Boolean(True)
        b2 = Boolean(0.5)

        self.assertTrue(b1())
        self.assertIn(b2(), [True, False])
    
    def test_serialization(self):
        b1 = Boolean(True)
       
        self.assertDictEqual(b1.to_json(), {'0':0.0, '1':1.0})
    
    def test_deserialization(self):
        b1 = Boolean(True)
       
        self.assertEqual(Boolean.from_json({'0':0.0, '1':1.0}), b1)

class TestBooleanFunction(unittest.TestCase):

    def test_creation(self):
        dbf = BooleanFunction(3)
                
        self.assertIsInstance(dbf[(True, True, False)], Boolean)

    
    def test_edit(self):
        dbf = BooleanFunction(3)
        
        v = dbf[(True, True, False)]
        dbf[(True, True, False)] = True
        self.assertIsInstance(dbf[(True, True, False)], Boolean)
        self.assertEqual(dbf[(True, True, False)], Boolean(True))
        self.assertEqual(dbf[(True, True, False)], True)
        self.assertEqual(dbf[(True, True, False)], 1.0)
        self.assertEqual(dbf[(True, True, False)], 1)

    
    def test_evaluation(self):
        dbf = BooleanFunction(3)
        
        dbf[(True, True, False)] = True

        self.assertTrue(dbf((True, True, False)))
    
    def test_serialization(self):
        dbf = BooleanFunction(2, result_generator=lambda *args: Boolean(args[0] and args[1]))

        dbf_json = {
            'arity':2,
            'truth_table':[
                {
                    'params':[False, False],
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':[False, True],
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':[True, False],
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':[True, True],
                    'hold':{'0':0.0, '1':1.0}
                }
                
            ]
        }

        self.assertDictEqual(dbf.to_json(), dbf_json)

    def test_deserialization(self):
        dbf = BooleanFunction(2, result_generator=lambda *args: Boolean(args[0] and args[1]))
        dbf_json = {
            'arity':2,
            'truth_table':[
                {
                    'params':[True, True],
                    'hold':{'0':0.0, '1':1.0}
                },
                {
                    'params':[True, False],
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':[False, True],
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':[False, False],
                    'hold':{'0':1.0, '1':0.0}
                }
            ]
        }
        self.assertEqual(dbf, BooleanFunction.from_json(dbf_json))

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

if __name__ == "__main__":
    unittest.main()