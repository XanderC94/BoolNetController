from collections import namedtuple
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.ntree.ntstructures import NTree
from bncontroller.boolnet.tes import bn_to_tes
import bncontroller.boolnet.eval.utils as utils

###############################################################################

def default_evaluation_strategy(bn: OpenBooleanNetwork, target_tes: NTree, thresholds: list) -> float:

    tes = bn_to_tes(bn, thresholds)
    return utils.tes_distance(tes, target_tes)

def default_scramble_strategy(bn: OpenBooleanNetwork, n_flips:int, excluded:set={}):
    '''
    Default scrambling strategy for vns algorithm.
    Scrambling = flips generation + boolean network edit

    returns the modified bn, the applied flips and their hashset
    '''
    terminal_nodes = list(
        n.label 
        for n in bn.nodes 
        if n.label not in bn.output_nodes and not any(n.label in x.predecessors for x in bn.nodes)
    )

    do_not_flip = excluded.union(set(map(hash, bn.input_nodes + terminal_nodes)))

    flips = utils.generate_flips(bn, n_flips, excluded=do_not_flip, flip_map=hash)
    bn = utils.edit_boolean_network(bn, flips)

    return bn, flips, set(map(hash, flips))

def default_compare_strategy(minimize, maximize):
    '''
    Default compare strategy for vns algorithm.

    return minimize < maximize
    '''
    return minimize < maximize

###############################################################################

VNSPublicContext = namedtuple(
        'VNSPublicContext',  
        ["it", "score", "n_flips", "n_stalls", "stagnation"]
    )

class VNSContext(object):

    def __init__(self, 
            it = 0,
            n_stalls = 0,
            n_flips = 0,
            stagnation = 0,
            score = float('-inf')):

        self.it = it
        self.n_stalls = n_stalls
        self.n_flips = n_flips
        self.stagnation = stagnation
        self.score = score
        self.stop = False
        self.excluded = set()
    
    @property
    def public(self):
        return VNSPublicContext(
            it=self.it,
            score=self.score,
            n_flips=self.n_flips,
            n_stalls=self.n_stalls,
            stagnation=self.stagnation
        )

# class VNSParams(object):

#     def __init__(self, 
#             target_score=0.0,
#             min_flips=1,
#             max_flips=-1,
#             max_iters=10000, 
#             max_stalls=-1,
#             max_stagnation=2500):

#         self.target_score=target_score,
#         self.min_flips=min_flips,
#         self.max_flips=max_flips,
#         self.max_iters=max_iters, 
#         self.max_stalls=max_stalls,
#         self.max_stagnation=max_stagnation 

################################################################################

def parametric_vns(
        bn: OpenBooleanNetwork,
        compare=lambda minimize, maximize: default_compare_strategy(minimize, maximize),
        evaluate=lambda bn, vns: default_evaluation_strategy(bn, NTree.empty(), []),
        scramble=lambda bn, nf, e: default_scramble_strategy(bn, nf, e),
        tidy=lambda bn, flips: utils.edit_boolean_network(bn, flips),
        target_score=0.0,
        min_flips=1,
        max_flips=-1,
        max_iters=10000, 
        max_stalls=-1,
        max_stagnation=2500):
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
            By default is: minimize < maximize, 
            that is if the value to be minimized is less than the value to be maximized.
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

    vns = VNSContext(n_flips = min_flips)

    vns.score = evaluate(bn, vns.public)

    if bn is not None and max_stalls >= 0 and max_flips <= 0:
        max_flips = sum(2**n.arity for n in bn.nodes) 

    check_param = lambda a, b: b >= 0 and a >= b
    
    while vns.it < max_iters and not vns.stop and compare(target_score, vns.score):

        bn, flips, vns.excluded = scramble(bn, vns.n_flips, vns.excluded)

        new_score = evaluate(bn, vns.public)
        
        if compare(new_score, vns.score):

            vns.stagnation = 0
            vns.n_stalls = 0
            vns.n_flips = min_flips
            vns.score = new_score

        else:

            bn = tidy(bn, flips)

            vns.stagnation += 1
            vns.n_stalls += 1
            
            if check_param(vns.n_stalls, max_stalls):
                vns.n_stalls = 0
                vns.n_flips += 1

            vns.stop = (
                check_param(vns.stagnation, max_stagnation) 
                or check_param(vns.n_flips, max_flips + 1)
            )
        
        vns.it += 1

    return bn, vns.public
