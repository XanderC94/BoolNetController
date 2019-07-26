import random
from pathlib import Path
from typing import Dict
from collections import defaultdict
from bncontroller.jsonlib.utils import read_json, json
from bncontroller.sim.data import SimulationStepData, Point3D
from bncontroller.sim.robot.utils import DeviceName
from bncontroller.sim.robot.morphology import EPuckMorphology
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.boolnet.selector import BoolNetSelector
from bncontroller.boolnet.utils import binstate, compact_state

class Controller(object):

    def __init__(self):
        pass

    def __call__(self, *args) -> SimulationStepData:
        pass

class BNController(Controller):

    def __init__(self, 
            model: OpenBooleanNetwork or Path, 
            bin_thresholds: dict, bin_strategies: dict,
            sensing_interval: int):

        self.__bn = model if isinstance(model, OpenBooleanNetwork) else OpenBooleanNetwork.from_json(read_json(model))
        self.__bin_strategies = bin_strategies
        self.__bin_thresholds = bin_thresholds
        self.__sensing_interval = sensing_interval
        self.__next_sensing = 0
        
        self.gps_data = []
        self.distance_data = []
        self.light_data = []
        self.touch_data = []
    
    def __call__(self, morphology: EPuckMorphology, step: int, timestep: int) -> SimulationStepData:

        # BN update is faster than sensor sampling frequency

        if self.__next_sensing == step:

            self.__next_sensing += int(self.__sensing_interval / timestep)

            # Retreive Sensors Data
            self.gps_data = [Point3D.from_tuple(g.read()) for g in morphology.GPSs.values()]

            # receiver_data = []
            
            # for r in morphology.receiver.values():
            #     while r.device.getQueueLength() > 0:
            #         receiver_data.append(r.device.getData())
            #         r.device.nextPacket()
            # if receiver_data:
            #     print(receiver_data)
            
            # self.distance_data = [d.device.getValue() for d in morphology.distance_sensors.values()]
            self.light_data = dict((k, l.read()) for k, l in morphology.light_sensors.items())
            # touch_data = [t.device.getValues() for t in morphology.touch.values()]

            # print(self.gps_data)
            # print(distance_data)
            # print(self.light_data)
            # print(touch_data)

        # Apply Binarization Strategies
        bin_light_data = self.__bin_strategies[DeviceName.LIGHT](
            self.light_data, 
            self.__bin_thresholds[DeviceName.LIGHT]
        )

        # "Perturbate" network based on binarized values
        # This should be applied each time on input nodes
        for l in self.__bn.input_nodes:
            self.__bn[l].state = bin_light_data[l]
            
            # print(self.__bn.state)
    
        # Update network state
        bn_state = self.__bn.update()

        # print(bn_state)

        # Apply Network Output to actuators
        lv, rv, *_ = [value for l, value in bn_state.items() if l in self.__bn.output_nodes] 

        # print(lv, rv)

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

class DualHBNController(Controller):

    def __init__(self,
            selector: BoolNetSelector,
            behaviours: Dict[str, BNController],
            input_fixation_steps: int,
            sensing_interval: int):

        self.__selector = selector
        self.__behaviours = behaviours

        self.__attractors = self.__selector.atm.dattractors
        self.__curr_attr = None
        self.__atm = self.__selector.atm.dtableau

        self.__bmap = defaultdict(
            self.__default_behaviour_strategy, 
            [
                (binstate(s), self.__behaviours[k])
                for k, attr in self.__attractors
                for s in attr
            ]
        ) 

        self.__sensing_interval = sensing_interval
        self.__input_fixation_steps = input_fixation_steps
        self.__next_sensing = 0
        self.__input_fixed_for = 0

        self.__msg_buffer = []

    def __default_behaviour_strategy(self):

        if self.__curr_attr is None:
            self.__curr_attr = random.choice(self.__attractors.keys())
            return self.__behaviours[self.__curr_attr]
        else:
            a = self.__atm[self.__curr_attr].keys()
            w = self.__atm[self.__curr_attr].values()
            self.__curr_attr = random.choices(a, w)
            return self.__behaviours[self.__curr_attr]

    def __call__(self, morphology: EPuckMorphology, step: int, timestep: int):

        # BN update is faster than sensor sampling frequency
        if self.__next_sensing == step:

            self.__next_sensing += int(self.__sensing_interval / timestep)

            r = morphology.receivers[-1]

            if r.device.getQueueLength() > 0:
                self.__input_fixed_for = 0
                while r.device.getQueueLength() > 0:
                    self.__msg_buffer.append(r.device.getData())
                    r.device.nextPacket()

        if self.__input_fixed_for < self.__input_fixation_steps:
            for l in self.__selector.input_nodes:
                self.__selector[l].state = len(self.__msg_buffer) == 0
                self.__input_fixed_for += 1
         
        self.__msg_buffer.clear()

        # Update network state
        bn_state = self.__selector.update()

        attractor = self.__bmap[binstate(bn_state)]

        return self.__behaviours[attractor](morphology, step, timestep)