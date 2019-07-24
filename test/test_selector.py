import unittest
import random
from pathlib import Path

import bncontroller.stubs.selector.tests as constraints
from bncontroller.stubs.selector.utils import template_selector_generator, noisy_update
from bncontroller.boolnet.utils import search_attractors, random_neighbors_generator, binstate
from bncontroller.boolnet.atm import AttractorsTransitionMatrix as ATM
from bncontroller.boolnet.structures import BooleanNetwork, BooleanNode, OpenBooleanNetwork
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.boolnet.function import BooleanFunction
from bncontroller.collectionslib.utils import flat, transpose
from bncontroller.jsonlib.utils import read_json

class TestBooleNetSelectorGenerator(unittest.TestCase):

    def test_attractor_search(self):
        
        states = [
            
            [0,1,0,1,0,0],
            [1,1,0,1,0,1],
            [0,0,0,0,0,0],
            [1,1,1,1,0,0],
            [0,1,0,1,0,1],
            [1,1,1,1,0,0],
            [0,1,0,1,0,1],
            [1,1,1,1,0,0],
            [0,1,0,1,0,1],
            [1,1,0,1,0,0],
            [1,1,0,1,0,1],
            [1,1,0,1,0,1],
            [1,1,0,1,0,1],
            [0,1,1,1,0,0],
            [1,1,1,1,0,0],
            [0,1,0,1,0,1],
        ]

        attractors = {
            'a0': [
                [1,1,1,1,0,0],
                [0,1,0,1,0,1],
            ],
            'a1': [
                [1,1,0,1,0,1],
            ],
        }

        res = search_attractors(states, attractors)

        labels, ns, lmaxs, lmins = transpose(res)

        self.assertTrue('a0' in labels and 'a1' in labels)

        ia0 = list(labels).index('a0')
        ia1 = list(labels).index('a1')

        self.assertTrue(ns[ia0] == 2)
        self.assertTrue(ns[ia1] == 2)

        self.assertTrue(lmaxs[ia0] == 3)
        self.assertTrue(lmaxs[ia1] == 3)

        self.assertTrue(lmins[ia0] == 1)
        self.assertTrue(lmins[ia1] == 1)
    
    def test_bn_noisy_run(self):

        N, K, P, Q, I, O = 5, 2, 0.5, 0.0, 1, 0
        g = template_selector_generator(N, K, P, Q, I, O)
        bn = g.new_selector()
        atm = bn.atm

        states = noisy_update(
            bn, 
            steps=max(map(len, atm.attractors))*len(bn)*10, 
            noise_p=0.2
            # input_step=max(map(len, atm.attractors)) * 2,
        )

        self.assertTrue(len(states) == max(map(len, atm.attractors))*len(bn)*10)
        self.assertTrue(all(x == 5 for x in map(len, states)))

    def __get_attractor_landscape_bn(self):

        def A(*args):
            return args[0] or args[1]

        def B(*args):
            return args[0] or args[1]

        def C(*args):
            return args[0] and args[1]

        def D(*args):
            return not(args[0]) and args[1]

        return BoolNetSelector(
            [
                BooleanNode('0', predecessors=['2', '3'], bf=BooleanFunction(2, result_generator=A)), # A
                BooleanNode('1', predecessors=['0', '1'], bf=BooleanFunction(2, result_generator=B)), # B
                BooleanNode('2', predecessors=['0', '1'], bf=BooleanFunction(2, result_generator=C)), # C
                BooleanNode('3', predecessors=['2', '3'], bf=BooleanFunction(2, result_generator=D))  # D
            ],
            input_nodes=['0']
        )

    def test_ebnf_generation(self):
        
        bn = self.__get_attractor_landscape_bn()

        correct_ebnf = Path('.\\test\\attractor_landscape_paper.bn').read_text()

        correct_ebnf = str(correct_ebnf).replace('A', 'n0')
        correct_ebnf = str(correct_ebnf).replace('B', 'n1')
        correct_ebnf = str(correct_ebnf).replace('C', 'n2')
        correct_ebnf = str(correct_ebnf).replace('D', 'n3')

        self.assertTrue(bn.to_ebnf() == correct_ebnf)
        self.assertTrue(bn.atm.tableau == ATM(correct_ebnf).tableau)

    def test_atm_generation(self):
        
        atms = []

        N, K, P, Q, I, O = 5, 2, 0.5, 0.0, 1, 0

        g1 = template_selector_generator(
            N, K, P, Q, I, O, 
            F=lambda a,b: random_neighbors_generator(a, b, self_loops=True)
        )
        
        for _ in range(100):
            bn = g1.new_selector()
            atms.append(bn.atm.dtableau)
            # print(bn.atm.tableau)
        
        self.assertTrue(all(
            [
                sum(
                    a == b
                    for b in atms
                ) <= 1 + int(len(atms) / 2)
                for a in atms
            ]
        ))

        atms.clear()

        # print('#######################################################')

        g2 = template_selector_generator(N, K, P, Q, I, O)
        
        for _ in range(100):
            bn = g2.new_selector()
            atms.append(bn.atm.dtableau)
            # print(bn.atm.tableau)
        
        self.assertTrue(all(
            [
                sum(
                    a == b
                    for b in atms
                ) <= 1 + int(len(atms) / 2)
                for a in atms
            ]
        ))

        atms.clear()
    
    def test_bnselector_atm_similarity(self):
        
        N, K, P, Q, I, O = 5, 2, 0.5, 0.0, 1, 0

        bnsg = template_selector_generator(N, K, P, Q, I, O)

        atms = []

        for _ in range(1000):
            s = bnsg.new_selector()
            if constraints.test_attractors_number(s, 2):
                atms.append(s.atm.tableau)
                # print(s.atm.tableau)
        
        flatatm = [flat(list(a), to=tuple) for a in atms]

        # print(len(set(flatatm)))
        
        self.assertTrue(all([
                sum(
                    a == b
                    for b in atms
                ) <= 1 + int(len(atms) / 2)
                for a in atms
            ]))

        ############################################################

        atms2 = []

        for _ in range(1000):
            s = bnsg.new_selector()
            if constraints.test_attractors_number(s, 2):
                atms2.append(s.atm.tableau)
                # print(s.atm.tableau)
        
        flatatm2 = [flat(list(a), to=tuple) for a in atms2]

        # print(len(set(flatatm2)))

        self.assertFalse(flatatm == flatatm2)

    def test_selector_constraint_1(self):
        bn = BoolNetSelector.from_json(read_json('./test/bn_for_test.json'))
        self.assertTrue(constraints.test_attractors_number(bn, 2))
        self.assertFalse(constraints.test_attractors_number(bn, 4))

    def test_selector_constraint_2(self):
        bn = BoolNetSelector.from_json(read_json('./test/bn_for_test.json'))
        self.assertTrue(constraints.test_attractors_transitions(bn, {
            'a0':{'a1': 0.3},
            'a1':{'a0': 0.3},
        }))

    def test_selector_constraint_3(self):
        bn = BoolNetSelector.from_json(read_json('./test/bn_for_test.json'))
        self.assertTrue(constraints.test_bn_state_space_omogeneity(bn, 0.1))
    
    def test_selector_constraint_4(self):
        bn = BoolNetSelector.from_json(read_json('./test/bn_for_test.json'))
        self.assertTrue(constraints.test_attraction_basins(bn, 5))
