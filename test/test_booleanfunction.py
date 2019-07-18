import unittest
from bncontroller.boolnet.boolean import Boolean
from bncontroller.boolnet.function import BooleanFunction

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
                    'params':{'0':False, '1':False},
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':{'0':False, '1':True},
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':{'0':True, '1':False},
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':{'0':True, '1':True},
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
                    'params':{'0':False, '1':False},
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':{'0':False, '1':True},
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':{'0':True, '1':False},
                    'hold':{'0':1.0, '1':0.0}
                },
                {
                    'params':{'0':True, '1':True},
                    'hold':{'0':0.0, '1':1.0}
                }
            ]
        }
        self.assertEqual(dbf, BooleanFunction.from_json(dbf_json))