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

    dist = evaluate(bn)

    max_flips = sum(2**n.arity for n in bn.nodes if n not in bn.input_nodes)

    it, excluded, n_stalls, n_flips = 0, set(), 0, 1

    while it < max_iters and dist > min_target:
        
        bn, last_flips, excluded = scramble(bn, n_flips, excluded)

        new_dist = evaluate(bn)
        
        print(
            'i:', it, 
            'n_flips:', n_flips,
            'n_stalls:', n_stalls,
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
