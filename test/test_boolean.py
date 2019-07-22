import unittest, copy
from bncontroller.boolnet.boolean import Boolean

class TestBoolean(unittest.TestCase):

    def test_creation(self):
        b1 = Boolean(True)
        b2 = Boolean(0.5)

        self.assertIsInstance(b1.bias, float)
        self.assertIsInstance(b2.bias, float)
        self.assertTrue(b1())
        self.assertIsInstance(b1(), int)
        self.assertIsInstance(b1(bool), bool)
        self.assertIsInstance(b2(), int)
        self.assertIsInstance(b2(bool), bool)
    
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
        self.assertIsInstance(b1(), int)
        self.assertIsInstance(b1(bool), bool)
        self.assertIsInstance(b2(), int)
        self.assertIsInstance(b2(bool), bool)
    
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