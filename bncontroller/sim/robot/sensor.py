from collections import defaultdict

class Sensor(object):

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

    def read(self):
        if hasattr(self.device, 'getValues'):
            return self.device.getValues()
        elif hasattr(self.device, 'getValue'):
            return self.device.getValue()
        else:
            raise Exception('Unreadable Sensor.')

def sensor_array(labels: dict, timestep: int, sensor_getter, sensors_positions = [0.0]):
    
    ss = defaultdict(type(None))
    i = 0
    
    for k, name in labels.items():
        # print(name)
        sensor = sensor_getter(name)
        
        if hasattr(sensor, 'enable'): 
            sensor.enable(timestep)
        
        ss.update({k:Sensor(k, name, sensor, sensors_positions[i])})

        if len(sensors_positions) > i+1 : i += 1
        
    return ss