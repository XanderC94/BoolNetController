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

def default_compare_strategy(a, b):
    return a < b

###############################################################################

def parametric_vns(
        bn: OpenBooleanNetwork,
        evaluate=lambda bn: default_evaluation_strategy(bn, NTree.empty(), []),
        scramble=lambda bn, nf, e: default_scramble_strategy(bn, nf, e),
        compare=lambda a, b: default_compare_strategy(a, b),
        min_target=0.0,
        max_iters=10000, 
        max_stalls=-1,
        max_stagnation=2500):

    '''
    Metaheuristic technique highly inspired by the Variable Neighbourhood Search (VNS) and 
    proposed in

        Nenad Mladenovic and Pierre Hansen. Variable neighborhood search.
        Computers & Operations Research, 24(11):1097–1100, 1997

    ...
    
    When the number of flip is equal to 1 (and number of max stalls is -1) 
    this algorithm behaves like an Adaptive Walk.
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
