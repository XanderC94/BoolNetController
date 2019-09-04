import unittest
import time
from bncontroller.boolnet.structures import BooleanNetwork, BooleanNode, OpenBooleanNetwork
from bncontroller.boolnet.function import BooleanFunction
from bncontroller.boolnet.utils import binstate
from bncontroller.boolnet.atm import AttractorsTransitionMatrix as ATM
from bncontroller.stubs.controller.utils import template_controller_generator
from bncontroller.search.utils import bn_scramble_strategy

class TestBooleanNetwork(unittest.TestCase):

    def test_bn_copy(self):
        bn = template_controller_generator(5, 2, 0.5, 0.0, 1, 0).new()

        bn_copy = BooleanNetwork.from_json(bn.to_json())

        self.assertTrue(bn.to_json(), bn_copy.to_json())

    def test_ebnf(self):
        bn = template_controller_generator(5, 2, 0.5, 0.0, 1, 0).new()

        bn_copy = BooleanNetwork.from_json(bn.to_json())

        self.assertTrue(bn.to_ebnf(), bn_copy.to_ebnf())

    def test_bn_update(self):
        bn = template_controller_generator(5, 2, 0.5, 0.0, 1, 0).new()

        bn_copy = BooleanNetwork.from_json(bn.to_json())

        matching_states = []

        for _ in range(10):
            
            s1 = binstate(bn.update())
            s2 = binstate(bn_copy.update())

            matching_states.append(s1 == s2)

        self.assertTrue(all(matching_states))

    def test_atm(self):

        bn = template_controller_generator(5, 2, 0.5, 0.0, 1, 0).new()

        atm = bn.atm

        for row in atm.tableau:
            s = sum(row)
            print(s)
            self.assertTrue(s > 0.98 and s < 1.02)

    def test_atm_caching(self):

        bn = template_controller_generator(5, 2, 0.5, 0.0, 1, 0).new()

        t = time.perf_counter()

        for _ in range(10):
            bn.atm
        
        t_cache = time.perf_counter() - t

        t = time.perf_counter()

        for _ in range(10):
            bn.atm
            bn, *_ = bn_scramble_strategy(bn, 1)
        
        t_cache_w_changes = time.perf_counter() - t

        t = time.perf_counter()

        for _ in range(10):
            ATM(bn.to_ebnf())
        
        t_creation = time.perf_counter() - t

        self.assertTrue(t_cache < t_creation and t_cache <  t_cache_w_changes)

    def test_obn_consistency(self):

        bn = OpenBooleanNetwork(
            [
                BooleanNode('0', predecessors=['1', '3'], bf=BooleanFunction(2)),
                BooleanNode('1', predecessors=['0', '4'], bf=BooleanFunction(2)),
                BooleanNode('2', predecessors=['1', '2'], bf=BooleanFunction(2)),
                BooleanNode('3', predecessors=['3', '4'], bf=BooleanFunction(2)),
                BooleanNode('4', predecessors=['2', '0'], bf=BooleanFunction(2)),
                BooleanNode('5', predecessors=['4', '2'], bf=BooleanFunction(2))
            ],
            input_nodes=['5'],
            output_nodes=[]
        )

        self.assertFalse(bn.is_consistent)

        bn = OpenBooleanNetwork(
            [
                BooleanNode('0', predecessors=['1', '3'], bf=BooleanFunction(2)),
                BooleanNode('1', predecessors=['0', '4'], bf=BooleanFunction(2)),
                BooleanNode('2', predecessors=['1', '2'], bf=BooleanFunction(2)),
                BooleanNode('3', predecessors=['3', '5'], bf=BooleanFunction(2)),
                BooleanNode('4', predecessors=['2', '0'], bf=BooleanFunction(2)),
                BooleanNode('5', predecessors=['4', '2'], bf=BooleanFunction(2))
            ],
            input_nodes=['5'],
            output_nodes=[]
        )

        self.assertTrue(bn.is_consistent)
