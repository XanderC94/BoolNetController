import time
import itertools
from pandas import DataFrame
from bncontroller.stubs.selector.tests import test_attractors_number
from bncontroller.stubs.selector.tests import test_attractors_transitions
from bncontroller.stubs.selector.tests import test_bn_state_space_omogeneity
from bncontroller.stubs.selector.tests import test_attraction_basins
from bncontroller.file.utils import get_dir
from bncontroller.jsonlib.utils import write_json
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.sim.data import BNParams

from bncontroller.stubs.selector.utils import generate_bnselector

########################################################################### 

if __name__ == "__main__":
    
    template = parse_args_to_config()
    
    nAs= [2]
    Ns = [5, 10]
    Ks = [2, 3]
    nRhos = [0.1, 0.2, 0.3]
    tRhos = [0.1, 0.2, 0.3, 0.4, 0.5]
    inFixs = [5, 10]

    instances = 1000
    date = template.globals['date']

    prod = itertools.product(nAs, Ns, Ks, nRhos, tRhos, inFixs)

    mpath = get_dir(template.bn_slct_model_path / 'stats/models', create_if_dir=True)
    dpath = get_dir(template.bn_slct_model_path / 'stats/data', create_if_dir=True)

    # print(len(list(prod)))

    for nA, N, K, nRho, tRho, inFix in prod:
        

        bns = []
        files = []
        c1s = []
        c2s = []
        c3s = []
        c4s = []

        for i in range(instances):
            
            bn = generate_bnselector(*BNParams(N, K, 0.5, 1, 0), force_consistency=True)

            tRho_map = {
                'a0': {'a1':tRho},
                'a1': {'a0':tRho}
            }

            c1 = test_attractors_number(bn, nA)
            c2 = test_attractors_transitions(bn, tRho_map) if len(bn.atm.attractors) > 1 else False
            c3 = test_bn_state_space_omogeneity(bn, nRho)
            c4 = test_attraction_basins(bn, inFix)

            files.append(mpath / f'{i}_bns_n{N}_k{K}_nrho{int(nRho*100)}_trho{int(tRho*100)}_if{inFix}.json')

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
        }).to_json(dpath /f'dataframe_n{N}_k{K}_nrho{int(nRho*100)}_trho{int(tRho*100)}_if{inFix}.json')
