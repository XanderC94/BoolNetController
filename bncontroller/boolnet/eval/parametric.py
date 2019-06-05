from bncontroller.boolnet.bnstructures import BooleanNetwork
from bncontroller.boolnet.boolean import Boolean, r_bool, truth_values
from bncontroller.ntree.ntstructures import NTree
from bncontroller.boolnet.tes import bn_to_tes
from bncontroller.boolnet.bnutils import RBNFactory
from pathlib import Path
import random, math, queue, copy, subprocess, datetime
import bncontroller.boolnet.eval.utils as utils

def default_evaluation_strategy(bn: BooleanNetwork, target_tes: NTree, thresholds: list) -> float:

    tes = bn_to_tes(bn, thresholds)
    return utils.tes_distance(tes, target_tes)

def default_scramble_strategy(bn: BooleanNetwork, n_flips, last_flipped):
    
    flips = utils.generate_flips(bn, n_flips, last_flipped)
    bn, flipped = utils.edit_boolean_network(bn, flips)

    return (bn, flipped, flips)

###############################################################################

def parametric_vns(
        bng: RBNFactory,
        evaluation_strategy = lambda bn: default_evaluation_strategy(bn, NTree.empty(), []),
        scramble_strategy =  lambda bn, n_flips, last_flipped: default_scramble_strategy(bn, n_flips, last_flipped),
        max_iters = 10000, max_stalls = -1):

    bn = bng.new()
    dist = evaluation_strategy(bn)

    it, last_flipped, n_stalls, n_flips = 0, [], 0, 1

    while it < max_iters and dist > 0:

        if n_stalls == max_stalls:
            n_stalls = 0
            n_flips += 1

            if n_flips > len(bn): return bn

        old = bn.to_json()
        
        bn, last_flipped, flips = scramble_strategy(bn, n_flips, last_flipped)

        new_dist = evaluation_strategy(bn)

        if new_dist > dist:
            bn, *_ = utils.edit_boolean_network(bn, [(flip[0], flip[1], 1.0 - flip[2]) for flip in flips])

            print(flips, dist, new_dist)

            # n_stalls = 0
            # n_flips = 1
        else:
            if new_dist == dist:
                n_stalls += 1
            else:
                n_stalls = 0
                n_flips = 1

            dist = new_dist

        it += 1

    return bn

#########################################################################################################

if __name__ == "__main__":
    
    bng = RBNFactory(5, 1, bf_init=lambda *args: r_bool(0.666), node_init=lambda i: False)

    bn = parametric_vns(bng, max_iters=100000)

    print(bn)
