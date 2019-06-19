from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.ntree.ntstructures import NTree
from bncontroller.boolnet.tes import bn_to_tes
import bncontroller.boolnet.eval.utils as utils

###############################################################################

def default_evaluation_strategy(bn: OpenBooleanNetwork, target_tes: NTree, thresholds: list) -> float:

    tes = bn_to_tes(bn, thresholds)
    return utils.tes_distance(tes, target_tes)

def default_scramble_strategy(bn: OpenBooleanNetwork, n_flips:int, excluded:set):

    do_not_flip = excluded.union(map(hash, bn.input_nodes))
    flips = utils.generate_flips(bn, n_flips, excluded=do_not_flip, flip_map=hash)
    bn = utils.edit_boolean_network(bn, flips)

    return (bn, flips, set(map(hash, flips)))

###############################################################################

def parametric_vns(
        bn: OpenBooleanNetwork,
        evaluate=lambda bn: default_evaluation_strategy(bn, NTree.empty(), []),
        scramble=lambda bn, nf, lf: default_scramble_strategy(bn, nf, lf),
        min_target=0.0,
        max_iters=10000, 
        max_stalls=-1):

    '''
    Metaheuristic technique highly inspired by the Variable Neighbourhood Search (VNS) and 
    proposed in

        Nenad Mladenovic and Pierre Hansen. Variable neighborhood search.
        Computers & Operations Research, 24(11):1097–1100, 1997

    The algorithm that we propose is an evolution of the previously presented
    algorithm, Adaptive Walk. The Adaptive Walk algorithm starts with a randomly 
    chosen network and applies an intensification strategy by making a flip 
    to an output entry at a time. However in this way the search process,
    depending on the starting solution, might get stuck into local minima with
    no possibilities to escape from them or into areas of the search landscape that
    does not present “good” quality solutions. For this reason we have added a
    diversification strategy to our VNS-like algorithm. 
    The process of diversification is implemented by increasing the number of 
    flips if the search process does not find a better solution than 
    the current one for a given number of steps. 
    A better solution corresponds to a Boolean network able to express a
    differentiation dynamics more similar to the desired one: with a lower value
    of objective function than to the one obtained by the current network

    The increasing of the number of random flips aids the search process to 
    escape from local minima and it is similar to the change of neighborhood 
    in case of no improvements that is present in the classical VNS. 
    As soon as a better solution is found, the number of flip is brought back to one 
    and so the intensification process restarts until the objective function reaches 
    zero or the number of maximum iterations is reached. 
    When the number of flip is equal to 1 (and number of max local minima is -1) 
    this algorithm behaves like Adaptive Walk.
    '''

    dist = evaluate(bn)

    max_flips = sum(2**n.arity for n in bn.nodes if n not in bn.input_nodes)

    it, excluded, n_stalls, n_flips = 0, set(), 0, 1

    while it < max_iters and dist > min_target:
        
        bn, flips, excluded = scramble(bn, n_flips, excluded)

        new_dist = evaluate(bn)
        
        print(
            'i:', it, 
            'n_flips:', n_flips,
            'n_stalls:', n_stalls,
            f'old: {dist}', 
            f'new: {new_dist}', 
            end='\n\n'
        )

        if new_dist < dist:

            n_stalls = 0
            n_flips = 1
            dist = new_dist

        else:

            bn = utils.edit_boolean_network(bn, flips)

            n_stalls += 1

            if n_stalls == max_stalls:
                n_stalls = 0
                n_flips += 1
                
                if n_flips > max_flips:
                    it = max_iters

        it += 1

    return bn
