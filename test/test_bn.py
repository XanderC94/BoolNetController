import unittest, time
from bncontroller.boolnet.structures import BooleanNetwork
from bncontroller.boolnet.utils import binstate
from bncontroller.stubs.bn import bn_generator
from bncontroller.search.parametric import default_scramble_strategy

class TestBooleanNetwork(unittest.TestCase):

    def test_bn_copy(self):
        bn = bn_generator(5, 2, 0.5, 1, 0)[0].new()

        bn_copy = BooleanNetwork.from_json(bn.to_json())

        self.assertTrue(bn.to_json(), bn_copy.to_json())

    def test_ebnf(self):
        bn = bn_generator(5, 2, 0.5, 1, 0)[0].new()

        bn_copy = BooleanNetwork.from_json(bn.to_json())

        self.assertTrue(bn.to_ebnf(), bn_copy.to_ebnf())

    def test_bn_update(self):
        bn = bn_generator(5, 2, 0.5, 1, 0)[0].new()

        bn_copy = BooleanNetwork.from_json(bn.to_json())

        matching_states = []

        for _ in range(10):
            
            s1 = binstate(bn.update())
            s2 = binstate(bn_copy.update())

            matching_states.append(s1 == s2)

        self.assertTrue(all(matching_states))

    def test_atm_caching(self):

        bn = bn_generator(5, 2, 0.5, 1, 0)[0].new()

        t = time.perf_counter()

        for _ in range(10):
            bn.get_atm(from_cache=True)
        
        t_cache = time.perf_counter() - t

        t = time.perf_counter()

        for _ in range(10):
            bn.get_atm(from_cache=True)
            bn, *_ = default_scramble_strategy(bn, 1)
        
        t_cache_w_changes = time.perf_counter() - t

        t = time.perf_counter()

        for _ in range(10):
            bn.get_atm()
        
        t_creation = time.perf_counter() - t

        self.assertTrue(t_cache < t_creation and t_cache <  t_cache_w_changes)

