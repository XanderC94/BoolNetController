from bncontroller.sim.config import SimulationConfig
from bncontroller.sim.robot.morphology import EPuckMorphology
from bncontroller.sim.data import SimulationStepData, Point3D
from bncontroller.boolnet.bnstructures import BooleanNetwork
from bncontroller.json.utils import read_json

class Controller(object):

    def __init__(self):
        pass

    def __call__(self, *args) -> SimulationStepData:
        pass

class BNController(Controller):

    def __init__(self, config: SimulationConfig, binarization_strategies = {}):
        self.__config = config
        self.__bn = BooleanNetwork.from_json(read_json(config.bn_model_path))
        self.__bin_strategies = binarization_strategies
        self.__next_sensing = 0
        self.input_nodes = list(map(str, range(config.bn_inputs)))
        self.output_nodes = list(map(str, range(config.bn_inputs, config.bn_inputs + config.bn_outputs)))

        self.gps_data = []
        self.distance_data = []
        self.light_data = []
        self.touch_data = []
    
    def __call__(self, morphology: EPuckMorphology, step: int, timestep: int) -> SimulationStepData:

        # BN update is faster than sensor sampling frequency

        if self.__next_sensing == step:

            self.__next_sensing += int(self.__config.sim_sensing_interval / timestep)

            # Retreive Sensors Data
            self.gps_data = [Point3D.from_tuple(g.device.getValues()) for g in morphology.gps.values()]
            self.distance_data = [d.device.getValue() for d in morphology.distance_sensors.values()]
            self.light_data = [label.device.getValue() for label in morphology.light_sensors.values()]
            # touch_data = [t.device.getValues() for t in morphology.touch.values()]

            # print(self.gps_data)
            # print(distance_data)
            # print(self.light_data)
            # print(touch_data)

            # Apply Binarization Strategies

            bin_light_data = self.__bin_strategies['light'](self.light_data)

            # Perturbate network based on binarized values

            for label, value in zip(self.input_nodes, bin_light_data):
                self.__bn[label].state = value
                # self.__bn[str(label)].bf(tuple([value]))
            
            # print(self.__bn.state)
    
        # Update network state
        bn_state = self.__bn.step()

        # Apply Network Output to actuators
        lv, rv, *_ = [value for label, value in bn_state.items() if label in self.output_nodes] 

        morphology.wheel_actuators['left'].device.setVelocity(lv)
        morphology.wheel_actuators['right'].device.setVelocity(rv)

        return SimulationStepData(
                step, 
                self.gps_data[0], 
                bn_state, 
                self.light_data, 
                self.distance_data, 
                self.touch_data
            )
