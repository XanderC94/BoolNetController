'''
Generate or load a BN and run Stochastic Descent Search Algorithm
'''
import time
from pathlib import Path
from bncontroller.stubs.bn import rbn_gen, is_obn_consistent
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.search.parametric import parametric_vns
from bncontroller.stubs.evaluation.controllers import train_evaluation
from bncontroller.stubs.comparators import compare_train_scores
from bncontroller.stubs.scrambling import train_scramble_strategy
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.file.utils import check_path
from bncontroller.sim.data import generate_spawn_points
from bncontroller.sim.config import SimulationConfig
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory

####################################################################################

def generate_or_load_bn(template: SimulationConfig, save_virgin=False):
    
    path=template.bn_model_path
    N=template.bn_n
    K=template.bn_k
    P=template.bn_p
    I=template.bn_n_inputs
    O=template.bn_n_outputs
    date=template.globals['date']

    bn = None

    if check_path(path, create_if_dir=True):
        bng, I, O, *_ = rbn_gen(N, K, P, I, O)
        bn = bng.new_obn(I, O)

        while not is_obn_consistent(bn.nodes, I, O):
            logger.info('Regenerating...')
            bn = bng.new_obn(I, O)

        logger.info('BN generated.')

        if save_virgin:
            p = path / f'virgin_bn_{date}.json'

            write_json(bn.to_json(), p)

            logger.info(f'Virgin BN saved to {p}')

    else:
        bn = OpenBooleanNetwork.from_json(read_json(path))
        logger.info(f'BN loaded from {path}.')

    return bn

def check_config(config:SimulationConfig):

    if isinstance(config.bn_model_path, list):
        raise Exception('Model path should be a dir or file')
    elif config.webots_world_path.is_dir():
        raise Exception('Simulation world template should be a file not a dir.') 

####################################################################################

if __name__ == "__main__":

    ### Load Configuration #########################################################

    template = parse_args_to_config()

    check_config(template)

    template.globals['mode'] = (
        'rtrain' 
        if check_path(template.bn_model_path, create_if_dir=True) 
        else 'renhance' 
    )
    ### Init logger ################################################################
    
    logger.instance = LoggerFactory.filelogger(
        template.app_output_path / '{key}_{date}.log'.format(
            key=template.globals['mode'],
            date=template.globals['date'],
        )
    )

    ### BN Generation / Loading ####################################################

    bn = generate_or_load_bn(template, save_virgin=True)
    
    ### Launch search algorithm ##############################################

    if not template.train_generate_only:
        
        template.globals.update(
            **generate_spawn_points(template)
        )

        t = time.perf_counter()

        bn, ctx = parametric_vns(
            bn,
            compare=lambda a, b: compare_train_scores(a, b),
            evaluate=lambda bn, ct: train_evaluation(template, bn, ct, compare=compare_train_scores),
            scramble=lambda bn, nf, e: train_scramble_strategy(bn, nf, e),
            target_score=template.sd_target_score,
            min_flips=template.sd_min_flips,
            max_flips=sum(2**n.arity for n in bn.nodes if n not in bn.input_nodes),
            max_iters=template.sd_max_iters,
            max_stalls=template.sd_max_stalls,
            max_stagnation=template.sd_max_stagnation
        )

        logger.info(f"Search time: {time.perf_counter()-t}s")
    
        logger.info(ctx)

        savepath = template.bn_model_path / '{mode}_output_bn_{date}.json'.format(
            mode=template.globals['mode'],
            date=template.globals['date']
        )

        write_json(bn, savepath)

        logger.info(f'Output model saved to {savepath}.')
   
    logger.info('Closing...')

    logger.flush()

    exit(1)
