'''
BN Evaluation utility module
'''
import math
import statistics
import itertools
from collections.abc import Iterable
import bncontroller.stubs.utils as stub_utils
from bncontroller.sim.config import Config
from bncontroller.sim.utils import GLOBALS
from bncontroller.jsonlib.utils import read_json
from bncontroller.type.comparators import Comparator
from bncontroller.search.pvns import VNSEvalContext
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger

###############################################################################################

def evaluate_pt_bncontroller(simconfig: Config, bn: OpenBooleanNetwork, on: tuple):
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

    simconfig.sim_agent_position = apos
    simconfig.sim_light_position = lpos
    simconfig.sim_agent_yrot_rad = yrot

    stub_utils.run_simulation(simconfig, bn)

    score, fpos = simconfig.eval_aggr_function(
        read_json(simconfig.sim_data_path)
    )

    dist = round(lpos.dist(fpos), 5)

    logger.info(
        'iDistance: (m)', lpos.dist(apos), '|',
        'yRot: (deg)', (yrot / math.pi * 180), '|',
        'fDistance: (m)', dist, '|',
        'score: (m2/W)', score, '|',
    )

    return score, dist, lpos, apos, yrot

def pt_evaluation_for_test(bn: OpenBooleanNetwork, test_params: Iterable):
    '''
    Run a simulation for each set of test parameters. 
    '''
    ### Generate ad hoc configuration for training ################################

    simconfig = GLOBALS.generate_sim_config()

    ### Generate simulation world file for training ################################

    if not simconfig.webots_world_path.exists():

        stub_utils.generate_webots_worldfile(
            GLOBALS.webots_world_path, 
            simconfig.webots_world_path,
            simconfig.arena_params
        )

    # May be launched parallel (... ?)
    data = [evaluate_pt_bncontroller(simconfig, bn, tp) for tp in test_params] 

    return tuple(list(e) for e in zip(*data))

###################################################################################

def pt_evaluation_for_train(bn: OpenBooleanNetwork, ctx: VNSEvalContext, spawn_points: list):
    '''
    Aggregates test parameters and run a simulation for each set of them. 
    '''
    test_params = itertools.product(
        spawn_points['light_spawn_points'], 
        spawn_points['agent_spawn_points'], 
        spawn_points['agent_yrots']
    )

    fscores, *_ = pt_evaluation_for_test(bn, test_params)

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
            GLOBALS.bn_ctrl_model_path,
            new_score,
            ctx.it,
            bn.to_json(), 
            save_subopt=ctx.comparator(
                new_score, 
                GLOBALS.train_save_suboptimal_models
            )
        )

    return new_score

################################################################################################