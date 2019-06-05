class Sensor:

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

def sensor_array(labels:str, timestep:int, sensor_getter, sensors_positions = [0.0], enable_sensors = True): 
    ss = {}
    i = 0
    
    for k, name in labels.items():
        # print(name)
        sensor = sensor_getter(name)
        
        if (enable_sensors) : sensor.enable(timestep)
        
        ss.update({k:Sensor(k, name, sensor, sensors_positions[i])})

        if len(sensors_positions) > i+1 : i += 1
        
    return ss