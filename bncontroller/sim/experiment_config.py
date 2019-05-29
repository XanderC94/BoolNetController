import json, argparse, sys
from pathlib import Path
from bncontroller.json_utils import Jsonkin
from bncontroller.sim.data import Point3D

class ExperimentConfig(Jsonkin):

    def __init__(self, options: dict = {}):

        self.__def_options = {
            'webots_path': Path(''), # Path to webots executable
            'webots_world_path': Path(''), # Path to webots world file
            'webots_launch_args': ["--mode=fast", "--batch"],
            'webots_close_on_quit': True,
            'sd_max_iters': 10000, # stochastic descent max iterations
            'sd_max_stalls': 1, # 1 -> Adaptive Walk, 2+ -> VNS 
            'sim_time': 10, # Execution time of the simulation in seconds
            'sim_event_timer': 10, # Perturbation event triggered after t seconds
            'sim_light_position': Point3D(0.0,0.0,0.0),
            'sim_config_path': Path(''), # Directory or file where to store the simulation config
            'sim_data_path': Path(''), # Directory or file where to store the simulation data
            'sim_log_path': Path(''), # Directory or file where to store the simulation general log
            'bn_model_path': Path(''), # Directory or file where to store the bn model
            'bn_n': 20, # Boolean Network cardinality
            'bn_k': 2, # Boolean Network Node a-rity
            'bn_p': 0.5, # Truth value bias
            'bn_inputs': 8, # Number or List of nodes of the BN to be reserved as inputs
            'bn_outputs': 2 # Number or List of nodes of the BN to be reserved as outputs
        }

        _options = dict(self.__def_options)
        _options.update(options)

        self.webots_path=Path(_options['webots_path'])
        self.webots_world_path=Path(_options['webots_world_path'])
        self.webots_launch_args=_options['webots_launch_args']
        self.webots_close_on_quit=_options['webots_close_on_quit']
        self.sd_max_iters=_options['sd_max_iters']
        self.sd_max_stalls=_options['sd_max_stalls'] 
        self.sim_time=_options['sim_time'] 
        self.sim_event_timer=_options['sim_event_timer'] 
        if isinstance(_options['sim_light_position'], Point3D):
            self.sim_light_position=_options['sim_light_position']  
        else:
            self.sim_light_position=Point3D.from_json(_options['sim_light_position'])
        self.sim_config_path=Path(_options['sim_config_path'])
        self.sim_data_path=Path(_options['sim_data_path'])
        self.sim_log_path=Path(_options['sim_log_path'])
        self.bn_model_path=Path(_options['bn_model_path'])
        self.bn_n=_options['bn_n']
        self.bn_k=_options['bn_k']
        self.bn_p=_options['bn_p']
        self.bn_inputs=_options['bn_inputs']
        self.bn_outputs=_options['bn_outputs'] 

    def to_json(self):
        return {
            'webots_path':str(self.webots_path),
            'webots_world_path':str(self.webots_world_path),
            'webots_launch_args':self.webots_launch_args,
            'webots_close_on_quit':self.webots_close_on_quit,
            'sd_max_iters':self.sd_max_iters,
            'sd_max_stalls':self.sd_max_stalls,
            'sim_time':self.sim_time,
            'sim_event_timer':self.sim_event_timer,
            'sim_light_position':self.sim_light_position.to_json(),
            'sim_config_path':str(self.sim_config_path),
            'sim_data_path':str(self.sim_data_path),
            'sim_log_path':str(self.sim_log_path),
            'bn_model_path':str(self.bn_model_path),
            'bn_n':self.bn_n,
            'bn_k':self.bn_k,
            'bn_p':self.bn_p,
            'bn_inputs':self.bn_inputs,
            'bn_outputs':self.bn_outputs,
        }

    @staticmethod
    def from_json(json:dict):
        return ExperimentConfig(json)

if __name__ == "__main__":

    parser = argparse.ArgumentParser('Create empty configuration file for simulation.')

    parser.add_argument('-p', '--path', type=Path, default='./default.json')

    args = parser.parse_args()

    config = ExperimentConfig()

    with open(Path(args.path), 'w') as fp:
        json.dump(config.to_json(), fp, indent=4)