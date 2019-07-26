import time
import itertools
from pandas import DataFrame
import bncontroller.stubs.selector.tests as constraints
from bncontroller.file.utils import get_dir, FROZEN_DATE
from bncontroller.jsonlib.utils import write_json
from bncontroller.sim.utils import GLOBALS

from bncontroller.stubs.selector.utils import template_selector_generator
from bncontroller.boolnet.factory import generate_rbn

########################################################################### 

if __name__ == "__main__":
    
    nAs= [2]
    Ns = [5, 10]
    Ks = [2, 3]
    Ps = [0.5]
    Qs = [0.0]
    Is = [1]
    Os = [0]
    nRhos = [0.1, 0.2, 0.3]
    tRhos = [0.1, 0.2, 0.3, 0.4, 0.5]
    inFixs = [5, 10]

    instances = 1000
    
    prod = itertools.product(nAs, Ns, Ks, Ps, Is, Os, nRhos, tRhos, inFixs)

    mpath = get_dir(GLOBALS.bn_slct_model_path / 'stats/models', create_if_dir=True)
    dpath = get_dir(GLOBALS.bn_slct_model_path / 'stats/data', create_if_dir=True)

    for nA, N, K, P, Q, I, O, nRho, tRho, inFix in prod:
        
        bns = []
        files = []
        c1s = []
        c2s = []
        c3s = []
        c4s = []
       
        generator = template_selector_generator(N, K, P, Q, I, O)

        for i in range(instances):
            
            bn = generate_rbn(generator.new_selector, force_consistency=True)

            tRho_map = {
                'a0': {'a1':tRho},
                'a1': {'a0':tRho}
            }

            c1 = constraints.test_attractors_number(bn, nA)
            c2 = constraints.test_attractors_transitions(bn, tRho_map) if len(bn.atm.attractors) > 1 else False
            c3 = constraints.test_bn_state_space_omogeneity(bn, nRho)
            c4 = constraints.test_attraction_basins(bn, inFix)

            files.append(mpath / f'{i}_bns_n{N}_k{K}_nrho{int(nRho*100)}_trho{int(tRho*100)}_if{inFix}_{FROZEN_DATE}.json')

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
        }).to_json(dpath /f'dataframe_n{N}_k{K}_nrho{int(nRho*100)}_trho{int(tRho*100)}_if{inFix}_{FROZEN_DATE}.json')
