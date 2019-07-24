import math
import numpy as np
from pathlib import Path
from collections import defaultdict
from singleton_decorator import singleton
from bncontroller.jsonlib.utils import jsonrepr, write_json
from bncontroller.file.utils import iso8106, gen_fname, get_dir
from bncontroller.sim.config import Config
from bncontroller.sim.data import Axis, Quadrant, Point3D, r_point3d

##########################################################################################

@singleton
class Globals(Config):

    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)

        self.__args = None
        self.__unknowns = None

        self.__app=defaultdict(
            type(None),
            mode='debug',
            date=iso8106(ms=3),
            subopt_model_name='bn_subopt_{date}{it}.json',
            last_model_name='bn_last_{date}.json',
            it_suffix='_it{it}',
            in_suffix='_in{it}'
        )

    def to_json(self):
        return dict(
            (k, jsonrepr(v)) 
            for k,v in vars(self).items() 
            if k not in ('__args', '__unknowns', '__app')
        )

    @staticmethod
    def from_json(json):
        return Globals(**json)

    @property
    def config(self) -> Config:
        return super()
    
    @config.setter
    def config(self, config: Config):
        self.__init__(**config.to_json())

    @property
    def app(self) -> defaultdict:
        return self.__app
    
    @property
    def args(self):
        return self.__args

    @args.setter
    def args(self, args):
        self.__args = args
    
    @property
    def unknowns(self) -> list:
        return self.__unknowns

    @unknowns.setter
    def unknowns(self, unknowns: list):
        self.__unknowns = unknowns

    def generate_sim_config(self,
            # keyword='',
            world_fname='{name}_sim_world_{uniqueness}.{ext}',
            config_fname='{name}_sim_config_{uniqueness}.{ext}',
            data_fname='{name}_sim_data_{uniqueness}.{ext}',
            log_fname='{name}_sim_log_{uniqueness}.{ext}',
            model_fname='{name}_sim_bn_{uniqueness}.{ext}'):
        
        '''
        Generate a config ready-to-use for running a simulation.
        This method completes or changes the paths of various 
        configuration options involving a path.
        '''

        uniqueness = lambda: self.app['date']

        world_fname = gen_fname(self.app['mode'], template=world_fname, uniqueness=uniqueness, ftype='wbt')
        model_fname = gen_fname(self.app['mode'], template=model_fname, uniqueness=uniqueness, ftype='json')
        config_fname = gen_fname(self.app['mode'], template=config_fname, uniqueness=uniqueness, ftype='json')
        data_fname = gen_fname(self.app['mode'], template=data_fname, uniqueness=uniqueness, ftype='json')
        log_fname = gen_fname(self.app['mode'], template=log_fname, uniqueness=uniqueness, ftype='log')

        # Create Sim Config based on the Experiment Config
        sim_config = Config.from_json(self.to_json())
        
        sim_config.webots_world_path = get_dir(sim_config.webots_world_path, create_if_dir=True) / world_fname
        
        # get_dir(sim_config.bn_ctrl_model_path, create_if_dir=True) 
        sim_config.bn_ctrl_model_path = get_dir(Path('./tmp/model').absolute(), create_if_dir=True) / model_fname 
        
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
                    quadrant=Quadrant.PPN
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
                    quadrant=Quadrant.PPN
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

###########################################################################################

if __name__ == "__main__":

    # write_json(Config(), './config_template.json')
    GLOBALS.config = Config()

    print(GLOBALS.to_json())
