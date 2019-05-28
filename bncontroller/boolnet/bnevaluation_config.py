import json, argparse, sys
from pathlib import Path

class EvaluationConfig(object):

    def __init__(self, options: dict = {}):

        self.__def_options = {
            'webots_path': str(Path('')), # Path to webots executable
            'webots_world_path': str(Path('')), # Path to webots world file
            'webots_launch_args': ["--mode=fast", "--batch"],
            'sd_max_iters': 10000, # stochastic descent max iterations
            'sd_max_stall': 1, # 1 -> Adaptive Walk, 2+ -> VNS 
            'sym_event_timer': 10, # Perturbation event triggered after t seconds
            'sym_data_dir': str(Path('')), # Directory where to store the simulation data
            'sym_time': 10, # Execution time of the simulation in seconds
            'sym_log_dir': str(Path('')), # Directory where to store the simulation general log
            'bn_model_dir': str(Path('')), # Directory where to store the bn model
            'bn_n': 20, # Boolean Network cardinality
            'bn_k': 2, # Boolean Network Node a-rity
            'bn_p': 0.5, # Truth value bias
            'bn_inputs': 8, # Number of nodes of the BN to be reserved as inputs
            'bn_outputs': 2 # Number of nodes of the BN to be reserved as outputs
        }

        self.__options = dict(self.__def_options)

        self.__options.update(options)

    def webots_path(self):
        return Path(self.__options['webots_path'])
    
    def webots_world_path(self):
        return Path(self.__options['webots_world_path'])
    
    def webots_launch_args(self):
        return self.__options['webots_launch_args']
    
    def sd_max_iters(self):
        return self.__options['sd_max_iters']
    
    def sd_max_stall(self):
        return self.__options['sd_max_stall']
    
    def sym_event_timer(self):
        return self.__options['sym_event_timer']
    
    def sym_data_dir(self):
        return Path(self.__options['sym_data_dir'])
    
    def sym_time(self):
        return self.__options['sym_time']
    
    def sym_log_dir(self):
        return Path(self.__options['sym_log_dir'])

    def bn_model_dir(self):
        return Path(self.__options['bn_model_dir'])

    def bn_n(self):
        return self.__options['bn_n']

    def bn_k(self):
        return self.__options['bn_k']

    def bn_p(self):
        return self.__options['bn_p']

    def to_json(self):
        return self.__options

    @staticmethod
    def from_json(json:dict):
        return EvaluationConfig(json)

if __name__ == "__main__":

    parser = argparse.ArgumentParser('Create empty configuration file for simulation.')

    parser.add_argument('-p', '--path', type=Path, default='./default.json', nargs=1, required=False)

    args = parser.parse_args()

    config = EvaluationConfig()

    with open(args.path, 'w') as fp:
        json.dump(config.to_json(), fp, indent=4)