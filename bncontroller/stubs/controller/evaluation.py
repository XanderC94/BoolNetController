'''
BN Evaluation utility module
'''
import math
import statistics
import itertools

from collections.abc import Iterable

import bncontroller.stubs.utils as stub_utils
import bncontroller.stubs.aggregators as aggregators

from bncontroller.sim.config import SimulationConfig, generate_sim_config
from bncontroller.jsonlib.utils import read_json
from bncontroller.type.comparators import Comparator
from bncontroller.search.parametric import VNSPublicContext
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.sim.logging.logger import staticlogger as logger

###############################################################################################

def evaluate_bncontroller(config: SimulationConfig, bn: OpenBooleanNetwork, on: tuple):
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

    fs, fpos = aggregators.phototaxis_score(
        read_json(config.sim_data_path)
    )

    ds = round(lpos.dist(fpos), 5)

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
            stub_utils.ArenaParams(
                floor_size=(3, 3),
                controller_args=template.sim_config_path
            )
        )

    data = [evaluate_bncontroller(config, bn, tp) for tp in test_params] 

    return tuple(list(e) for e in zip(*data))

###################################################################################

def train_evaluation(
        template: SimulationConfig, bn: OpenBooleanNetwork, 
        ctx: VNSPublicContext, compare:Comparator):

    test_params = itertools.product(
        template.globals['light_spawn_points'], 
        template.globals['agent_spawn_points'], 
        template.globals['agent_yrots']
    )

    fscores, *_ = test_evaluation(template, bn, test_params)

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

    if compare(new_score, ctx.score):
        
        stub_utils.save_subopt_model(
            template,
            bn.to_json(), 
            ctx,
            compare
        )

    return new_score

################################################################################################