from pandas import DataFrame
from pathlib import Path
from bncontroller.json.utils import read_json, write_json
from bncontroller.file.utils import iso8106
from bncontroller.sim.config import parse_args_to_config
from bncontroller.sim.data import Point3D, r_point3d, Axis, Quadrant
from bncontroller.boolnet.bnstructures import OpenBooleanNetwork
from collections import defaultdict
import random, math, numpy as np
import bncontroller.stubs.evaluation as evaluation

#########################################################################################################

date = iso8106()

if __name__ == "__main__":

    config = parse_args_to_config()

    yrots = list(
        np.arange(0, 2*math.pi, config.test_agent_y_rot_step_rad)
    )

    lpos = list(
        r_point3d(
            O=config.sim_light_position, 
            R=config.sim_light_spawn_radius, 
            axis=Axis.Y, 
            quadrant=Quadrant.NPP
        )
        for _ in range(config.test_n_light_spawn_points)
    )   

    apos = list(
        r_point3d(
            O=config.sim_agent_position, 
            R=config.sim_agent_spawn_radius, 
            axis=Axis.Y, 
            quadrant=Quadrant.PPN
        )
        for _ in range(config.test_n_agent_spawn_points)    
    )

    files = dict()
    bns = defaultdict(list)
    data = defaultdict(DataFrame)

    if config.bn_model_path.is_dir():
        
        for f in config.bn_model_path.iterdir():
            if f.is_file() and 'json' in f.suffix and 'rtest' not in f.name:
                name = f.with_suffix('').name
                # name = str(name).split('_')[1]
                bns[name] = OpenBooleanNetwork.from_json(read_json(f))
                files[name] = f

    else: 
        name = f.with_suffix('').name
        # name = str(name).split('_')[1]
        bn = OpenBooleanNetwork.from_json(read_json(config.bn_model_path))
        bns[name] = bn
        files[name] = f.name

    for k in bns:
        print(k)

        _d = defaultdict(list)

        for i in range(config.sd_max_iters):
            
            for yr in yrots:

                sim_config = evaluation.generate_ad_hoc_sim_config(config, keyword=f'rtest')
                sim_config.sim_agent_y_rot_rad = yr
                sim_config.sim_agent_position = apos[i]
                sim_config.sim_light_position = lpos[i]

                data = evaluation.run_simulation(sim_config, bns[k])
                new_score, rscore = evaluation.aggregate_sim_data(sim_config.sim_light_position, data)

                # new_score = random.normalvariate(0.5, math.sqrt(0.5)) # only for test purpose

                _d['scores'].append(new_score)
                _d['apos'].append(sim_config.sim_agent_position)
                _d['lpos'].append(sim_config.sim_light_position)
                _d['yrot'].append(sim_config.sim_agent_y_rot_rad)
                _d['idist'].append(_d['apos'][-1].dist(_d['lpos'][-1]))
                _d['fdist'].append(rscore)

        df = DataFrame(_d)

        data[k] = df

        if not config.test_data_path.exists():
            config.test_data_path.mkdir()

        df.to_json(config.test_data_path / ('rtest_data_' + str(files[k].name)))