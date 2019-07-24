
from bncontroller.stubs.selector.evaluation import step1_evaluation, step2_evaluation
from bncontroller.boolnet.factory import generate_rbn
from bncontroller.stubs.selector.utils import template_selector_generator
from bncontroller.search.genntest import GenerateNTest
from bncontroller.sim.utils import GLOBALS

def generate_consistent_bnselector():

    bn_params = GLOBALS.bn_params
    
    max_iters = GLOBALS.sd_max_iters
    na = GLOBALS.slct_target_n_attractors
    at_rhos = GLOBALS.slct_target_transition_rho
    n_rho = GLOBALS.slct_noise_rho
    fixed_in_steps = GLOBALS.slct_fix_input_steps

    generator = template_selector_generator(*bn_params)

    gnt = GenerateNTest(
        sol_generator=lambda: generate_rbn(generator.new_selector, force_consistency=True),
        sol_test=lambda sol: step1_evaluation(sol, na, at_rhos, n_rho) and step2_evaluation(sol, fixed_in_steps),
        sol_evaluator=lambda score: score
    )

    return gnt(max_iters)
