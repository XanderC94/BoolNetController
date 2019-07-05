'''
Configuration class and utils module.
'''

import math
import argparse
import numpy as np
from pathlib import Path
from collections import defaultdict
from bncontroller.json.utils import Jsonkin, read_json, jsonrepr, objrepr, write_json
from bncontroller.sim.data import Point3D, r_point3d, Quadrant, Axis
from bncontroller.file.utils import iso8106
from bncontroller.sim.robot.utils import DeviceName

class DefaultConfigOptions(Jsonkin):
    
    __def_options=dict(
        
        app_output_path=Path('.'), # Directory or file where to store the simulation general log
        
        # Simulator Launch Options #

        webots_path=Path('.'), # Path to webots executable
        webots_world_path=Path('.'), # Path to webots world file
        webots_launch_args=["--mode=fast", "--batch", "--minimize"],
        webots_quit_on_termination=True,
        webots_nodes_defs=defaultdict(str),

        # Stochastic Descent Algorithm Control Parameters #

        sd_max_iters=10000, # stochastic descent max iterations
        sd_max_stalls=1, # 1 -> Adaptive Walk, 2+ -> VNS 
        sd_minimization_target=0.0, # value to which reduce the objective function 
        sd_max_stagnation=1250, # close the algorithm if no further improvement are found after i iteration

        # Simulation Control Options #

        sim_run_time_s=60, # Execution time of the simulation in seconds
        sim_timestep_ms=32, # Simulation Loop synch time in ms
        sim_sensing_interval_ms=320, # Execution time of the simulation in milli-seconds
        sim_sensors_thresholds={
            DeviceName.DISTANCE : 0.0,
            DeviceName.LIGHT : 0.0,
            DeviceName.LED : 0.0,
            DeviceName.TOUCH : 0.0,
            DeviceName.WHEEL_MOTOR : 0.0,
            DeviceName.WHEEL_POS : 0.0,
            DeviceName.GPS : 0.0,
        }, # sensors threshold to apply as filters
        sim_event_timer_s=-1, # Perturbation event triggered after t seconds
        sim_light_position=Point3D(0.0, 0.0, 0.0), # Origin spawn point for light source
        sim_agent_position=Point3D(0.0, 0.0, 0.0), # Origin Spawn point for agents
        sim_agent_yrot_rad=0.0,
        sim_suppress_logging=True, # Directory or file where to store the simulation general log
        sim_config_path=Path('.'), # Directory or file where to store the simulation config
        sim_data_path=Path('.'), # Directory or file where to store the simulation data
        sim_log_path=Path('.'), # Directory or file where to store the simulation general log

        # Boolean Networks Generation Control Parameters #

        bn_model_path=Path('.'), # Directory or file where to store the bn model
        bn_n=20, # Boolean Network cardinality
        bn_k=2, # Boolean Network Node a-rity
        bn_p=0.5, # Truth value bias
        bn_n_inputs=8, # Number or List of nodes of the BN to be reserved as inputs
        bn_n_outputs=2, # Number or List of nodes of the BN to be reserved as outputs

        # Evaluation Parameters

        train_save_suboptimal_models=2e-06, # value to which reduce the objective function
        eval_agent_spawn_radius_m=0.5, # meters
        eval_light_spawn_radius_m=0.5, # meters 
        eval_n_agent_spawn_points=1, # How many agent position to evaluate, If 0 uses always the same point (specified in sim_agent_position) to spawn the agent
        eval_n_light_spawn_points=1, # How many light position to evaluate, If 0 uses always the same point (specified in sim_light_position) to spawn the light
        eval_agent_yrot_start_rad=0.0, # From where to start sampling the yrot angles
        eval_agent_n_yrot_samples=6, # Number of rotation to evaluate If 0 uses always the same value (specified in sim_agent_yrot_rad) to set the agent rotation
        
        # Model Test Control Parameters #

        test_positives_threshold=2e-06, # Specify a score threshold under which model are considered "good"
        test_data_path=Path('.'), # Path where to store test data
        test_n_instances=1, # number of iterations of the test cycle
        test_params_aggr_func='lp,ap,ar', # how test parameters should be aggregated in the test loop
       
        # Train control parameters#

        train_generate_only=False, # Only generate training bn without running SD

        # App Globals #

        globals=dict(
            date=iso8106(ms=3),
            score=float('+inf'),
            it=-1,
            top_model_name='bn_subopt_{date}'+'{subfix}.json',
            subopt_suffix='_it{it}',
            agent_spawn_points=[],
            light_spawn_points=[],
            agent_yrots=[]
        )

    )

    @staticmethod
    def items():
        return dict(DefaultConfigOptions.__def_options)

    @staticmethod
    def options():
        return DefaultConfigOptions.__def_options.keys()
    
    @staticmethod
    def values():
        return DefaultConfigOptions.__def_options.values()

################################################################################################

class SimulationConfig(Jsonkin):

    '''      
    * app_output_path -- Directory or file where to store the simulation general log
    
    # Simulator params
    
    * webots_path -- Path to webots executable
    * webots_world_path -- Path to webots world file
    * webots_launch_args -- commandline arguments of the simulator
    * webots_quit_on_termination -- quit the simulator after completing the evaluation
    * webots_nodes_defs -- Specify the Node Defs of the simulated world

    # Stochastic Descent Algorithm Control Parameters #

    * sd_max_iters -- stochastic descent max iterations
    * sd_max_stalls -- 1 -> Adaptive Walk, 2+ -> VNS 
    * sd_minimization_target -- value to which reduce the objective function 
    * sd_max_stagnation -- close the algorithm if no further improvement are found after i iteration

    # Simulation Control Options #

    * sim_run_time_s -- Execution time of the simulation in seconds
    * sim_timestep_ms -- Simulation Loop synch time in ms
    * sim_sensing_interval_ms -- Execution time of the simulation in milli-seconds
    * sim_sensors_thresholds -- # sensors threshold to apply as filters
    * sim_event_timer_s -- Perturbation event triggered after t seconds
    * sim_light_position -- Origin spawn point for light source
    * sim_agent_position -- Origin Spawn point for agents
    * sim_agent_yrot_rad -- Radius of rotation of the agent body
    * sim_suppress_logging -- Directory or file where to store the simulation general log
    * sim_config_path -- Directory or file where to store the simulation config
    * sim_data_path -- Directory or file where to store the simulation data
    * sim_log_path -- Directory or file where to store the simulation general log

    # Boolean Networks Generation Control Parameters #

    * bn_model_path -- Directory or file where to store the bn model
    * bn_n -- Boolean Network cardinality
    * bn_k -- Boolean Network Node a-rity
    * bn_p -- Truth value bias
    * bn_n_inputs -- Number or List of nodes of the BN to be reserved as inputs
    * bn_n_outputs -- Number or List of nodes of the BN to be reserved as outputs

    # Evaluation Parameters

    * eval_agent_spawn_radius_m
    * eval_light_spawn_radius_m
    * eval_n_agent_spawn_points -- How many agent position to evaluate, 
    If 0 uses always the same point (specified in sim_agent_position) to spawn the agent

    * eval_n_light_spawn_points -- How many light position to evaluate, 
    If 0 uses always the same point (specified in sim_light_position) to spawn the light

    * eval_agent_yrot_start_rad -- From where to start sampling the yrot angles
    * eval_agent_n_yrot_samples -- Number of rotation to evaluate, 
    If 0 uses always the same value (specified in sim_agent_yrot_rad) to set the agent rotation.
    If -1 generates max(1, eval_n_agent_spawn_points) random rotation in [0, 2PI].

    # Model Test Control Parameters #

    * test_positives_threshold -- Specify a score threshold under which model are considered "good"
    * test_data_path -- Path where to store test data
    * test_n_instances -- Number of iterations of the test cycle
    * test_params_aggr_func -- how test parameters should be aggregated in the test loop

    # Train control parameters #

    * train_generate_only -- Only generate training bn without running SD
    * train_save_suboptimal_models -- value to which reduce the objective function
    '''

    def __init__(self, **kwargs):

        options = DefaultConfigOptions.items()
        options.update(self.__normalize(options, **kwargs))
        
        self.app_output_path = options['app_output_path']

        # Webots #
        self.webots_path = options['webots_path']
        self.webots_world_path = options['webots_world_path']
        self.webots_launch_args = options['webots_launch_args']
        self.webots_quit_on_termination = options['webots_quit_on_termination']
        self.webots_nodes_defs = options['webots_nodes_defs']

        # Stochastic Descent Search
        self.sd_max_iters = options['sd_max_iters']
        self.sd_max_stalls = options['sd_max_stalls']
        self.sd_minimization_target = options['sd_minimization_target']
        self.sd_max_stagnation = options['sd_max_stagnation']

        # Simulation #
        self.sim_run_time_s = options['sim_run_time_s']
        self.sim_timestep_ms = options['sim_timestep_ms']
        self.sim_sensing_interval_ms = options['sim_sensing_interval_ms']
        self.sim_sensors_thresholds = options['sim_sensors_thresholds']
        self.sim_event_timer_s = options['sim_event_timer_s']
        self.sim_light_position = options['sim_light_position']
        self.sim_agent_position = options['sim_agent_position']
        self.sim_agent_yrot_rad = options['sim_agent_yrot_rad']
        self.sim_config_path = options['sim_config_path']
        self.sim_data_path = options['sim_data_path']
        self.sim_log_path = options['sim_log_path']
        self.sim_suppress_logging = options['sim_suppress_logging']

        # Boolean Network #
        self.bn_model_path = options['bn_model_path']
        self.bn_n = options['bn_n']
        self.bn_k = options['bn_k']
        self.bn_p = options['bn_p']
        self.bn_n_inputs = options['bn_n_inputs']
        self.bn_n_outputs = options['bn_n_outputs']

        # Evaluation Parameters
        self.eval_light_spawn_radius_m = options['eval_light_spawn_radius_m']
        self.eval_agent_spawn_radius_m = options['eval_agent_spawn_radius_m']
        self.eval_n_agent_spawn_points = options['eval_n_agent_spawn_points']
        self.eval_n_light_spawn_points = options['eval_n_light_spawn_points']
        self.eval_agent_yrot_start_rad = options['eval_agent_yrot_start_rad']
        self.eval_agent_n_yrot_samples = options['eval_agent_n_yrot_samples']

        # Test #
        self.test_positives_threshold = options['test_positives_threshold']
        self.test_data_path = options['test_data_path']
        self.test_n_instances = options['test_n_instances']
        self.test_params_aggr_func = options['test_params_aggr_func']

        # Train #
        self.train_save_suboptimal_models = options['train_save_suboptimal_models']
        self.train_generate_only = options['train_generate_only']
        
        # App Globals #
        self.globals = options['globals']

    def __normalize(self, defaults: dict, **kwargs):

        norm = dict()

        for k, v, in kwargs.items():
            if isinstance(v, dict) and isinstance(defaults[k], dict): 
                norm.update({k:self.__normalize(defaults[k], **v)})
            else:
                norm.update({k: objrepr(v, type(defaults[k]))})

        return norm

    def fill_globals(self):
        # Generate Evaluation Point
        self.globals['agent_spawn_points'] = (
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
        self.globals['light_spawn_points'] = (
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
        self.globals['agent_yrots'] = (
            [self.sim_agent_yrot_rad]
            if not self.eval_agent_n_yrot_samples else np.arange(
                self.eval_agent_yrot_start_rad,
                2*math.pi + self.eval_agent_yrot_start_rad,
                2*math.pi / self.eval_agent_n_yrot_samples
            ) if self.eval_agent_n_yrot_samples > 0 else np.random.uniform(
                0.0, 2*math.pi, max(1, self.eval_n_agent_spawn_points)
            )
        )

    def to_json(self) -> dict:
        
        return dict((k, jsonrepr(v)) for k, v in vars(self).items() if k != 'globals')
    
    @staticmethod
    def from_json(json:dict):
        return SimulationConfig(**json)

###########################################################################################

def parse_args_to_config() -> SimulationConfig:

    parser = argparse.ArgumentParser('BoolNet Controller Configuration Parsing Unit.')

    parser.add_argument('-cp', '--config_path', type=Path)

    args = parser.parse_args()

    json_config = read_json(args.config_path)

    return SimulationConfig(**json_config)

if __name__ == "__main__":
    
    write_json(SimulationConfig(), './config_template.json')