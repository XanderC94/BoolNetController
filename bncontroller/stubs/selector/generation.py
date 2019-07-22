
from bncontroller.stubs.selector.evaluation import step1_evaluation, step2_evaluation
from bncontroller.stubs.selector.utils import generate_bnselector
from bncontroller.search.genntest import GenerateNTest

def generate(template):

    gnt = GenerateNTest(
        sol_generator=lambda: generate_bnselector(template, force_consistency=False),
        sol_test=lambda sol: step1_evaluation(template, sol) and step2_evaluation(template, sol),
        sol_evaluator=lambda score: score
    )


    return gnt(template.sd_max_iters)
