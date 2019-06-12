from bncontroller.boolnet.eval.search.parametric import default_evaluation_strategy
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from bncontroller.ntree.ntstructures import NTree
from multiset import FrozenMultiset
import bncontroller.boolnet.eval.utils as utils
import math

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