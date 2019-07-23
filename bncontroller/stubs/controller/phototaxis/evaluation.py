'''
BN Evaluation utility module
'''
import math
import statistics
import itertools
from collections.abc import Iterable
import bncontroller.stubs.utils as stub_utils
from bncontroller.sim.config import SimulationConfig, generate_sim_config
from bncontroller.jsonlib.utils import read_json
from bncontroller.type.comparators import Comparator
from bncontroller.search.pvns import VNSEvalContext
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger

###############################################################################################

def evaluate_pt_bncontroller(config: SimulationConfig, bn: OpenBooleanNetwork, on: tuple):
    '''
    Evaluate the given BN model as a robot controller on the given set of points/parameters.

    Returns:
        * function score
        * final distance
        * light initial position
        * agent initial position
        * agent y-axis rotation
    '''
    lpos, apos, yrot, *_ = on

    config.sim_agent_position = apos
    config.sim_light_position = lpos
    config.sim_agent_yrot_rad = yrot

    stub_utils.run_simulation(config, bn)

    score, fpos = config.eval_aggr_function(
        read_json(config.sim_data_path)
    )

    dist = round(lpos.dist(fpos), 5)

    logger.info(
        'iDistance: (m)', lpos.dist(apos), '|',
        'yRot: (deg)', (yrot / math.pi * 180), '|',
        'fDistance: (m)', dist, '|',
        'score: (m2/W)', score, '|',
    )

    return score, dist, lpos, apos, yrot

def pt_evaluation_for_test(template: SimulationConfig, bn: OpenBooleanNetwork, test_params: Iterable):

    ### Generate ad hoc configuration for training ################################

    config = generate_sim_config(template, keyword=template.globals['mode'])

    ### Generate simulation world file for training ################################

    if not config.webots_world_path.exists():

        stub_utils.generate_webots_worldfile(
            template.webots_world_path, 
            config.webots_world_path,
            config.arena_params
        )

    data = [evaluate_pt_bncontroller(config, bn, tp) for tp in test_params] 

    return tuple(list(e) for e in zip(*data))

###################################################################################

def pt_evaluation_for_train(template: SimulationConfig, bn: OpenBooleanNetwork, ctx: VNSEvalContext):

    test_params = itertools.product(
        template.globals['light_spawn_points'], 
        template.globals['agent_spawn_points'], 
        template.globals['agent_yrots']
    )

    fscores, *_ = pt_evaluation_for_test(template, bn, test_params)

    new_score = statistics.mean(fscores), statistics.stdev(fscores)

    logger.info(
        'it:', ctx.it, 
        'flips:', ctx.n_flips, 
        'stalls:', ctx.n_stalls,
        'stagnation: ', ctx.stagnation,
        'dist --',
        'old:', ctx.score,  
        'new:', new_score
    )

    if ctx.comparator(new_score, ctx.score):
        
        stub_utils.save_subopt_model(
            template,
            bn.to_json(), 
            ctx
        )

    return new_score

################################################################################################