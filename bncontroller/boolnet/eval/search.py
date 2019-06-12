from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.boolnet.boolean import Boolean, r_bool, truth_values
from bncontroller.ntree.ntstructures import NTree
from bncontroller.boolnet.tes import bn_to_tes
from bncontroller.boolnet.bnutils import RBNFactory
from pathlib import Path
from multiset import FrozenMultiset
import bncontroller.boolnet.eval.utils as utils
import math

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
        max_iters=10000, 
        max_stalls=-1):

    dist = evaluate(bn)

    max_flips = sum(2**n.arity for n in bn.nodes if n not in bn.input_nodes)

    it, excluded, n_stalls, n_flips = 0, set(), 0, 1

    while it < max_iters and dist > 0:
        
        bn, last_flips, excluded = scramble(bn, n_flips, excluded)

        new_dist = evaluate(bn)
        
        print(
            'i:', it, 
            'n_flips:', n_flips,
            f'old: {dist}', 
            f'new: {new_dist}', 
            end='\n\n'
        )

        if new_dist > dist:

            reverse_flips = utils.reverse_flips(last_flips)
            bn = utils.edit_boolean_network(bn, reverse_flips)

        elif new_dist == dist:

            n_stalls += 1

            if n_stalls == max_stalls:
                n_stalls = 0
                n_flips += 1
                
                if n_flips > max_flips:
                    it = max_iters

        else:
            n_stalls = 0
            n_flips = 1
            dist = new_dist

        it += 1

    return bn

#########################################################################################################

def incr_scramble_strategy(bn:OpenBooleanNetwork, n_flips:int, already_flipped:set):

    do_not_flip = already_flipped.union(hash(k) for k in bn.input_nodes)
    flips, hflip = utils.generate_flips_blob(bn, n_flips, already_flipped=already_flipped)
    bn = utils.edit_boolean_network(bn, flips)

    return (bn, flips, already_flipped.union([hflip]))

def incremental_stochastic_descent(bn: OpenBooleanNetwork,
        evaluate = lambda bn: default_evaluation_strategy(bn, NTree.empty(), []),
        scramble = lambda bn, nf, lf: incr_scramble_strategy(bn, nf, lf),
        flip_counter = utils.ncombinations,
        max_iters = 10000,
        max_stalls = 7):
    '''
    This stochastic search algorithm incrementally changes and evaluates the given boolean network.

    The algorithm initially tries to only flip 1 truth entry at one time of a network node boolean function.

    When all the entries have been flipped without finding any BN that gives better result of the evaluation function,
    the number of flips is incremented by one and the algorithm restarts, by empting the set of already flipped nodes.

    When a better performing BN has been found the set of already flipped node is emptied.

    The algorithm stop if the evaluation function has been minimized (distance is 0.0) 
    or when the number of flips to be generated at one time is higher than the number of possible flips.

    The number of possible flips is calculated as:

        Sum(2^k(n)) for n in nodes(bn) if n not in inputs(bn)
    '''
    dist = evaluate(bn)

    it = 0
    n_flips = 1
    n_stalls = 0
    n_entries = sum(2**n.arity for n in bn.nodes if n.label not in bn.input_nodes)
    max_flips = flip_counter(n_entries, n_flips)
    excluded = set()

    while it < max_iters and dist > 0:
        
        bn, flips, excluded = scramble(bn, n_flips, excluded)

        new_dist = evaluate(bn)
        
        print(
            'i:', it, 
            'n_flips:', n_flips, 
            'already_flipped:', len(excluded), 
            f'old: {dist}', 
            f'new: {new_dist}', 
            end='\n\n'
        )

        if new_dist < dist:

            n_flips = 1
            n_stalls = 0
            max_flips = flip_counter(n_entries, n_flips)
            dist = new_dist
            excluded = set()

        else:
            reverse_flips = [utils.Flip(f.label, f.entry, 1.0 - f.new_bias) for f in flips]
            bn = utils.edit_boolean_network(bn, reverse_flips)

            if new_dist == dist:
                n_stalls +=1

            if not max_flips > len(excluded) or not max_stalls > n_stalls:
                n_flips += 1
                n_stalls = 0
                
                if n_flips > n_entries: # end algorithm
                    it = max_iters
                else:
                    max_flips = flip_counter(n_entries, n_flips)
                    excluded = set()

        it += 1

    return bn

#########################################################################################################