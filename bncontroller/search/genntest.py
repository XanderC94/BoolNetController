'''
Generate-and-Test algorithm template class
'''

from typing import Callable

class GenerateNTest(Callable[[int], object]):
    '''
    A simple Generate 'n Test algorithm 
    '''

    def __init__(self, 
        sol_generator: Callable[[], object], 
        sol_test: Callable[[object], object],
        sol_evaluator: Callable[[object], bool]):

        self.__generate = sol_generator
        self.__test = sol_test
        self.__evaluate = sol_evaluator

    def __call__(self, max_iters: int):

        it = 0
        score = None
        sol = None

        while it < max_iters and not self.__evaluate(score):

            sol = self.__generate()
            score = self.__test(sol)
            it += 1

        return sol if self.__evaluate(score) else None
