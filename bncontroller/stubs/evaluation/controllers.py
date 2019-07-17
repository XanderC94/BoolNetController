'''
BN Evaluation utility module
'''
import math
import statistics
import itertools

from collections.abc import Iterable

import bncontroller.stubs.utils as stub_utils
import bncontroller.stubs.aggregators as aggregators
import bncontroller.stubs.comparators as comparators

from bncontroller.sim.config import SimulationConfig, generate_sim_config
from bncontroller.sim.logging.logger import staticlogger as logger
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.search.parametric import VNSPublicContext

###############################################################################################

def evaluate_bncontroller(config: SimulationConfig, bn: OpenBooleanNetwork, on: tuple):

    lpos, apos, yrot, *_ = on

    config.sim_agent_position = apos
    config.sim_light_position = lpos
    config.sim_agent_yrot_rad = yrot

    data = stub_utils.run_simulation(config, bn)

    fs, ds = aggregators.phototaxis_score(lpos, data)

    logger.info(
        'iDistance: (m)', lpos.dist(apos), '|',
        'yRot: (deg)', (yrot / math.pi * 180), '|',
        'fDistance: (m)', ds, '|',
        'score: (m2/W)', fs, '|',
    )

    return fs, ds, lpos, apos, yrot

def test_evaluation(template: SimulationConfig, bn: OpenBooleanNetwork, test_params: Iterable):

    ### Generate ad hoc configuration for training ################################

    config = generate_sim_config(template, keyword=template.globals['mode'])

    ### Generate simulation world file for training ################################

    if not config.webots_world_path.exists():

        stub_utils.generate_webots_worldfile(
            template.webots_world_path, 
            config.webots_world_path,
            config.sim_config_path
        )

    data = [evaluate_bncontroller(config, bn, tp) for tp in test_params] 

    return tuple(list(e) for e in zip(*data))

###################################################################################

def train_evaluation(
        template: SimulationConfig, bn: OpenBooleanNetwork, 
        vns_ctx: VNSPublicContext, compare=comparators.compare_train_scores):

    test_params = itertools.product(
        template.globals['light_spawn_points'], 
        template.globals['agent_spawn_points'], 
        template.globals['agent_yrots']
    )

    fscores, *_ = test_evaluation(template, bn, test_params)

    new_score = statistics.mean(fscores), statistics.stdev(fscores)

    logger.info(
        'it:', vns_ctx.it, 
        'flips:', vns_ctx.n_flips, 
        'stalls:', vns_ctx.n_stalls,
        'stagnation: ', vns_ctx.stagnation,
        'dist --',
        'old:', vns_ctx.score,  
        'new:', new_score
    )

    if compare(new_score, vns_ctx.score):
        
        stub_utils.save_subopt_model(
            template,
            bn.to_json(), 
            vns_ctx,
            compare
        )

    return new_score

################################################################################################