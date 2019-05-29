from bncontroller.boolnet.bnstructures import BooleanNetwork
from bncontroller.boolnet.boolean import Boolean, r_bool, truth_values
from bncontroller.ntree.ntstructures import NTree
from bncontroller.boolnet.tes import bn_to_tes
from bncontroller.boolnet.eval.sota import generate_flips, edit_boolean_network, tes_distance
from pathlib import Path
import random, math, queue, copy, subprocess, datetime

def default_evaluation_strategy(bn: BooleanNetwork, target_tes: NTree, thresholds: list) -> float:

    tes = bn_to_tes(bn, thresholds)
    return tes_distance(tes, target_tes)

def default_scramble_strategy(bn: BooleanNetwork, n_flips, last_flips):
    flips = generate_flips(bn, n_flips, last_flips)
    bn, flipped = edit_boolean_network(bn, flips)
    return (bn, flipped, flips)

def adaptive_walk(
        n: int or list, k: int or list or dict, p:float, 
        target_tes: NTree, thresholds: list, 
        max_iters = 10000):
    
    return parametric_vns(
        n, k, p, 
        evaluation_strategy = lambda *args: default_evaluation_strategy(args[0], target_tes, thresholds), 
        max_iters=max_iters, 
        max_stalls=-1
    )

def variable_neighborhood_search(
        n: int or list, k: int or list or dict, p:float, 
        target_tes: NTree, thresholds: list, 
        max_iters = 10000, max_stalls = 10):
    
    return parametric_vns(
        n, k, p, 
        evaluation_strategy = lambda *args: default_evaluation_strategy(args[0], target_tes, thresholds), 
        max_iters=max_iters, 
        max_stalls=max_stalls
    )

def parametric_vns(
        n: int or list, k: int or list or dict, p: float, 
        evaluation_strategy = lambda *args: default_evaluation_strategy(args[0], NTree.empty(), []),
        scramble_strategy =  lambda bn, n_flips, last_flipped: default_scramble_strategy(bn, n_flips, last_flipped),
        max_iters = 10000, max_stalls = -1):

    bn = BooleanNetwork(n, k, bfInit= lambda *args: Boolean(r_bool(p)))
    # sol = bn
    dist = evaluation_strategy(bn)

    it, last_flipped, n_stalls, n_flips = 0, [-1], 0, 1

    while it < max_iters and dist > 0:

        if n_stalls == max_stalls:
            n_stalls = 0
            n_flips += 1

            if n_flips > len(bn): return bn

        bn, last_flipped, flips = scramble_strategy(bn, n_flips, last_flipped)

        new_dist = evaluation_strategy(bn)

        if new_dist > dist:
            bn = edit_boolean_network(bn, [(flip[0], flip[1], not flip[2]) for flip in flips])
        else:

            if dist == new_dist:
                n_stalls += 1
            else:
                n_stalls = 0
                n_flips = 1

            dist = new_dist
            # sol = bn

        it += 1

    return bn

#########################################################################################################

if __name__ == "__main__":
    
    bn = adaptive_walk(5, 1, 0.666, NTree.empty(), [], max_iters=100000)

    print(bn)
