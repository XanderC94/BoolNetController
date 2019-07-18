import unittest
from bncontroller.stubs.bn import bn_generator
from bncontroller.stubs.selector.utils import noisy_run
from bncontroller.boolnet.utils import search_attractors

class TestBooleNetSelectorGenerator(unittest.TestCase):

    def test_attractor_search(self):
        
        states = [
            [0,1,0,1,0,0],
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
            [0,1,0,1,0,0]
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
        
        self.assertTrue('a0' in res and 'a1' in res)
    
    def test_bn_noisy_run(self):

        g, I, O = bn_generator(5, 2, 0.5, 1, 0)
        bn = g.new_obn(I, O)
        atm = bn.get_atm()

        states = noisy_run(
            bn, 
            max(map(len, atm.attractors))*len(bn)*10, 
            input_step=max(map(len, atm.attractors)) * 2,
        )

        self.assertTrue(len(states) == max(map(len, atm.attractors))*len(bn)*10)
        self.assertTrue(all(x == 5 for x in map(len, states)))
        pass

    def test_attractor_space_omogeneity(self):
        pass

    def test_selector_consistency(self):
        pass