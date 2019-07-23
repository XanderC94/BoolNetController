
from bncontroller.stubs.selector.evaluation import step1_evaluation, step2_evaluation
from bncontroller.stubs.selector.utils import generate_bnselector
from bncontroller.search.genntest import GenerateNTest
from bncontroller.sim.config import SimulationConfig

def generate(template: SimulationConfig):

    gnt = GenerateNTest(
        sol_generator=lambda: generate_bnselector(*template.bn_params, force_consistency=False),
        sol_test=lambda sol: step1_evaluation(template, sol) and step2_evaluation(template, sol),
        sol_evaluator=lambda score: score
    )


    return gnt(template.sd_max_iters)
