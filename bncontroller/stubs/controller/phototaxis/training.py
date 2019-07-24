

from bncontroller.sim.config import Config
from bncontroller.sim.utils import GLOBALS
from bncontroller.boolnet.utils import get_terminal_nodes
from bncontroller.type.comparators import lesser, seq_compare, mixed_compare
from bncontroller.search.pvns import VariableNeighborhoodSearch as VNS, VNSParameters
from bncontroller.search.utils import edit_boolean_network, bn_scramble_strategy
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.collectionslib.utils import flat
from bncontroller.stubs.controller.phototaxis.evaluation import pt_evaluation_for_train

def train_bncontroller(bn: OpenBooleanNetwork):

    spawn_points = GLOBALS.generate_spawn_points()

    terminal_nodes = get_terminal_nodes(bn)
    to_never_flip = set(map(hash, bn.input_nodes + terminal_nodes))

    train_scores_cmp = lambda a, b: seq_compare(a, b, strat=lesser, fallback=mixed_compare)
    train_eval_fn = lambda bn, ct: pt_evaluation_for_train(bn, ct, spawn_points)
    train_scramble_strategy = lambda bn, nf, e: bn_scramble_strategy(bn, nf, e.union(to_never_flip))
    train_tidy_strategy = lambda bn, nf: edit_boolean_network(bn, nf)

    pvns = VNS(
        sol_evaluator=train_eval_fn,
        sols_comparator=train_scores_cmp,
        sol_scrambler=train_scramble_strategy,
        sol_tidier=train_tidy_strategy
    )

    params = VNSParameters(
        target_score=flat((GLOBALS.sd_target_score, float('+inf')), to=tuple),
        min_flips=GLOBALS.sd_min_flips,
        max_flips=sum(2**n.arity for n in bn.nodes if hash(n.label) not in to_never_flip),
        max_iters=GLOBALS.sd_max_iters,
        max_stalls=GLOBALS.sd_max_stalls,
        max_stagnation=GLOBALS.sd_max_stagnation
    )

    return pvns(bn, params)