import time
import itertools
from pandas import DataFrame
import bncontroller.stubs.selector.constraints as constraints
from bncontroller.filelib.utils import get_dir, FROZEN_DATE
from bncontroller.jsonlib.utils import write_json
from bncontroller.sim.utils import GLOBALS, load_global_config

from bncontroller.stubs.selector.utils import template_selector_generator
from bncontroller.boolnet.factory import generate_rbn

########################################################################### 

if __name__ == "__main__":
    
    load_global_config()

    nAs = GLOBALS.slct_target_n_attractors
    Ns = GLOBALS.bn_n
    Ks = GLOBALS.bn_k
    Ps = GLOBALS.bn_p
    Qs = GLOBALS.bn_q
    Is = GLOBALS.bn_n_inputs
    Os = GLOBALS.bn_n_outputs
    nRhos = GLOBALS.slct_noise_rho
    tTaus = GLOBALS.slct_target_transition_tau
    isPhis = GLOBALS.slct_input_steps_phi

    instances = GLOBALS.sd_max_iters
    
    prod = itertools.product(nAs, Ns, Ks, Ps, Qs, Is, Os, nRhos, tTaus, isPhis)

    mpath = get_dir(GLOBALS.bn_ctrl_model_path / 'stats/models', create_if_dir=True)
    dpath = get_dir(GLOBALS.bn_ctrl_model_path / 'stats/data', create_if_dir=True)

    for nA, N, K, P, Q, I, O, nRho, tTau, isPhi in prod:
        
        bns = []
        files = []
        c1s = []
        c2s = []
        c3s = []
        c4s = []
       
        generator = template_selector_generator(N, K, P, Q, I, O)

        for i in range(instances):
            
            bn = generate_rbn(generator.new_selector, force_consistency=True)

            tTau_map = {
                'a0': {'a1':tTau},
                'a1': {'a0':tTau}
            }

            i = max(map(len, bn.atm.attractors))*len(bn)*20

            c1 = constraints.test_attractors_number(bn, nA)
            c2 = constraints.test_attractors_transitions(bn, tTau_map) if len(bn.atm.attractors) > 1 else False
            c3 = constraints.test_bn_state_space_omogeneity(bn, i, nRho)
            c4 = constraints.test_attraction_basins(bn, isPhi)

            files.append(mpath / f'{i}_bns_n{N}_k{K}_nrho{int(nRho*100)}_ttau{int(tTau*100)}_iphi{isPhi}_{FROZEN_DATE}.json')

            write_json(bn.to_json(), files[-1])

            c1s.append(c1)
            c2s.append(c2)
            c3s.append(c3)
            c4s.append(c4)

        DataFrame({
            'bn': list(map(lambda p: p.name, files)),
            'c1': c1s,
            'c2': c2s,
            'c3': c3s,
            'c4': c4s
        }).to_json(dpath /f'dataframe_n{N}_k{K}_nrho{int(nRho*100)}_ttau{int(tTau*100)}_if{isPhi}_{FROZEN_DATE}.json')
