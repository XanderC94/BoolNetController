import unittest
from bncontroller.jsonlib.utils import jsonrepr, objrepr
from bncontroller.type.comparators import seq_compare

class Foo1(object):

    def __init__(self):
        pass


class TestJSONlib(unittest.TestCase):
    
    def test_jsonrepr(self):
        pass
    
    def test_objrepr(self):
        
        jsondict = {
            'a': 1,
            'b': list()
        }

        obj = objrepr(jsondict, dict)
        
        self.assertTrue(isinstance(obj, dict))

        pass