import time
import itertools
from pathlib import Path
from bncontroller.sim.utils import GLOBALS, load_global_config
from bncontroller.file.utils import get_dir, iso8106, FROZEN_DATE
from bncontroller.jsonlib.utils import write_json
from bncontroller.stubs.selector.generation import generate_consistent_bnselector
from bncontroller.sim.logging.logger import staticlogger as logger, LoggerFactory

########################################################################### 

if __name__ == "__main__":
    
    load_global_config()

    GLOBALS.app['mode'] = 'generate'

    if GLOBALS.sim_suppress_logging:
        logger.instance.suppress(True)
    else:
        logger.instance = LoggerFactory.filelogger(
            get_dir(
                GLOBALS.app_output_path, create_if_dir=True
            ) / '{key}_{date}.log'.format(
                key=GLOBALS.app['mode'],
                date=FROZEN_DATE,
            )
        )

    toiter = lambda x: x if isinstance(x, (list, tuple)) else list([x])

    Ns, Ks, Ps, Qs, Is, Os = tuple(map(toiter, GLOBALS.bn_params))

    tRhos, nRhos = toiter(GLOBALS.slct_target_transition_rho), toiter(GLOBALS.slct_noise_rho)
    
    params = itertools.product(Ns, Ks, Ps, Qs, Is, Os, tRhos, nRhos)

    FOLDER = get_dir(GLOBALS.bn_ctrl_model_path, create_if_dir=True)
    
    for N, K, P, Q, I, O, tRho, nRho in params:

        GLOBALS.bn_n, GLOBALS.bn_k, GLOBALS.bn_p, GLOBALS.bn_q, GLOBALS.bn_n_inputs, GLOBALS.bn_n_outputs = N, K, P, Q, I, O

        if not isinstance(tRho, dict):
            GLOBALS.slct_target_transition_rho = {
                "a0": {"a0": tRho, "a1": tRho},
                "a1": {"a0": tRho, "a1": tRho}
            }

        GLOBALS.slct_noise_rho = nRho
        
        t = time.perf_counter()

        bn = GLOBALS.app_core_function()

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
                ["N", "K", "P", "Q", "I", "O", "tRho", "nRho"],
                [N, K, P, Q, I, O, tRho, "nRho"]
            ))
        )

        write_json(bnjson, path, indent=True)

        logger.info(f'BN Selector saved in {path}.\n')

    logger.flush()
    
    exit(1)


