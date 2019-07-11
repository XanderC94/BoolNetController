'''
Configuration class and utils module.
'''

import math
import numpy as np
from pathlib import Path
from argparse import ArgumentParser, Action
from collections import defaultdict
from bncontroller.jsonlib.utils import Jsonkin, read_json, jsonrepr, objrepr, write_json
from bncontroller.sim.data import Point3D
from bncontroller.file.utils import iso8106, get_fname, check_path, get_dir
from bncontroller.sim.robot.utils import DeviceName
from collections import namedtuple

CONFIG_CLI_NAMES = ['-c', '-cp', '--config_path', '--config']

################################################################################################

DefaultOption = namedtuple('DefaultOption', ['value', 'alt', 'descr'])

class DefaultConfigOptions(Jsonkin):
    
    __def_options=dict(
        
        app_output_path=DefaultOption(
            value=Path('.'),
            alt=list,
            descr='''Directory or file where to store the simulation general log'''
        ),
        
        # Simulator Launch Options #

        webots_path=DefaultOption(
            value=Path('.'),
            alt=None,
            descr='''path to webots executable'''
        ),
        webots_world_path=DefaultOption(
            value=Path('.'),
            alt=None,
            descr='''path to webots world file'''
        ),
        webots_launch_args=DefaultOption(
            value=["--mode=fast", "--batch", "--minimize"],
            alt=None,
            descr='''simulator command line arguements'''
        ),
        webots_quit_on_termination=DefaultOption(
            value=True,
            alt=None,
            descr='''quit simulator after simulation ends'''
        ),
        webots_nodes_defs=DefaultOption(
            value=defaultdict(str),
            alt=None,
            descr='''simulation world node definitions (node custom names)'''
        ),

        # Stochastic Descent Algorithm Control Parameters #

        sd_max_iters=DefaultOption(
            value=10000,
            alt=None,
            descr='''stochastic descent max iterations'''
        ),
        sd_max_stalls=DefaultOption(
            value=1,
            alt=None,
            descr='''-1 -> Adaptive Walk, 0+ -> VNS'''
        ),  
        sd_minimization_target=DefaultOption(
            value=0.0,
            alt=tuple,
            descr='''value to which reduce the objective function'''
        ), #  
        sd_max_stagnation=DefaultOption(
            value=1250,
            alt=None,
            descr='''close the algorithm if no further improvement are found after i iteration'''
        ),

        # Simulation Control Options #

        sim_run_time_s=DefaultOption(
            value=60,
            alt=None,
            descr='''execution time of the simulation in seconds'''
        ),
        sim_timestep_ms=DefaultOption(
            value=32,
            alt=None,
            descr='''simulation Loop synch time in ms'''
        ),
        sim_sensing_interval_ms=DefaultOption(
            value=320,
            alt=None,
            descr='''execution time of the simulation in milli-seconds'''
        ),
        sim_sensors_thresholds=DefaultOption(
            value={
                DeviceName.DISTANCE : 0.0,
                DeviceName.LIGHT : 0.0,
                DeviceName.LED : 0.0,
                DeviceName.TOUCH : 0.0,
                DeviceName.WHEEL_MOTOR : 0.0,
                DeviceName.WHEEL_POS : 0.0,
                DeviceName.GPS : 0.0,
            },
            alt=None,
            descr='''sensors threshold to apply as binarization filters'''
        ),
        sim_event_timer_s=DefaultOption(
            value=-1,
            alt=None,
            descr='''perturbation event triggered after t seconds. if -1 => not triggered.'''
        ),
        sim_light_position=DefaultOption(
            value=Point3D(0.0, 0.0, 0.0),
            alt=list,
            descr='''origin spawn point for light source'''
        ),
        sim_agent_position=DefaultOption(
            value=Point3D(0.0, 0.0, 0.0),
            alt=list,
            descr='''origin Spawn point for agents'''
        ), 
        sim_agent_yrot_rad=DefaultOption(
            value=0.0,
            alt=list,
            descr='''agent spawn orientation'''
        ),
        sim_suppress_logging=DefaultOption(
            value=True,
            alt=None,
            descr='''shut the simulation logger unit'''
        ),
        sim_config_path=DefaultOption(
            value=Path('.'),
            alt=None,
            descr='''Directory or file where to store the simulation config'''
        ),
        sim_data_path=DefaultOption(
            value=Path('.'),
            alt=list,
            descr='''Directory or file where to store the simulation data'''
        ),
        sim_log_path=DefaultOption(
            value=Path('.'),
            alt=None,
            descr='''Directory or file where to store the simulation general log'''
        ),

        # Boolean Networks Generation Control Parameters #

        bn_model_path=DefaultOption(
            value=Path('.'),
            alt=list,
            descr='''Directory or file where to store the bn model'''
        ),
        bn_n=DefaultOption(
            value=20,
            alt=None,
            descr='''boolean Network cardinality'''
        ),
        bn_k=DefaultOption(
            value=2,
            alt=None,
            descr='''boolean Network Node arity'''
        ),
        bn_p=DefaultOption(
            value=0.5,
            alt=None,
            descr='''truth value bias'''
        ),
        bn_n_inputs=DefaultOption(
            value=8,
            alt=list,
            descr='''number or List of nodes of the BN to be reserved as inputs'''
        ),
        bn_n_outputs=DefaultOption(
            value=2,
            alt=list,
            descr='''number or List of nodes of the BN to be reserved as outputs'''
        ),

        # Evaluation Parameters

        train_save_suboptimal_models=DefaultOption(
            value=2e-06,
            alt=None,
            descr='''save bn model with score under the specified threshold'''
        ),
        eval_agent_spawn_radius_m=DefaultOption(
            value=0.5,
            alt=None,
            descr='''spawn radius of the agent'''
        ), #
        eval_light_spawn_radius_m=DefaultOption(
            value=0.5,
            alt=None,
            descr='''spawn radius of the light point'''
        ),
        eval_n_agent_spawn_points=DefaultOption(
            value=1,
            alt=None,
            descr='''How many agent position to evaluate, If 0 uses always the same point (specified in sim_agent_position) to spawn the agent'''
        ),
        eval_n_light_spawn_points=DefaultOption(
            value=1,
            alt=None,
            descr='''How many light position to evaluate, If 0 uses always the same point (specified in sim_light_position) to spawn the light'''
        ),
        eval_agent_yrot_start_rad=DefaultOption(
            value=0.0,
            alt=None,
            descr='''From where to start sampling the yrot angles'''
        ),
        eval_agent_n_yrot_samples=DefaultOption(
            value=6,
            alt=None,
            descr='''Number of rotation to evaluate If 0 uses always the same value (specified in sim_agent_yrot_rad) to set the agent rotation'''
        ),
        
        # Model Test Control Parameters #

        plot_positives_threshold=DefaultOption(
            value=2e-06,
            alt=None,
            descr='''Specify a score threshold under which model are considered "good"'''
        ),
        test_data_path=DefaultOption(
            value=Path('.'),
            alt=list,
            descr='''Path where to store / read test data'''
        ),
        test_n_instances=DefaultOption(
            value=1,
            alt=None,
            descr='''# number of instances of the test cycle for each bn'''
        ), 
        test_params_aggr_func=DefaultOption(
            value='lp,ap,ar',
            alt=None,
            descr='''how test parameters should be aggregated in the test loop'''
        ),
        
        # Train control parameters#

        train_generate_only=DefaultOption(
            value=False,
            alt=None,
            descr='''Only generate training bn without running SD'''
        ),

        # App Globals #

        globals=DefaultOption(
            value=dict(
                date=iso8106(ms=3),
                score=float('+inf'),
                it=-1,
                subopt_model_name='bn_subopt_{date}{it}.json',
                it_suffix='_it{it}',
                in_suffix='_in{it}',
                agent_spawn_points=[],
                light_spawn_points=[],
                agent_yrots=[],
                mode=''
            ),
            alt=None,
            descr=''''''
        )
    )

    @staticmethod
    def options():
        return dict(DefaultConfigOptions.__def_options)
    
    @staticmethod
    def default():
        return dict((k, o.value) for k, o in DefaultConfigOptions.options().items())

    @staticmethod
    def keys():
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

    * plot_positives_threshold -- Specify a score threshold under which model are considered "good"
    * test_data_path -- Path where to store test data
    * test_n_instances -- Number of iterations of the test cycle
    * test_params_aggr_func -- how test parameters should be aggregated in the test loop

    # Train control parameters #

    * train_generate_only -- Only generate training bn without running SD
    * train_save_suboptimal_models -- value to which reduce the objective function
    '''

    def __init__(self, **kwargs):

        options = DefaultConfigOptions.default()

        options.update(self.__normalize(DefaultConfigOptions.options(), **kwargs))

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
        self.plot_positives_threshold = options['plot_positives_threshold']
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

            d, alt = (
                (defaults[k].value, defaults[k].alt)
                if isinstance(defaults[k], DefaultOption) 
                else (defaults[k], None)
            )

            norm.update(
                {k:self.__normalize(d, **v)}
                if isinstance(v, dict) and isinstance(d, dict)
                else {k: objrepr(v, type(d), alt_type=alt)}
            )

        return norm

    def to_json(self) -> dict:
        return dict((k, jsonrepr(v)) for k, v in vars(self).items() if k != 'globals')
    
    @staticmethod
    def from_json(json):

        __json = json

        if isinstance(json, (Path, str)):
            __json = read_json(json)

        return SimulationConfig(**__json)

###########################################################################################

def generate_sim_config(
        config:SimulationConfig, 
        keyword='',
        world_fname='{name}_sim_world_{uniqueness}.{ext}',
        config_fname='{name}_sim_config_{uniqueness}.{ext}',
        data_fname='{name}_sim_data_{uniqueness}.{ext}',
        log_fname='{name}_sim_log_{uniqueness}.{ext}',
        model_fname='{name}_sim_bn_{uniqueness}.{ext}'
    ):
    
    uniqueness = lambda: config.globals['date']

    world_fname = get_fname(keyword, template=world_fname, uniqueness=uniqueness, ftype='wbt')
    model_fname = get_fname(keyword, template=model_fname, uniqueness=uniqueness, ftype='json')
    config_fname = get_fname(keyword, template=config_fname, uniqueness=uniqueness, ftype='json')
    data_fname = get_fname(keyword, template=data_fname, uniqueness=uniqueness, ftype='json')
    log_fname = get_fname(keyword, template=log_fname, uniqueness=uniqueness, ftype='log')

    # Create Sim Config based on the Experiment Config
    sim_config = SimulationConfig.from_json(config.to_json())

    sim_config.globals['template'] = config
    
    sim_config.webots_world_path = get_dir(sim_config.webots_world_path, create_dirs=True) / world_fname

    sim_config.bn_model_path = get_dir(sim_config.bn_model_path, True) / model_fname

    sim_config.sim_config_path = get_dir(sim_config.sim_config_path, True) / config_fname
        
    sim_config.sim_data_path = get_dir(sim_config.sim_data_path, True) / data_fname

    sim_config.sim_log_path = get_dir(sim_config.sim_log_path, True) / log_fname

    return sim_config

###########################################################################################

if __name__ == "__main__":
    
    c = SimulationConfig()

    jr = c.to_json()

    c2 = SimulationConfig.from_json(jr)

    print(c2)

    # write_json(SimulationConfig(), './config_template.json')