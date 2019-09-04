import time
import itertools
from pandas import DataFrame
from collections import defaultdict
import bncontroller.stubs.selector.constraints as constraints
from bncontroller.filelib.utils import get_dir, FROZEN_DATE
from bncontroller.jsonlib.utils import write_json
from bncontroller.collectionslib.utils import flat
from bncontroller.sim.utils import GLOBALS, load_global_config

from bncontroller.stubs.selector.utils import template_selector_generator
from bncontroller.boolnet.factory import generate_rbn

########################################################################### 

def build_tmap(tau, n):
    if isinstance(tau, dict):
        return tau
    else:
        tmap = defaultdict(lambda: defaultdict(lambda: 1.0))

        for a1 in range(n):
            for a2 in range(n):
                tmap[f'a{a1}'][f'a{a2}'] = tau
        return tmap

if __name__ == "__main__":
    
    load_global_config()

    toiter = lambda x: x if isinstance(x, (list, tuple)) else list([x])

    Ns, Ks, Ps, Qs, Is, Os = tuple(map(toiter, GLOBALS.bn_params))

    aNs = flat(toiter(GLOBALS.slct_target_n_attractors))
    tTaus = flat(toiter(GLOBALS.slct_target_transition_tau))
    nRhos = flat(toiter(GLOBALS.slct_noise_rho))
    iPhis = flat(toiter(GLOBALS.slct_input_steps_phi))

    instances = GLOBALS.sd_max_iters
    
    prod = itertools.product(aNs, Ns, Ks, Ps, Qs, Is, Os, nRhos, tTaus, iPhis)

    mpath = get_dir(GLOBALS.sim_data_path / 'stats/models', create_if_dir=True)
    dpath = get_dir(GLOBALS.sim_data_path / 'stats/data', create_if_dir=True)

    for nA, N, K, P, Q, I, O, nRho, tTau, isPhi in prod:
        
        bns = []
        files = []
        c1s = []
        c2s = []
        c2no1s = []
        c3s = []
        c4s = []
       
        generator = template_selector_generator(N, K, P, Q, I, O)

        for i in range(instances):
            
            bn = generate_rbn(generator.new_selector, force_consistency=True)

            tTau_map = build_tmap(tTau, len(bn.atm.attractors))

            it = max(map(len, bn.atm.attractors))*len(bn)*20

            c1 = constraints.test_attractors_number(bn, nA)
            c2 = constraints.test_attractors_transitions(bn, tTau_map) # if len(bn.atm.attractors) > 1 else False
            c2no1 = constraints.test_attractors_transitions(bn, tTau_map) if len(bn.atm.attractors) > 1 else False
            c3 = constraints.test_bn_state_space_homogeneity(bn, it, nRho)
            c4 = bool(constraints.test_attraction_basins(bn, isPhi))

            files.append(mpath / f'{i}_bns_n{N}_k{K}_nrho{int(nRho*100)}_ttau{int(tTau*100)}_iphi{isPhi}_{FROZEN_DATE}.json')

            write_json(bn.to_json(), files[-1])

            c1s.append(c1)
            c2s.append(c2)
            c2no1s.append(c2no1)
            c3s.append(c3)
            c4s.append(c4)

        DataFrame({
            'bn': list(map(lambda p: p.name, files)),
            'c1': c1s,
            'c2': c2s,
            'c2no1': c2no1s,
            'c3': c3s,
            'c4': c4s
        }).to_json(dpath /f'dataframe_n{N}_k{K}_nrho{int(nRho*100)}_ttau{int(tTau*100)}_if{isPhi}_{FROZEN_DATE}.json')
