'''
Variable Neighborhood Search (Stochastic Descent Algorithm) template
'''
from typing import Callable, TypeVar
from collections import namedtuple
from bncontroller.search.utils import ScrambleOutput

S = TypeVar('S')
C = TypeVar('C')

###############################################################################

VNSPublicContext = namedtuple(
    'VNSPublicContext',  
    ["it", "score", "n_flips", "n_stalls", "stagnation"]
)

class VNSContext(object):
    '''
    Function Context of VNS algorithm
    '''
    def __init__(self, 
            it = 0,
            n_stalls = 0,
            n_flips = 0,
            stagnation = 0,
            score = None):

        self.it = it
        self.n_stalls = n_stalls
        self.n_flips = n_flips
        self.stagnation = stagnation
        self.score = score
        self.stop = False
        self.flips = set()
    
    @property
    def public(self):
        return VNSPublicContext(
            it=self.it,
            score=self.score,
            n_flips=self.n_flips,
            n_stalls=self.n_stalls,
            stagnation=self.stagnation
        )

class VNSParameters(object):
    '''
    Variable Neighborhood Search Parameters holder
    '''
    def __init__(self, 
        target_score=0.0,
        min_flips=1,
        max_flips=-1,
        max_iters=10000, 
        max_stalls=-1,
        max_stagnation=2500):

        self.target_score = target_score
        self.min_flips = min_flips
        self.max_flips = max_flips
        self.max_iters = max_iters
        self.max_stalls = max_stalls
        self.max_stagnation = max_stagnation

VNSOutput = namedtuple('VNSOutput', ['solution', 'context'])

class VariableNeighborhoodSearch(
        Callable[[S, VNSParameters], VNSOutput]
    ):

    '''
    Metaheuristic technique highly inspired by the Variable Neighbourhood Search (VNS) and 
    proposed in

        Nenad Mladenovic and Pierre Hansen. Variable neighborhood search.
        Computers & Operations Research, 24(11):1097–1100, 1997

    Parameters:

        * bn -> the OpenBooleanNetwork to be improved
        * scramble -> the strategy to apply that changes the bn at each iteration
        * evaluate -> the given strategy to evaluate the scrambled bn at each iteration
        * compare -> the given strategy to be applied to the output of the evaluation strategy.
            This strategy is both applied to check algorithm termination 
            (evaluation output matches in some way the target_score parameter)
            and to choose if keeping or discarting changes to the bn.
            By default is: old < new (score minimization).
        * target_score -> the value of the evaluation strategy at which the algorithm will stop
        * max_iters -> global max number of iterations of the stochastic descent
        * max_stalls -> max number of iterations without improvement. 
            When reached it increases the number of flips by 1.
            It resets if a better Bn is found.
            If set to -1 it won't be considered 
            and the algorithm will behave similarly to an Adaptive Walk (1 flip).
        * max_stagnations -> global max number of iteration without improvements.
            When reached the algorithm will stop.
            It resets if a better Bn is found.
            If set to -1 it won't be considered
    '''

    def __init__(self, 
            sol_evaluator: Callable[[S, VNSPublicContext], C],
            sols_comparator: Callable[[C, C], bool],
            sol_scrambler: Callable[[S, int, set], ScrambleOutput],
            sol_tidier: Callable[[S, set], S]):

        self.__evaluate = sol_evaluator
        self.__compare = sols_comparator
        self.__scramble = sol_scrambler
        self.__tidy = sol_tidier

    def __check_params(self, a, b):
        return b >= 0 and a >= b

    def __call__(self, sol: object, params: VNSParameters):

        ctx = VNSContext(n_flips=params.min_flips)

        ctx.score = self.__evaluate(sol, ctx.public)

        while (
                ctx.it < params.max_iters
                and not ctx.stop
                and not self.__compare(ctx.score, params.target_score)
            ):

            sol, ctx.flips = self.__scramble(sol, ctx.n_flips, ctx.flips)

            new_score = self.__evaluate(sol, ctx.public)

            if self.__compare(new_score, ctx.score):

                ctx.stagnation = 0
                ctx.n_stalls = 0
                ctx.n_flips = params.min_flips
                ctx.score = new_score

            else:

                sol = self.__tidy(sol, ctx.flips)

                ctx.stagnation += 1
                ctx.n_stalls += 1

                if self.__check_params(ctx.n_stalls, params.max_stalls):
                    ctx.n_stalls = 0
                    ctx.n_flips += 1

                ctx.stop = (
                    self.__check_params(ctx.stagnation, params.max_stagnation) 
                    or self.__check_params(ctx.n_flips, params.max_flips + 1)
                )

            ctx.it += 1

        return VNSOutput(solution=sol, context=ctx.public)
