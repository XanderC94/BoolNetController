import json, argparse, sys
from pathlib import Path
from bncontroller.json_utils import Jsonkin
from bncontroller.sim.data import Point3D

class SimulationConfig(Jsonkin):

    def __init__(self, options: dict = {}):

        self.__def_options = {
            'webots_path': str(Path('.')), # Path to webots executable
            'webots_world_path': str(Path('.')), # Path to webots world file
            'webots_launch_args': ["--mode=fast", "--batch"],
            'webots_close_on_quit': True,
            'sd_max_iters': 10000, # stochastic descent max iterations
            'sd_max_stalls': 1, # 1 -> Adaptive Walk, 2+ -> VNS 
            'sim_time': 10, # Execution time of the simulation in seconds
            'sim_event_timer': 10, # Perturbation event triggered after t seconds
            'sim_light_position': Point3D(0.0,0.0,0.0).to_json(),
            'sim_config_path': str(Path('.')), # Directory or file where to store the simulation config
            'sim_data_path': str(Path('.')), # Directory or file where to store the simulation data
            'sim_log_path': str(Path('.')), # Directory or file where to store the simulation general log
            'bn_model_path': str(Path('.')), # Directory or file where to store the bn model
            'bn_n': 20, # Boolean Network cardinality
            'bn_k': 2, # Boolean Network Node a-rity
            'bn_p': 0.5, # Truth value bias
            'bn_inputs': 8, # Number or List of nodes of the BN to be reserved as inputs
            'bn_outputs': 2 # Number or List of nodes of the BN to be reserved as outputs
        }

        self.__options = dict(self.__def_options)
        self.__options.update(options)

    # Getters #

    @property
    def webots_path(self):
        return Path(self.__options['webots_path'])
    
    @property
    def webots_world_path(self):
        return Path(self.__options['webots_world_path'])

    @property
    def webots_launch_args(self):
        return self.__options['webots_launch_args']
    
    @property
    def webots_close_on_quit(self):
        return self.__options['webots_close_on_quit']
    
    @property
    def sd_max_iters(self):
        return self.__options['sd_max_iters']
    
    @property
    def sd_max_stalls(self):
        return self.__options['sd_max_stalls']
    
    @property
    def sim_time(self):
        return self.__options['sim_time']
    
    @property
    def sim_event_timer(self):
        return self.__options['sim_event_timer']
    
    @property
    def sim_config_path(self):
        return Path(self.__options['sim_config_path'])
    
    @property
    def sim_light_position(self):
        return Point3D.from_json(self.__options['sim_light_position'])
        
    @property
    def sim_data_path(self):
        return Path(self.__options['sim_data_path'])
    
    @property
    def sim_log_path(self):
        return Path(self.__options['sim_log_path'])
    
    @property
    def bn_model_path(self):
        return Path(self.__options['bn_model_path'])
    
    @property
    def bn_n(self):
        return self.__options['bn_n']
    
    @property
    def bn_k(self):
        return self.__options['bn_k']
    
    @property
    def bn_p(self):
        return self.__options['bn_p']
    
    @property
    def bn_inputs(self):
        return self.__options['bn_inputs']
    
    @property
    def bn_outputs(self):
        return self.__options['bn_outputs']
    
    # Setters #

    @webots_path.setter
    def webots_path(self, webots_path):
        self.__options['webots_path'] = str(webots_path)
    
    @webots_world_path.setter
    def webots_world_path(self, webots_world_path):
        self.__options['webots_world_path'] = str(webots_world_path)

    @webots_launch_args.setter
    def webots_launch_args(self, webots_launch_args):
        self.__options['webots_launch_args'] = webots_launch_args
    
    @webots_close_on_quit.setter
    def webots_close_on_quit(self, webots_close_on_quit):
        self.__options['webots_close_on_quit'] = webots_close_on_quit
    
    @sd_max_iters.setter
    def sd_max_iters(self, sd_max_iters):
        self.__options['sd_max_iters'] = sd_max_iters
    
    @sd_max_stalls.setter
    def sd_max_stalls(self, sd_max_stalls):
        self.__options['sd_max_stalls'] = sd_max_stalls
    
    @sim_time.setter
    def sim_time(self, sim_time):
        self.__options['sim_time'] = sim_time
    
    @sim_event_timer.setter
    def sim_event_timer(self, sim_event_timer):
        self.__options['sim_event_timer'] = sim_event_timer
    
    @sim_config_path.setter
    def sim_config_path(self, sim_config_path):
        self.__options['sim_config_path'] = str(sim_config_path)
    
    @sim_light_position.setter
    def sim_light_position(self, sim_light_position):

        if isinstance(sim_light_position, Point3D):
            self.__options['sim_light_position'] = sim_light_position.to_json()
        elif isinstance(sim_light_position, dict):
            self.__options['sim_light_position'] = sim_light_position
        else:
            self.__options['sim_light_position'] = Point3D.from_tuple(sim_light_position).to_json()

    @sim_data_path.setter
    def sim_data_path(self, sim_data_path):
        self.__options['sim_data_path'] = str(sim_data_path)
    
    @sim_log_path.setter
    def sim_log_path(self, sim_log_path):
        self.__options['sim_log_path'] = str(sim_log_path)
    
    @bn_model_path.setter
    def bn_model_path(self, bn_model_path):
        self.__options['bn_model_path'] = str(bn_model_path)
    
    @bn_n.setter
    def bn_n(self, bn_n):
        self.__options['bn_n'] = bn_n
    
    @bn_k.setter
    def bn_k(self, bn_k):
        self.__options['bn_k'] = bn_k
    
    @bn_p.setter
    def bn_p(self, bn_p):
        self.__options['bn_p'] = bn_p
    
    @bn_inputs.setter
    def bn_inputs(self, bn_inputs):
        self.__options['bn_inputs'] = bn_inputs
    
    @bn_outputs.setter
    def bn_outputs(self, bn_outputs):
        self.__options['bn_outputs'] = bn_outputs

    def to_json(self):
        return dict(self.__options)

    @staticmethod
    def from_json(json:dict):
        return SimulationConfig(json)

###########################################################################################

if __name__ == "__main__":

    parser = argparse.ArgumentParser('Create empty configuration file for simulation.')

    parser.add_argument('-p', '--path', type=Path, default='./default.json')

    args = parser.parse_args()

    config = SimulationConfig()

    with open(Path(args.path), 'w') as fp:
        json.dump(config.to_json(), fp, indent=4)