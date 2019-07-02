import json, argparse, sys, math
from pathlib import Path
from bncontroller.json.utils import Jsonkin, read_json, jsonrepr, objrepr
from bncontroller.sim.data import Point3D
from bncontroller.sim.robot.utils import DeviceName
from collections import defaultdict

class DefaultConfigOptions(Jsonkin):

    __def_options = dict(
        
        # Simulator Launch Options #

        webots_path = Path('.'), # Path to webots executable
        webots_world_path = Path('.'), # Path to webots world file
        webots_launch_args = ["--mode=fast", "--batch", "--minimize"],
        webots_quit_on_termination = True,
        webots_nodes_defs = defaultdict(str),

        # Stochastic Descent Algorithm Control Parameters #

        sd_max_iters = 10000, # stochastic descent max iterations
        sd_max_stalls = 1, # 1 -> Adaptive Walk, 2+ -> VNS 
        sd_minimization_target = 0.0, # value to which reduce the objective function 
        sd_save_suboptimal_models = 2e-06, # value to which reduce the objective function

        # Simulation Control Options #

        sim_run_time_s = 10, # Execution time of the simulation in seconds
        sim_timestep_ms = 32, # Simulation Loop synch time in ms
        sim_sensing_interval_ms = 320, # Execution time of the simulation in milli-seconds
        sim_sensors_thresholds = {
            DeviceName.DISTANCE : 0.0,
            DeviceName.LIGHT : 0.0,
            DeviceName.LED : 0.0,
            DeviceName.TOUCH : 0.0,
            DeviceName.WHEEL_MOTOR : 0.0,
            DeviceName.WHEEL_POS : 0.0,
            DeviceName.GPS : 0.0,
        }, # sensors threshold to apply as filters
        sim_event_timer_s = -1, # Perturbation event triggered after t seconds
        sim_light_position = Point3D(0.0,0.0,0.0), # Origin spawn point for light source
        sim_light_spawn_radius = 0.5, # meters 
        sim_agent_position = Point3D(0.0,0.0,0.0), # Origin Spawn point for agents
        sim_agent_y_rot_rad = 0.0,
        sim_agent_spawn_radius = 0.5, # meters
        sim_suppress_logging = True, # Directory or file where to store the simulation general log
        sim_config_path = Path('.'), # Directory or file where to store the simulation config
        sim_data_path = Path('.'), # Directory or file where to store the simulation data
        sim_log_path = Path('.'), # Directory or file where to store the simulation general log
        sim_output_path = Path('.'), # Directory or file where to store the simulation general log

        # Boolean Networks Generation Control Parameters #

        bn_model_path = Path('.'), # Directory or file where to store the bn model
        bn_n = 20, # Boolean Network cardinality
        bn_k = 2, # Boolean Network Node a-rity
        bn_p = 0.5, # Truth value bias
        bn_inputs = 8, # Number or List of nodes of the BN to be reserved as inputs
        bn_outputs = 2, # Number or List of nodes of the BN to be reserved as outputs

        # Model Test Control Parameters #

        test_n_agent_spawn_points = 20,
        test_n_light_spawn_points = 20,
        test_agent_y_rot_step_rad = 15 / 180 * math.pi, # 15°
        test_positives_threshold = 2e-06, # Specify a score threshold under which model are considered "good"
        test_data_path = Path('.'), # Path where to store test data
        
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

    def __init__(self, **kwargs):

        options = DefaultConfigOptions.items()
        options.update(self.__normalize(options, **kwargs))
        
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
        self.sd_save_suboptimal_models = options['sd_save_suboptimal_models']
        # Simulation #
        self.sim_run_time_s = options['sim_run_time_s']
        self.sim_timestep_ms = options['sim_timestep_ms']
        self.sim_sensing_interval_ms = options['sim_sensing_interval_ms']
        self.sim_sensors_thresholds = options['sim_sensors_thresholds']
        self.sim_event_timer_s = options['sim_event_timer_s']
        self.sim_light_position = options['sim_light_position']
        self.sim_light_spawn_radius = options['sim_light_spawn_radius']
        self.sim_agent_position = options['sim_agent_position']
        self.sim_agent_y_rot_rad = options['sim_agent_y_rot_rad']
        self.sim_agent_spawn_radius = options['sim_agent_spawn_radius']
        self.sim_config_path = options['sim_config_path']
        self.sim_data_path = options['sim_data_path']
        self.sim_log_path = options['sim_log_path']
        self.sim_output_path = options['sim_output_path']
        self.sim_suppress_logging = options['sim_suppress_logging']
        # Boolean Network #
        self.bn_model_path = options['bn_model_path']
        self.bn_n = options['bn_n']
        self.bn_k = options['bn_k']
        self.bn_p = options['bn_p']
        self.bn_inputs = options['bn_inputs']
        self.bn_outputs = options['bn_outputs']
        # Test #
        self.test_n_agent_spawn_points = options['test_n_agent_spawn_points']
        self.test_n_light_spawn_points = options['test_n_light_spawn_points']
        self.test_agent_y_rot_step_rad = options['test_agent_y_rot_step_rad']
        self.test_positives_threshold = options['test_positives_threshold']
        self.test_data_path = options['test_data_path']

    def __normalize(self, defaults:dict, **kwargs):

        norm = dict()

        for k, v, in kwargs.items():
            if isinstance(v, dict) and isinstance(defaults[k], dict): 
                norm.update({k:self.__normalize(defaults[k], **v)})
            else:
                norm.update({k: objrepr(v, type(defaults[k]))})

        return norm

    def to_json(self) -> dict:
        return dict((k, jsonrepr(v)) for k, v in vars(self).items())
    
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

############################################################################################

if __name__ == "__main__":

    c = SimulationConfig(sd_max_iters = 10)

    c.sim_event_timer_s = 10

    # print(c, end='\n\n')

    cjson = c.to_json()

    print(cjson)

    c1 = SimulationConfig.from_json(cjson)

    print(isinstance(c1.webots_path, Path))

    print(str(c1) == str(c))

    # parser = argparse.ArgumentParser('Create empty configuration file for simulation.')

    # parser.add_argument('-p', '--path', type=Path, default='./default.json')

    # args = parser.parse_args()

    # config = SimulationConfig()

    # with open(Path(args.path), 'w') as fp:
    #     json.dump(config.to_json(), fp, indent=4)