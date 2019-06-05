class Actuator:

    def __init__(self, label, name, device, position):
        self.__name = name
        self.__label = label
        self.__device = device
        self.__position = position
    
    @property
    def name(self):
        return self.__name
    @property
    def label(self):
        return self.__label
    @property
    def device(self):
        return self.__device
    @property
    def position(self):
        return self.__position

def actuators_array(labels:str, timestep:int, actuator_getter, actuators_positions = [0.0]): 
    ss = {}
    i = 0
    
    for k, name in labels.items():
        
        actuator = actuator_getter(name)
                
        ss.update({k:Actuator(k, name, actuator, actuators_positions[i])})

        if len(actuators_positions) > i+1 : i += 1
        
    return ss