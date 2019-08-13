import random
from pathlib import Path
from typing import Dict, Callable
from collections import defaultdict
from bncontroller.sim.data import SimulationStepData, Point3D
from bncontroller.sim.robot.utils import DeviceName
from bncontroller.sim.robot.morphology import EPuckMorphology
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.boolnet.boolean import TRUTH_VALUES
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.boolnet.utils import binstate, compact_state
from bncontroller.collectionslib.utils import transpose

class Controller(object):

    def __init__(self):
        pass

    def __call__(self, *args) -> SimulationStepData:
        pass

class BNController(Controller):

    def __init__(self, 
            model: OpenBooleanNetwork, 
            bin_strategies: dict,
            bin_thresholds: dict, 
            sensing_interval: int,
            led_color: int=0xff0000):

        self.__bn = model
        self.__bin_strategies = bin_strategies
        self.__bin_thresholds = bin_thresholds
        self.__sensing_interval = sensing_interval
        self.__next_sensing = 0

        self.gps_data = []
        self.distance_data = []
        self.light_data = []
        self.touch_data = []

        self.led_color = led_color
    
    def __call__(self, morphology: EPuckMorphology, step: int, timestep: int, force_sensing=False) -> SimulationStepData:

        # BN update is faster than sensor sampling frequency
        
        for k, led in morphology.led_actuators.items():
            # print(k, led.device)
            led.device.set(self.led_color)

        if self.__next_sensing == 0 or self.__next_sensing == step or force_sensing:
            
            self.__next_sensing += int(self.__sensing_interval / timestep)

            # Retreive Sensors Data
            self.gps_data = [Point3D.from_tuple(g.read()) for g in morphology.GPSs.values()]

            self.light_data = dict((k, l.read()) for k, l in morphology.light_sensors.items())

        # Apply Binarization Strategies
        
        bin_light_data = self.__bin_strategies[DeviceName.LIGHT](
            self.light_data, 
            self.__bin_thresholds[DeviceName.LIGHT]
        )

        # "Perturbate" network based on binarized values
        # This should be applied each time on input nodes
        for l in self.__bn.input_nodes:
            self.__bn[l].state = bin_light_data[l]
        

        # Update network state
        bn_state = self.__bn.update()

        # Apply Network Output to actuators
        lv, rv, *_ = [self.__bn[k].state for k in sorted(self.__bn.output_nodes)] 

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

class HBNAController(Controller):

    def __init__(self,
            selector: SelectiveBooleanNetwork,
            behaviours: Dict[str, BNController],
            bin_strategies : Dict[str, Callable[[dict, float], dict]],
            bin_thresholds : Dict[str, float],
            noise_rho: float,
            input_fixation_steps: int,
            sensing_interval: int):

        self.__selector = selector
        self.__behaviours = behaviours


        self.__bin_strategies = bin_strategies
        self.__bin_thresholds = bin_thresholds

        self.__attractors = self.__selector.atm.dattractors
        self.__curr_attr = None
        self.__atm = self.__selector.atm.dtableau

        self.__bmap = defaultdict(
                self.__default_behaviour_strategy,
                [
                    (binstate(s), k)
                    for k, attr in self.__attractors.items()
                    for s in attr
                ]
            )
        
        print(self.__behaviours)

        self.__signal = -1 # True # 

        for k in self.__selector.keys:
            self.__selector[k].state = random.choice([True, False]) # self.__signal # 

        self.__sensing_interval = sensing_interval
        self.__noise_rho = noise_rho
        self.__input_fixation_steps = input_fixation_steps
        self.__next_sensing = 0
        self.__input_fixed_for = 0

        self.__light_data = []

    def __default_behaviour_strategy(self):

        if self.__curr_attr is None:
            return random.choice([*self.__attractors.keys()])
        else:
            a, w = transpose(self.__atm[self.__curr_attr].items())
            return random.choices(a, w)[0]

    def __call__(self, morphology: EPuckMorphology, step: int, timestep: int):

        # BN update is faster than sensor sampling frequency
        sensed = False
        
        if self.__next_sensing == step:
            
            sensed = True

            self.__next_sensing += int(self.__sensing_interval / timestep)

            # Collect light data            
            self.__light_data = dict((k, l.read()) for k, l in morphology.light_sensors.items())

            # print(self.__light_data)

            # Collect Radio messages
            r = morphology.receivers[-1]

            if r.device.getQueueLength() > 0:
                
                pkt = int(r.device.getData(), 2)

                self.__input_fixed_for = 0
                self.__signal = pkt
                               
                while r.device.getQueueLength() > 0:
                    r.device.nextPacket()
                
                print(f"Env. signal {pkt} received.")

        if self.__signal != -1:

            if self.__input_fixed_for < self.__input_fixation_steps:
                # print('F')
                for l in self.__selector.input_nodes:
                    self.__selector[l].state = self.__signal
                    # print(l, self.__selector[l].state)
                    self.__input_fixed_for += 1
            pass
        else:
            # Apply random noise
            # print('Noise')

            # Apply Binarization Strategies
            bin_light_data = self.__bin_strategies[DeviceName.LIGHT](
                self.__light_data, 
                self.__bin_thresholds[DeviceName.LIGHT]
            )
            
            noise_rho = sum(bin_light_data.values()) / len(bin_light_data)
            noise_rho = max(self.__noise_rho, noise_rho)

            k = random.randint(1, max(1, sum(bin_light_data.values())))
            
            nodes = random.choices(self.__selector.keys, k=k)
            
            for n in nodes:
                apply_noise = random.choices(TRUTH_VALUES, [noise_rho, 1.0 - noise_rho])[0]
                
                if apply_noise:
                    self.__selector[n].state = not self.__selector[n].state
            pass

        # Update network state
        bn_state = self.__selector.update()
        self.__curr_attr = self.__bmap[binstate(bn_state)]
        
        # print(self.__selector.attractors_input_map)
        # print(self.__curr_attr)

        cdata = self.__behaviours[self.__curr_attr](morphology, step, timestep, sensed)

        cdata.noise = self.__signal == -1
        cdata.attr = self.__curr_attr
        cdata.input = self.__signal

        return cdata