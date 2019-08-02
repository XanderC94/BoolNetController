'''
Configuration class and utils module.
'''
from pathlib import Path
from collections import namedtuple
from bncontroller.jsonlib.utils import Jsonkin, FunctionWrapper
from bncontroller.jsonlib.utils import read_json, jsonrepr, objrepr, write_json
from bncontroller.collectionslib.utils import first
from bncontroller.sim.data import Point3D, ArenaParams, BNParams
from bncontroller.file.utils import iso8106, gen_fname, get_dir
from bncontroller.sim.robot.utils import DeviceName
from singleton_decorator import singleton

CONFIG_CLI_NAMES = ['-c', '-cp', '--config_path', '--config']

################################################################################################

DefaultOption = namedtuple(
    'DefaultOption', 
    [
        'value', 'type', 'alt', 'descr', 
        'serializer', 'deserializer'
    ],
    defaults=[None, None]
)

def empty(*args):
    raise Exception('Empty method called. Provide a real method.')

def normalize(defaults: dict, **kwargs):

    norm = dict()

    def r_update_internal_dict(defaults: dict, t, alt, **kwargs):
        norm = dict(**defaults)

        for k, v, in kwargs.items():
            norm.update({k: 
                r_update_internal_dict(d, t, alt, **v)
                if isinstance(v, dict) and isinstance(d, dict)
                else v
            })
    
        return norm

    for k, v, in kwargs.items():
        # print(k)
        try:
            d, t, alt = defaults[k].value, defaults[k].type, defaults[k].alt

            obj = objrepr(v, t, alt_type=alt)

            if isinstance(obj, dict) and isinstance(d, dict):
                norm.update({k: r_update_internal_dict(d, t, alt, **obj)})
            elif isinstance(obj, list) and isinstance(d, dict):
                norm.update({k: [
                    r_update_internal_dict(d, t, alt, **o)
                    if isinstance(o, dict) else o
                    for o in obj
                ]})
            else:
                norm.update({k: obj})

        except KeyError as ke:
            pass
    return norm

################################################################################################

class DefaultConfigOptions(Jsonkin):
    
    __def_options=dict(
        
        app_output_path=DefaultOption(
            value=Path('.'),
            type=Path,
            alt=None,
            descr='''Directory or file where to store the simulation general log'''
        ),
        app_core_function=DefaultOption(
            value=FunctionWrapper('bncontroller.sim.config::empty'),
            type=FunctionWrapper,
            alt=None,
            descr='''Core function called by main holding the experiment procedure'''
        ), #  
        eval_aggr_function=DefaultOption(
            value=FunctionWrapper('bncontroller.sim.config::empty'),
            type=FunctionWrapper,
            alt=None,
            descr='''value to which reduce the objective function'''
        ), #  
        
        # Simulator Launch Options #

        webots_path=DefaultOption(
            value=Path('.'),
            type=Path,
            alt=None,
            descr='''path to webots executable'''
        ),
        webots_world_path=DefaultOption(
            value=Path('.'),
            type=Path,
            alt=None,
            descr='''path to webots world file'''
        ),
        webots_launch_opts=DefaultOption(
            value=["--mode=fast", "--batch", "--minimize"],
            type=str,
            alt=None,
            descr='''simulator command line arguements'''
        ),
        webots_quit_on_termination=DefaultOption(
            value=True,
            type=bool,
            alt=None,
            descr='''quit simulator after simulation ends'''
        ),
        webots_nodes_defs=DefaultOption(
            value=dict(),
            type=str,
            alt=dict,
            descr='''simulation world node definitions (node custom names)'''
        ),
        webots_agent_controller=DefaultOption(
            value='none',
            type=str,
            alt=None,
            descr='''simulation world node definitions (node custom names)'''
        ),        
        webots_arena_size=DefaultOption(
            value=(3.0, 3.0),
            type=float,
            alt=tuple,
            descr='''simulation world arena size'''
        ),

        # Stochastic Descent Algorithm Control Parameters #

        sd_max_iters=DefaultOption(
            value=10000,
            type=int,
            alt=None,
            descr='''stochastic descent max iterations'''
        ),
        sd_min_flips=DefaultOption(
            value=1,
            type=int,
            alt=None,
            descr='''stochastic descent min flipped TT entries by iteration'''
        ),
        sd_max_stalls=DefaultOption(
            value=1,
            type=int,
            alt=None,
            descr='''-1 -> Adaptive Walk, 0+ -> VNS'''
        ),  
        sd_max_stagnation=DefaultOption(
            value=1250,
            type=int,
            alt=None,
            descr='''close the algorithm if no further improvement are found after i iteration'''
        ),
        sd_target_score=DefaultOption(
            value=0.0,
            type=float,
            alt=tuple,
            descr='''value to which reduce the objective function'''
        ), #  
        
        # Simulation Control Options #

        sim_run_time_s=DefaultOption(
            value=60,
            type=int,
            alt=None,
            descr='''execution time of the simulation in seconds'''
        ),
        sim_timestep_ms=DefaultOption(
            value=32,
            type=int,
            alt=None,
            descr='''simulation Loop synch time in ms'''
        ),
        sim_sensing_interval_ms=DefaultOption(
            value=320,
            type=int,
            alt=None,
            descr='''execution time of the simulation in milli-seconds'''
        ),
        sim_sensors_thresholds=DefaultOption(
            value={
                DeviceName.DISTANCE: 0.0,
                DeviceName.LIGHT: 0.0,
                DeviceName.LED: 0.0,
                DeviceName.TOUCH: 0.0,
                DeviceName.WHEEL_MOTOR: 0.0,
                DeviceName.WHEEL_POS: 0.0,
                DeviceName.GPS: 0.0,
            },
            type=float,
            alt=dict,
            descr='''sensors threshold to apply as binarization filters'''
        ),
        sim_event_timer_s=DefaultOption(
            value=-1,
            type=int,
            alt=None,
            descr='''perturbation event triggered after t seconds. if -1 => not triggered.'''
        ),
        sim_light_position=DefaultOption(
            value=Point3D(0.0, 0.0, 0.0),
            type=Point3D,
            alt=None,
            descr='''origin spawn point for light source'''
        ),
        sim_agent_position=DefaultOption(
            value=Point3D(0.0, 0.0, 0.0),
            type=Point3D,
            alt=None,
            descr='''origin Spawn point for agents'''
        ), 
        sim_agent_yrot_rad=DefaultOption(
            value=0.0,
            type=float,
            alt=None,
            descr='''agent spawn orientation'''
        ),
        sim_suppress_logging=DefaultOption(
            value=True,
            type=bool,
            alt=None,
            descr='''shut the simulation logger unit'''
        ),
        sim_config_path=DefaultOption(
            value=Path('.'),
            type=Path,
            alt=None,
            descr='''Directory or file where to store the simulation config'''
        ),
        sim_data_path=DefaultOption(
            value=Path('.'),
            type=Path,
            alt=None,
            descr='''Directory or file where to store the simulation data'''
        ),
        sim_log_path=DefaultOption(
            value=Path('.'),
            type=Path,
            alt=None,
            descr='''Directory or file where to store the simulation general log'''
        ),

        # Boolean Networks Generation Control Parameters #

        bn_ctrl_model_path=DefaultOption(
            value=Path('.'),
            type=Path,
            alt=None,
            descr='''Directory or file where to store the bn model'''
        ),
        # bn_ctrl_model_path=DefaultOption(
        #     value=Path('.'),
        #     type=Path,
        #     alt=None,
        #     descr='''Directory or file where to store the bn selector model'''
        # ),
        bn_n=DefaultOption(
            value=20,
            type=int,
            alt=None,
            descr='''boolean Network cardinality'''
        ),
        bn_k=DefaultOption(
            value=2,
            type=int,
            alt=None,
            descr='''boolean Network Node arity'''
        ),
        bn_p=DefaultOption(
            value=0.5,
            type=float,
            alt=None,
            descr='''truth table value bias'''
        ),
        bn_q=DefaultOption(
            value=0.5,
            type=float,
            alt=None,
            descr='''bn node intial state bias'''
        ),
        bn_n_inputs=DefaultOption(
            value=8,
            type=int,
            alt=None,
            descr='''number of nodes of the BN to be reserved as inputs'''
        ),
        bn_n_outputs=DefaultOption(
            value=2,
            type=int,
            alt=None,
            descr='''number of nodes of the BN to be reserved as outputs'''
        ),
        slct_behaviours_map=DefaultOption(
            value=dict(),
            type=Path,
            alt=dict,
            descr='''mapping attractor -> behaviour bn model path'''
        ),
        slct_target_n_attractors=DefaultOption(
            value=2,
            type=int,
            alt=None,
            descr='''number of wanted attractors'''
        ),
        slct_target_transition_rho=DefaultOption(
            value=dict(),
            type=float,
            alt=dict,
            descr='''probability to jump from an attractor to another different from itself.''',
        ),
        # slct_in_attr_map=DefaultOption(
        #     value=[
        #         [False],
        #         [True]
        #     ],
        # type=Path,    
        # alt=None,
        #     descr='''specifify the input values to apply to input nodes for that attractor'''
        # ),
        slct_noise_rho=DefaultOption(
            value=0.1,
            type=float,
            alt=None,
            descr='''Probability of noise to flip the state of a BN'''
        ),
        # slct_input_step_frac=DefaultOption(
        #     value=1/5,
        # type=Path,    
        # alt=None,
        #     descr='''Fractions of update steps (it) on each which apply inputs on input node.'''
        # ),
        slct_fix_input_steps=DefaultOption(
            value=1,
            type=int,
            alt=None,
            descr='''For how many steps the input should be enforced in the network (after each sensing)'''
        ),

        # Evaluation Parameters

        eval_agent_spawn_radius_m=DefaultOption(
            value=0.5,
            type=float,
            alt=None,
            descr='''spawn radius of the agent'''
        ), #
        eval_agent_offset_quadrant=DefaultOption(
            value='ANY',
            type=str,
            alt=None,
            descr='''spawn quadrant of the agent'''
        ), #
        eval_light_spawn_radius_m=DefaultOption(
            value=0.5,
            type=float,
            alt=None,
            descr='''spawn radius of the light point'''
        ),
        eval_light_offset_quadrant=DefaultOption(
            value='ANY',
            type=str,
            alt=None,
            descr='''spawn quadrant of the light point'''
        ),
        eval_n_agent_spawn_points=DefaultOption(
            value=1,
            type=int,
            alt=None,
            descr='''How many agent position to evaluate, If 0 uses always the same point (specified in sim_agent_position) to spawn the agent'''
        ),
        eval_n_light_spawn_points=DefaultOption(
            value=1,
            type=int,
            alt=None,
            descr='''How many light position to evaluate, If 0 uses always the same point (specified in sim_light_position) to spawn the light'''
        ),
        eval_agent_yrot_start_rad=DefaultOption(
            value=0.0,
            type=float,
            alt=None,
            descr='''From where to start sampling the yrot angles'''
        ),
        eval_agent_n_yrot_samples=DefaultOption(
            value=6,
            type=int,
            alt=None,
            descr='''Number of rotation to evaluate If 0 uses always the same value (specified in sim_agent_yrot_rad) to set the agent rotation'''
        ),
        
        # Model Test Control Parameters #

        plot_positives_threshold=DefaultOption(
            value=2e-06,
            type=float,
            alt=None,
            descr='''Specify a score threshold under which model are considered "good"'''
        ),
        test_data_path=DefaultOption(
            value=Path('.'),
            type=Path,
            alt=None,
            descr='''Path where to store / read test data'''
        ),
        test_n_instances=DefaultOption(
            value=1,
            type=int,
            alt=None,
            descr='''# number of instances of the test cycle for each bn'''
        ),
        # test_aggr_function=DefaultOption(
        #     value=FunctionWrapper('bncontroller.sim.config::empty'),
        # type=Path,    
        # alt=None,
        #     descr='''how test parameters should be aggregated in the test loop'''
        # ),
        
        # Train control parameters#

        train_save_suboptimal_models=DefaultOption(
            value=2e-06,
            type=float,
            alt=tuple,
            descr='''save bn model with score under the specified threshold'''
        ),
        train_generate_only=DefaultOption(
            value=False,
            type=bool,
            alt=None,
            descr='''Only generate training bn without running SD'''
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

class Config(Jsonkin):
    '''      
    app_output_path -- Directory or file where to store the simulation general log
    webots_path -- path to webots executable
    webots_world_path -- path to webots world file
    webots_launch_opts -- simulator command line arguements
    webots_quit_on_termination -- quit simulator after simulation ends
    webots_nodes_defs -- simulation world node definitions (node custom names)
    webots_agent_controller -- simulation world node definitions (node custom names)
    webots_arena_size -- simulation world arena size
    sd_max_iters -- stochastic descent max iterations
    sd_min_flips -- stochastic descent min flipped TT entries by iteration
    sd_max_stalls -- -1 -> Adaptive Walk, 0+ -> VNS
    sd_max_stagnation -- close the algorithm if no further improvement are found after i iteration
    sd_target_score -- value to which reduce the objective function
    app_core_function -- value to which reduce the objective function
    sim_run_time_s -- execution time of the simulation in seconds
    sim_timestep_ms -- simulation Loop synch time in ms
    sim_sensing_interval_ms -- execution time of the simulation in milli-seconds
    sim_sensors_thresholds -- sensors threshold to apply as binarization filters
    sim_event_timer_s -- perturbation event triggered after t seconds. if -1 => not triggered.
    sim_light_position -- origin spawn point for light source
    sim_agent_position -- origin Spawn point for agents
    sim_agent_yrot_rad -- agent spawn orientation
    sim_suppress_logging -- shut the simulation logger unit
    sim_config_path -- Directory or file where to store the simulation config
    sim_data_path -- Directory or file where to store the simulation data
    sim_log_path -- Directory or file where to store the simulation general log
    bn_ctrl_model_path -- Directory or file where to store the bn model
    bn_ctrl_model_path -- Directory or file where to store the bn selector model
    bn_n -- boolean Network cardinality
    bn_k -- boolean Network Node arity
    bn_p -- truth value bias
    bn_n_inputs -- number or List of nodes of the BN to be reserved as inputs
    bn_n_outputs -- number or List of nodes of the BN to be reserved as outputs
    slct_target_n_attractors -- number of wanted attractors
    slct_target_transition_rho -- probability to jump from an attractor to another different from itself.
    slct_noise_rho -- Probability of noise to flip the state of a BN
    slct_fix_input_steps --
                For how many steps the input should be enforced in the network
                (after each sensing)

    eval_agent_spawn_radius_m -- spawn radius of the agent
    eval_light_spawn_radius_m -- spawn radius of the light point
    eval_n_agent_spawn_points -- How many agent position to evaluate, If 0 uses always the same point (specified in sim_agent_position) to spawn the agent
    eval_n_light_spawn_points -- How many light position to evaluate, If 0 uses always the same point (specified in sim_light_position) to spawn the light
    eval_agent_yrot_start_rad -- From where to start sampling the yrot angles
    eval_agent_n_yrot_samples -- Number of rotation to evaluate If 0 uses always the same value (specified in sim_agent_yrot_rad) to set the agent rotation
    plot_positives_threshold -- Specify a score threshold under which model are considered "good"
    test_data_path -- Path where to store / read test data
    test_n_instances -- # number of instances of the test cycle for each bn
    test_aggr_function -- how test parameters should be aggregated in the test loop
    train_save_suboptimal_models -- save bn model with score under the specified threshold
    train_generate_only -- Only generate training bn without running SD
    app --
    '''

    def __init__(self, **kwargs):

        options = DefaultConfigOptions.default()

        options.update(normalize(DefaultConfigOptions.options(), **kwargs))

        self.app_output_path = options['app_output_path']
        self.app_core_function = options['app_core_function']

        # Webots #
        self.webots_path = options['webots_path']
        self.webots_world_path = options['webots_world_path']
        self.webots_launch_opts = options['webots_launch_opts']
        self.webots_quit_on_termination = options['webots_quit_on_termination']
        self.webots_nodes_defs = options['webots_nodes_defs']
        self.webots_agent_controller = options['webots_agent_controller']
        self.webots_arena_size = options['webots_arena_size']

        # Stochastic Descent Search
        self.sd_max_iters = options['sd_max_iters']
        self.sd_min_flips = options['sd_min_flips']
        self.sd_max_stalls = options['sd_max_stalls']
        self.sd_max_stagnation = options['sd_max_stagnation']
        self.sd_target_score = options['sd_target_score']

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
        self.bn_ctrl_model_path = options['bn_ctrl_model_path']
        # self.bn_ctrl_model_path = options['bn_ctrl_model_path']
        self.bn_n = options['bn_n']
        self.bn_k = options['bn_k']
        self.bn_p = options['bn_p']
        self.bn_q = options['bn_q']
        self.bn_n_inputs = options['bn_n_inputs']
        self.bn_n_outputs = options['bn_n_outputs']
        self.slct_behaviours_map = options['slct_behaviours_map']
        self.slct_target_n_attractors = options['slct_target_n_attractors']
        self.slct_target_transition_rho = options['slct_target_transition_rho']
        # self.slct_in_attr_map = options['slct_in_attr_map']
        self.slct_noise_rho = options['slct_noise_rho']
        # self.slct_input_step_frac = options['slct_input_step_frac']
        self.slct_fix_input_steps = options['slct_fix_input_steps']

        # Evaluation Parameters
        self.eval_aggr_function = options['eval_aggr_function']
        self.eval_light_spawn_radius_m = options['eval_light_spawn_radius_m']
        self.eval_light_offset_quadrant = options['eval_light_offset_quadrant'].upper()
        self.eval_agent_spawn_radius_m = options['eval_agent_spawn_radius_m']
        self.eval_agent_offset_quadrant = options['eval_agent_offset_quadrant'].upper()
        self.eval_n_agent_spawn_points = options['eval_n_agent_spawn_points']
        self.eval_n_light_spawn_points = options['eval_n_light_spawn_points']
        self.eval_agent_yrot_start_rad = options['eval_agent_yrot_start_rad']
        self.eval_agent_n_yrot_samples = options['eval_agent_n_yrot_samples']

        # Test #
        self.plot_positives_threshold = options['plot_positives_threshold']
        self.test_data_path = options['test_data_path']
        self.test_n_instances = options['test_n_instances']
        # self.test_aggr_function = options['test_aggr_function']

        # Train #
        self.train_save_suboptimal_models = options['train_save_suboptimal_models']
        self.train_generate_only = options['train_generate_only']

        pass

    def to_json(self) -> dict:
        return dict((k, jsonrepr(v)) for k, v in vars(self).items())
    
    @staticmethod
    def from_json(json):
        return Config(**json)

    def to_file(self, fp: Path or str):
        write_json(self.to_json(), fp, indent=True)

    @staticmethod
    def from_file(fp: Path or str):
        return Config(**read_json(fp))

    @property
    def arena_params(self):
        return ArenaParams(
            floor_size=self.webots_arena_size,
            sim_config=self.sim_config_path,
            controller=self.webots_agent_controller,
        )

    @property
    def bn_params(self):
        return BNParams(
            N=self.bn_n,
            K=self.bn_k,
            P=self.bn_p,
            Q=self.bn_q,
            I=self.bn_n_inputs,
            O=self.bn_n_outputs
        )
    
    @bn_params.setter
    def bn_params(self, params: BNParams or tuple):
        
        N, K, P, Q, I, O = params

        self.bn_n = N
        self.bn_k = K
        self.bn_p = P
        self.bn_q = Q
        self.bn_n_inputs = I 
        self.bn_n_outputs = O