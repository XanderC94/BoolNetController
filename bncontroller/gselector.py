import time
import itertools
from pathlib import Path
from bncontroller.sim.utils import GLOBALS, load_global_config
from bncontroller.filelib.utils import get_dir, iso8106, FROZEN_DATE
from bncontroller.collectionslib.utils import flat
from bncontroller.jsonlib.utils import write_json
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory

from multiprocessing import Pool, cpu_count

########################################################################### 

if __name__ == "__main__":
    
    load_global_config()

    GLOBALS.app['mode'] = 'generate'

    if not GLOBALS.sim_suppress_logging:
        logger.instance = LoggerFactory.filelogger(
            get_dir(
                GLOBALS.app_output_path, create_if_dir=True
            ) / '{key}_{date}.log'.format(
                key=GLOBALS.app['mode'],
                date=FROZEN_DATE,
            )
        )

    ##############################################################

    NP = cpu_count()

    pool = Pool(processes=NP)
    
    mapper = lambda f, p: pool.imap_unordered(f, p, chunksize=2*NP)

    ##############################################################

    toiter = lambda x: x if isinstance(x, (list, tuple)) else list([x])

    Ns, Ks, Ps, Qs, Is, Os = tuple(map(toiter, GLOBALS.bn_params))

    aNs = flat(toiter(GLOBALS.slct_target_n_attractors))
    tTaus = flat(toiter(GLOBALS.slct_target_transition_tau))
    nRhos = flat(toiter(GLOBALS.slct_noise_rho))
    iPhis = flat(toiter(GLOBALS.slct_input_steps_phi))

    params = itertools.product(Ns, Ks, Ps, Qs, Is, Os, aNs, tTaus, nRhos, iPhis)

    FOLDER = get_dir(GLOBALS.bn_model_path, create_if_dir=True)
    
    for N, K, P, Q, I, O, aN, tTau, nRho, iPhi in params:

        GLOBALS.bn_params = N, K, P, Q, I, O

        if not isinstance(tTau, dict):
            GLOBALS.slct_target_transition_tau = {
                "a0": {"a0": tTau, "a1": tTau},
                "a1": {"a0": tTau, "a1": tTau}
            }

        GLOBALS.slct_noise_rho = nRho
        GLOBALS.slct_target_n_attractors = aN
        GLOBALS.slct_input_steps_phi = iPhi
        
        t = time.perf_counter()

        bn = GLOBALS.app_core_function(mapper)

        logger.info(time.perf_counter() - t)

        while bn is None or not bn.attractors_input_map or None in bn.attractors_input_map:
            logger.info('Failure. Retrying...')
            t = time.perf_counter()
            bn = GLOBALS.app_core_function()
            logger.info(time.perf_counter() - t)

        logger.info(dict(**bn.attractors_input_map))
        logger.info(dict(**bn.atm.dtableau))
        logger.info(dict(**bn.atm.dattractors))

        path = FOLDER / f'bn_selector_{iso8106(ms=3)}.json'

        bnjson = bn.to_json()

        bnjson['gen_params'] = dict(
            list(zip(
                ["N", "K", "P", "Q", "I", "O", "tTau", "nRho"],
                [N, K, P, Q, I, O, tTau, nRho]
            ))
        )

        write_json(bnjson, path, indent=True)

        logger.info(f'BN Selector saved in {path}.\n')

    logger.flush()
    
    exit(1)


