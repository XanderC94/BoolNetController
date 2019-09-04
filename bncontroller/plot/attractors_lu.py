import random, math, argparse
import itertools
import numpy as np
import bncontroller.filelib.utils as fu
from pprint import pprint
from pandas import DataFrame
from pathlib import Path
from collections import OrderedDict
from bncontroller.jsonlib.utils import read_json
from bncontroller.filelib.utils import cpaths
from bncontroller.sim.utils import Config, GLOBALS, load_global_config
from bncontroller.parse.utils import parse_args
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.collectionslib.utils import flat, transpose
from bncontroller.stubs.aggregators import weighted_pt, weighted_apt
from bncontroller.boolnet.utils import binstate, compact_state, search_attractors
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.boolnet.boolean import TRUTH_VALUES

# pt_input_configs = set([

#     (0, 0, 0, 0, 1, 0, 0, 0),
#     (0, 0, 0, 0, 1, 0, 0, 0),
#     (0, 0, 0, 0, 1, 1, 0, 0),
#     (0, 0, 0, 0, 1, 1, 1, 0),
#     (0, 0, 0, 0, 1, 1, 1, 1),
#     (0, 0, 0, 0, 0, 1, 1, 1),
#     (0, 0, 0, 0, 0, 0, 1, 1),
#     (0, 0, 0, 0, 0, 0, 0, 1),
#     (1, 0, 0, 0, 0, 0, 0, 1),
#     (1, 1, 0, 0, 0, 0, 1, 1),
#     (1, 1, 1, 0, 0, 1, 1, 1),
#     (0, 1, 1, 1, 1, 1, 1, 0),
#     (1, 1, 1, 1, 1, 1, 1, 1),
#     (0, 0, 1, 1, 1, 1, 0, 0),
#     (0, 0, 0, 1, 1, 0, 0, 0),
#     (0, 0, 0, 0, 0, 0, 0, 0),
#     (0, 0, 0, 1, 0, 0, 0, 0),
#     (0, 0, 1, 1, 0, 0, 0, 0),
#     (0, 1, 1, 1, 0, 0, 0, 0),
#     (1, 1, 1, 1, 0, 0, 0, 0),
#     (1, 1, 1, 0, 0, 0, 0, 0),
#     (1, 1, 0, 0, 0, 0, 0, 0),
#     (1, 0, 0, 0, 0, 0, 0, 0),
# ])

# apt_input_configs = set(tuple(map(lambda b: 1-b, x)) for x in pt_input_configs)

def lookup_attractors(bn: OpenBooleanNetwork):

    ts = dict()

    pt_input_configs = itertools.product(TRUTH_VALUES, repeat=len(bn.input_nodes))

    for i in pt_input_configs:

        for n, v in zip(bn.input_nodes, i):
            bn[n].state = v
        
        actual_state = bn.update()

        trajectory = []

        while binstate(actual_state) not in set(trajectory):
            
            trajectory.append(binstate(actual_state))

            for n, v in zip(bn.input_nodes, i):
                bn[n].state = v
            
            actual_state = bn.update()
            
        cutoff = trajectory.index(binstate(actual_state))
        
        # pprint(trajectory[cutoff:])

        ts.update({tuple(trajectory[cutoff:]): None})
    
    return [*ts.keys()]

###############################################################################

if __name__ == "__main__":

    load_global_config()

    ps = cpaths(
        GLOBALS.bn_ctrl_model_path, recursive=3
    ) + cpaths(
        list(map(Path, GLOBALS.slct_behaviours_map.values()))
    )

    for path in ps:
        bn = OpenBooleanNetwork.from_json(read_json(path))
        luts = lookup_attractors(bn)

        print('BN attractors:')
        pprint(bn.atm.mapped_attractors(binstate))
        print(len(bn.atm.attractors), end='\n\n')
        print('Simulated Attractors:')
        pprint(luts)
        print(len(luts), end='\n\n')

        print(sum(
            any(set(a1).intersection(set(a2)) for a2 in bn.atm.mapped_attractors(binstate)) 
            for a1 in luts
        ))

    tts = OrderedDict()

    for path in cpaths(GLOBALS.sim_data_path, recursive=1):
        # print(path)
        if path.is_file():
            sim_data = read_json(path)

            a = dict()
            l = -1

            for e in sim_data['data']:
                
                l = len(a)
                a.update({binstate(e['bnstate']): binstate(e['bnstate'])})
                
                if len(a) == l:
                    if binstate(e['bnstate']) not in tts:
                        tts[binstate(e['bnstate'])] = tuple(a.keys())
                    a.clear()
                    l = -1

    print('Test Trajectories:')
    pprint([*tts.values()])
    print(len(tts), end='\n\n')

    print(sum(any(set(a).intersection(set(tts[k])) for a in luts) for k in tts))

    pass