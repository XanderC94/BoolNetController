from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.ntree.ntstructures import NTree
from bncontroller.boolnet.tes import bn_to_tes
import bncontroller.boolnet.eval.utils as utils
from bncontroller.sim.logging.logger import staticlogger as logger

###############################################################################

def default_evaluation_strategy(bn: OpenBooleanNetwork, target_tes: NTree, thresholds: list) -> float:

    tes = bn_to_tes(bn, thresholds)
    return utils.tes_distance(tes, target_tes)

def default_scramble_strategy(bn: OpenBooleanNetwork, n_flips:int, excluded:set):

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
    return minimize < maximize

###############################################################################

def parametric_vns(
        bn: OpenBooleanNetwork,
        evaluate=lambda bn: default_evaluation_strategy(bn, NTree.empty(), []),
        scramble=lambda bn, nf, e: default_scramble_strategy(bn, nf, e),
        compare=lambda minimize, maximize: default_compare_strategy(minimize, maximize),
        min_target=0.0,
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
            (evaluation output matches in some way the min_target parameter)
            and to choose if keeping or discarting changes to the bn.
            By default is: minimize < maximize, 
            that is if the value to be minimized is less than the value to be maximized.
        * min_target -> the value of the evaluation strategy at which the algorithm will stop
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

    dist = evaluate(bn)

    max_flips = sum(2**n.arity for n in bn.nodes if n not in bn.input_nodes)

    it = 0
    excluded = set()
    n_stalls = 0
    n_flips = 1
    n_stagnation = 0

    while it < max_iters and compare(min_target, dist):
        
        bn, flips, excluded = scramble(bn, n_flips, excluded)

        new_dist = evaluate(bn)

        logger.info(
            'it:', it, 
            'flips:', len(flips), '/', n_flips, 
            'stalls:', n_stalls,
            'stagnation: ', n_stagnation,
            'dist --',
            'old:', dist,  
            'new:', new_dist
        )
        
        if compare(new_dist, dist):

            n_stagnation = 0
            n_stalls = 0
            n_flips = 1
            dist = new_dist

        else:

            bn = utils.edit_boolean_network(bn, flips)

            n_stagnation += 1
            n_stalls += 1
            
            if max_stagnation > 0 and n_stagnation >= max_stagnation:
                it = max_iters

            if max_stalls > 0 and n_stalls >= max_stalls:
                n_stalls = 0
                n_flips += 1
                
                if n_flips > max_flips:
                    it = max_iters
        
        it += 1

    return bn
