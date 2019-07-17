from pathlib import Path

import bncontroller.stubs.selector as selector_utils

from bncontroller.type.utils import isnotnone, first
from bncontroller.sim.config import SimulationConfig
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.search.parametric import VNSPublicContext

def step1_evaluation(bn: BoolNetSelector, path:Path, tna:int, tpa:dict):
    
    atm = bn.get_atm(atm_ws_path=path / 'atm-workspace.txt', from_cache=True)
    return selector_utils.is_bnselector_consistent(bn, atm, tna, tpa)

def step2_evaluation(template: SimulationConfig, bn: BoolNetSelector, vns_ctx: VNSPublicContext):
    
    if bn is None:
        return False
    
    for k, input_values in enumerate(template.bn_in_attr_map):

        # Impose values on input nodes
        for i in map(int, bn.input_nodes):
            bn[i].state = input_values[i]
        
        states = [
            selector_utils.compact_state(bn.step())
            for _ in range(int(template.sim_run_time_s / template.sim_timestep_ms))
        ]
        
        # Search which attractractors have developed in the run
        attr = selector_utils.search_attractors(states, bn.get_atm(from_cache=True).dattractors)

        # In this case we want than only one attractor shall appear for each input
        # in absence of noise
        if len(attr) == 1:
            bn.attractors_input_map.append((attr[0], input_values))
        else:
            return False

    # No key is None and an attractor should appear for at least 1 set of inputs
    # # that is, even if there are repeated keys, all key shall appears
    return (
        all(map(isnotnone, bn.attractors_input_map)) 
        and len(set(map(first, bn.attractors_input_map))) == template.bn_target_n_attractors
    )