import math
import numpy as np
from pathlib import Path
from collections import defaultdict
from singleton_decorator import singleton
from bncontroller.sim.data import Axis, Quadrant, Point3D, r_point3d
from bncontroller.sim.config import Config
from bncontroller.file.utils import FROZEN_DATE, gen_fname, get_dir
from bncontroller.parse.utils import parse_args
from bncontroller.jsonlib.utils import jsonrepr, write_json, read_json, FunctionWrapper

##########################################################################################

@singleton
class Globals(Config):

    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)

        self.__json_ex_keys = (
            '__app', '__json_ex_keys',
            '_Globals__app', '_Globals__json_ex_keys'
        )

        self.__app=defaultdict(
            type(None),
            mode='debug',
            date=FROZEN_DATE,
            subopt_model_name='bn_subopt_{date}{it}.json',
            last_model_name='bn_last_{date}.json',
            it_suffix='_it{it}',
            in_suffix='_in{it}'
        )

    def to_json(self):
        return dict(
            (k, jsonrepr(v)) 
            for k, v in vars(self).items() 
            if k not in self.__json_ex_keys
        )

    @staticmethod
    def from_json(json):
        return Globals(**json)

    @property
    def config(self) -> Config:
        return super()
    
    @config.setter
    def config(self, config: Config or dict or Path):
        if isinstance(config, Config):
            self.__dict__.update(**vars(config))
        elif isinstance(config, dict):
            self.__dict__.update(**vars(Config.from_json(config)))
        elif isinstance(config, (Path, str)):
            self.__dict__.update(**vars(Config.from_file(config)))
        
    @property
    def app(self) -> defaultdict:
        return self.__app

    def generate_sim_config(self,
            world_fname='{name}_sim_world_{uniqueness}.{ext}',
            config_fname='{name}_sim_config_{uniqueness}.{ext}',
            data_fname='{name}_sim_data_{uniqueness}.{ext}',
            log_fname='{name}_sim_log_{uniqueness}.{ext}',
            ctrl_fname='{name}_sim_bn_{uniqueness}.{ext}'):
        
        '''
        Generate a config ready-to-use for running a simulation.
        This method completes or changes the paths of various 
        configuration options involving a path.
        '''

        uniqueness = lambda: FROZEN_DATE

        world_fname = gen_fname(self.app['mode'], template=world_fname, uniqueness=uniqueness, ftype='wbt')
        ctrl_fname = gen_fname(self.app['mode'], template=ctrl_fname, uniqueness=uniqueness, ftype='json')
        # slct_fname = gen_fname(self.app['mode'], template=slct_fname, uniqueness=uniqueness, ftype='json')
        config_fname = gen_fname(self.app['mode'], template=config_fname, uniqueness=uniqueness, ftype='json')
        data_fname = gen_fname(self.app['mode'], template=data_fname, uniqueness=uniqueness, ftype='json')
        log_fname = gen_fname(self.app['mode'], template=log_fname, uniqueness=uniqueness, ftype='log')

        # Create Sim Config based on the Experiment Config
        sim_config = Config.from_json(self.to_json())
        
        sim_config.webots_world_path = get_dir(sim_config.webots_world_path, create_if_dir=True) / world_fname
        
        # get_dir(sim_config.bn_ctrl_model_path, create_if_dir=True) 
        sim_config.bn_ctrl_model_path = get_dir(Path('./tmp/model').absolute(), create_if_dir=True) / ctrl_fname 

        # get_dir(sim_config.sim_config_path, create_if_dir=True)
        sim_config.sim_config_path = get_dir(Path('./tmp/config').absolute(), create_if_dir=True) / config_fname 
        
        sim_config.sim_data_path = get_dir(sim_config.sim_data_path, create_if_dir=True) / data_fname

        sim_config.sim_log_path = get_dir(sim_config.sim_log_path, create_if_dir=True) / log_fname

        return sim_config
    
    def generate_spawn_points(self):
        '''
        Return a dictionary holding:
            * generated agent spawn points (3d)
            * generated light-source spawn points (3d)
            * generated agent rotation along the y axis.

        The number and distribution of set of points/values 
        is based on the loaded configuration options.
        '''

        spawn_points = defaultdict(list)

        # Generate Evaluation Point
        spawn_points['agent_spawn_points'] = (
            [self.sim_agent_position]
            if not self.eval_n_agent_spawn_points else [
                r_point3d(
                    O=self.sim_agent_position, 
                    R=self.eval_agent_spawn_radius_m, 
                    axis=Axis.Y, 
                    quadrant=Quadrant.get(self.eval_agent_offset_quadrant)
                )
                for _ in range(self.eval_n_agent_spawn_points)    
            ]
        )

        # Generate Light Position
        spawn_points['light_spawn_points'] = (
            [self.sim_light_position]
            if not self.eval_n_light_spawn_points else [
                r_point3d(
                    O=self.sim_light_position, 
                    R=self.eval_light_spawn_radius_m, 
                    axis=Axis.Y, 
                    quadrant=Quadrant.get(self.eval_light_offset_quadrant)
                )
                for _ in range(self.eval_n_light_spawn_points)    
            ]
        )

        # Generate Evaluation yRot
        spawn_points['agent_yrots'] = (
            [self.sim_agent_yrot_rad]
            if not self.eval_agent_n_yrot_samples else np.arange(
                self.eval_agent_yrot_start_rad,
                2*math.pi + self.eval_agent_yrot_start_rad,
                2*math.pi / self.eval_agent_n_yrot_samples
            ) if self.eval_agent_n_yrot_samples > 0 else np.random.uniform(
                0.0, 2*math.pi, max(1, self.eval_n_agent_spawn_points)
            )
        )

        return spawn_points

###########################################################################################

GLOBALS : Globals = Globals()

def load_global_config():
    
    # import time
    # from pprint import pprint

    try:
        # t = time.perf_counter()
        GLOBALS.config = parse_args().config
        print('Global Configuration loaded from file...')
        # print(time.perf_counter() - t)
        # pprint(vars(GLOBALS), indent=4)

    except Exception as ex:
        print('Unable to load Global Config...')
        print(ex)
        exit(1)
    
    return GLOBALS
        
###########################################################################################

if __name__ == "__main__":

    import time, json, pprint, importlib
    from bncontroller.parse.utils import parse_args
    from argparse import ArgumentParser
    from singleton_decorator import singleton
    import statistics

    p = Path('D:\\Xander\\Documenti\\Projects\\BoolNetController\\res\\configs\\check.json')
  
    ts = []
    
    for i in range(1000):
        t = time.perf_counter()
        FunctionWrapper('bncontroller.stubs.bn::generate_simple_rbn')
        dt = time.perf_counter()-t
        ts.append(dt)

    print(
        'Z', 
        'mean:', statistics.mean(ts), 
        'stdev:', statistics.stdev(ts), 
        'max:', max(ts), 
        'min:', min(ts)
    )

    ts = []
    
    for i in range(1000):
        t = time.perf_counter()
        __ARGS = parse_args(parser=ArgumentParser('Banana Parser'), config_converter=Path)
        GLOBALS.config = __ARGS.config
        dt = time.perf_counter()-t
        ts.append(dt)

    print(
        'A', 
        'mean:', statistics.mean(ts), 
        'stdev:', statistics.stdev(ts), 
        'max:', max(ts), 
        'min:', min(ts)
    )

    ts = []
    
    for i in range(1000):
        t = time.perf_counter()
        __ARGS = parse_args(ArgumentParser('Banana Parser'), config_converter=read_json)
        GLOBALS.config = __ARGS.config
        dt = time.perf_counter()-t
        ts.append(dt)

    print(
        'B', 
        'mean:', statistics.mean(ts), 
        'stdev:', statistics.stdev(ts), 
        'max:', max(ts), 
        'min:', min(ts)
    )

    ts = []

    for i in range(1000):
        t = time.perf_counter()
        __ARGS = parse_args(ArgumentParser('Banana Parser'), config_converter=read_json)
        Config.from_json(__ARGS.config)
        dt = time.perf_counter()-t
        ts.append(dt)

    print(
        'C', 
        'mean:', statistics.mean(ts), 
        'stdev:', statistics.stdev(ts), 
        'max:', max(ts), 
        'min:', min(ts)
    )

    # pprint.pprint(GLOBALS.to_json(), indent=4)