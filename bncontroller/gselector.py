import time

import bncontroller.type.comparators as comparators 
from bncontroller.stubs.evaluation.selectors import step1_evaluation, step2_evaluation
from bncontroller.stubs.scrambling import selector_step1_scramble_strategy, selector_step2_scramble_strategy 
from bncontroller.stubs.selector import generate_selector 
from bncontroller.file.utils import get_dir
from bncontroller.jsonlib.utils import write_json
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.search.parametric import parametric_vns

########################################################################### 
         
if __name__ == "__main__":
    
    template = parse_args_to_config()

    t = time.perf_counter()
    
    atmworkspace = get_dir(template.bn_selector_path, create_if_file=True)
    tna = template.bn_target_n_attractors
    tpa = template.bn_target_p_attractors
    
    bn, atm = None, None # generate_(template), None

    max_flips = (2**template.bn_k) * (template.bn_n - template.bn_n_inputs) + (2**1) * template.bn_n_inputs

    search1 = lambda bn : parametric_vns(
        bn,
        compare=comparators.greater,
        evaluate=lambda bn, ctx: step1_evaluation(bn, atmworkspace, tna, tpa),
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

    bn, (it, score, *_) = search2(bn)
    
    print(time.perf_counter() - t, end='\n\n')
        
    print(it)
    print(bn.attractors_input_map)
    print(bn.get_atm(from_cache=True).dtableau)
    print(bn.get_atm(from_cache=True).dattractors)

    if not bn.attractors_input_map or None in bn.attractors_input_map:
        print('Failure.')
    else:
        write_json(bn, get_dir(template.bn_selector_path) / 'bn_selector_{date}.json'.format(
            date=template.globals['date']
        ), indent=True)

