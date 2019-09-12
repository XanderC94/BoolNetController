import unittest
import bncontroller.stubs.comparators as cmp
from bncontroller.boolnet.structures import BooleanNetwork
from bncontroller.search.utils import edit_boolean_network, bn_scramble_strategy
from bncontroller.stubs.behaviour.utils import template_behaviour_generator

class TestParametricVNS(unittest.TestCase):

    def test_default_scramble_strategy(self):

        bn = template_behaviour_generator(5, 2, 0.5, 0.0, 1, 0).new()
        bn_copy = BooleanNetwork.from_json(bn.to_json())

        bn_copy, flips = bn_scramble_strategy(bn_copy, 1)

        self.assertFalse(bn.to_json() == bn_copy.to_json())

        bn_copy = edit_boolean_network(bn_copy, flips)

        self.assertTrue(bn.to_json() == bn_copy.to_json())

    def test_tuple_comparator(self):

        t1 = 1,2,3,4,5,6
        t2 = 1,2,3,4,5,6
        t3 = 4,5,6,7,8,9
        t4 = 4,5,6,7

        self.assertFalse(cmp.mixed_ls(t1, t2))
        self.assertFalse(cmp.mixed_ls(t3, t1))
        self.assertTrue(cmp.mixed_eq(t1, t2))
        self.assertTrue(cmp.mixed_gr(t3, t1))
        self.assertTrue(cmp.mixed_gr(t3, t4))
       
        