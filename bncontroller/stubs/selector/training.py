
import bncontroller.type.comparators as comparators 
from bncontroller.stubs.selector.evaluation import step1_evaluation, step2_evaluation
from bncontroller.stubs.selector.scrambling import selector_step1_scramble_strategy, selector_step2_scramble_strategy 
from bncontroller.stubs.selector.utils import generate_selector
from bncontroller.search.parametric import parametric_vns

def search(template):

    tna = template.bn_target_n_attractors
    tpa = template.bn_target_p_attractors

    max_flips = (2**template.bn_k) * (template.bn_n - template.bn_n_inputs) + (2**1) * template.bn_n_inputs

    search1 = lambda bn : parametric_vns(
        bn,
        compare=comparators.greater,
        evaluate=lambda bn, ctx: step1_evaluation(bn, tna, tpa),
        scramble=selector_step1_scramble_strategy,
        target_score=True,
        min_flips=int(max_flips / 2),
        max_flips=max_flips,
        max_iters=int(template.sd_max_iters),
        max_stagnation=-1,
        max_stalls=max_flips
    )

    search2 = lambda bn: parametric_vns(
        bn,
        compare=comparators.greater,
        evaluate=lambda bn, ctx: step2_evaluation(template, bn, ctx),
        scramble=lambda bn, nf, e: selector_step2_scramble_strategy(
            bn, search1, lambda: generate_selector(template)
        ),
        tidy=lambda bn, flips: bn,
        target_score=True,
        max_iters=template.sd_max_iters,
        max_stagnation=-1,
        max_stalls=-1
    )

    return search2(None)