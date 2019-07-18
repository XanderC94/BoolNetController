
from bncontroller.sim.data import generate_spawn_points
from bncontroller.sim.config import SimulationConfig
from bncontroller.boolnet.utils import get_terminal_nodes
from bncontroller.type.comparators import lesser, seq_compare, mixed_compare
from bncontroller.search.parametric import parametric_vns, default_scramble_strategy
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.collectionslib.utils import flat
from bncontroller.stubs.controller.evaluation import train_evaluation

def train_bncontroller(template: SimulationConfig, bn: OpenBooleanNetwork):

    template.globals.update(
        **generate_spawn_points(template)
    )

    terminal_nodes = get_terminal_nodes(bn)
    to_never_flip = set(map(hash, bn.input_nodes + terminal_nodes))

    train_scores_cmp = lambda a, b: seq_compare(a, b, strat=lesser, fallback=mixed_compare)
    train_obj_fn = lambda bn, ct: train_evaluation(template, bn, ct, compare=train_scores_cmp)
    train_scramble_strategy = lambda bn, nf, e: default_scramble_strategy(bn, nf, e.union(to_never_flip))

    return parametric_vns(
        bn,
        compare=train_scores_cmp,
        evaluate=train_obj_fn,
        scramble=train_scramble_strategy,
        target_score=flat((template.sd_target_score, float('+inf')), to=tuple),
        min_flips=template.sd_min_flips,
        max_flips=sum(2**n.arity for n in bn.nodes if hash(n.label) not in to_never_flip),
        max_iters=template.sd_max_iters,
        max_stalls=template.sd_max_stalls,
        max_stagnation=template.sd_max_stagnation
    )