import unittest, copy, random
from boolean import Boolean
from booleanfunction import BooleanFunction

class BNUnitTesting(unittest.TestCase):

    def test_creation(self):
        b1 = Boolean(True)
        b2 = Boolean(0.5)

        self.assertIsInstance(b1.bias(), float)
        self.assertIsInstance(b2.bias(), float)
        self.assertTrue(b1())
        self.assertIsInstance(b1(), bool)
        self.assertIsInstance(b2(), bool)
    
    def test_modification(self):
        b1 = Boolean(True)
        b2 = Boolean(0.5)

        tmp1 = copy.deepcopy(b1)
        tmp2 = copy.deepcopy(b2)

        b1.set_bias(0.5)
        b2.set_bias(False)

        self.assertIsInstance(b1.bias(), float)
        self.assertIsInstance(b2.bias(), float)
        self.assertNotEqual(b1.bias(), tmp1.bias())
        self.assertNotEqual(b2.bias(), tmp2.bias())
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

    
    def test_modification(self):
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
            'k':2,
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

        print(dbf.to_json())

        self.assertDictEqual(dbf.to_json(), dbf_json)

    def test_deserialization(self):
        dbf = BooleanFunction(2, result_generator=lambda *args: Boolean(args[0] and args[1]))
        dbf_json = {
            'k':2,
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


if __name__ == "__main__":
    unittest.main()