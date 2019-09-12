from controller import Robot
from bncontroller.sim.robot.utils import EPuckDevicesLabels
from bncontroller.sim.robot.sensor import sensor_array
from bncontroller.sim.robot.actuator import actuators_array
from math import pi

class EPuckMorphology(object):
    
    LEFT, RIGHT = 'left', 'right'

    WHEEL_RADIUS = 0.02 # meters
    AXLE_LENGTH = 0.052 # meters

    RANGE = float(1024 / 2)

    PI = pi
    EPUCK_FRONT_RAD = PI / 2
    EPUCK_FRONT_DEG = EPUCK_FRONT_RAD * 180 / PI
    W_WHEEL = 2 * PI
    MAX_V = 7.536 # 1200 step / second
    MIN_V = PI / 4

    N_LEDS = 10
    N_DISTANCE_SENSORS = 8
    N_LIGHT_SENSORS = 8
    N_WHEELS = [LEFT, RIGHT]
    N_BUMPERS = 8
    N_GPS = 1
    N_RECEVIER = 1
    N_EMITTERS = 1

    # LIGHT_SENSORS_POSITION = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87, 1.58784]
    DISTANCE_SENSORS_POSITION = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]
    WHEEL_ACTUATORS_POSITION = [0.0, 3.14159]
    LIGHT_SENSORS_POSITION = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]

    def __init__(self, timestep: int, bot: Robot):
        
        # self.light_sensors_positions = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87, 1.58784]
        # self.distance_sensors_positions = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]
        # self.wheel_actuators_positions = [0.0, 3.14159]
        # self.bump_sensors_positions = [1.27, 0.77, 0.0, 5.21, 4.21, 3.14159, 2.37, 1.87]

        self.__devices_labels = EPuckDevicesLabels(
            self.N_DISTANCE_SENSORS, 
            self.N_LIGHT_SENSORS, 
            self.N_BUMPERS, 
            self.N_LEDS,
            self.N_WHEELS
        )

        #Retrieve device references
        self.__led_actuators = actuators_array(
            self.__devices_labels.led_actuators_labels, 
            timestep, 
            lambda name: bot.getLED(name)
        )

        self.__wheel_actuators = actuators_array(
            self.__devices_labels.wheel_actuators_labels, 
            timestep, 
            lambda name: bot.getMotor(name),
            actuators_positions=self.WHEEL_ACTUATORS_POSITION
        )

        self.__distance_sensors = sensor_array(
            self.__devices_labels.distance_sensors_labels, 
            timestep, 
            lambda name: bot.getDistanceSensor(name),
            sensors_positions=self.DISTANCE_SENSORS_POSITION
        )

        self.__light_sensors = sensor_array(
            self.__devices_labels.light_sensors_labels, 
            timestep, 
            lambda name: bot.getLightSensor(name),
            sensors_positions=self.LIGHT_SENSORS_POSITION
        )

        # self.__bumpers = sensor_array(
        #     self.__devices_labels.bump_sensors_labels, 
        #     timestep, 
        #     lambda name: bot.getTouchSensor(name),
        #     sensors_positions = self.bump_sensors_positions
        # )

        self.__gps = sensor_array(
            self.__devices_labels.gps_sensors_labels, 
            timestep, 
            lambda name: bot.getGPS(name),
            sensors_positions=[0.0]
        )

        self.__emitters = actuators_array(
            self.__devices_labels.emitter_labels, 
            timestep, 
            lambda name: bot.getEmitter(name),
            actuators_positions=[0.0]
        )

        self.__receivers = sensor_array(
            self.__devices_labels.receiver_labels, 
            timestep, 
            lambda name: bot.getReceiver(name),
            sensors_positions=[0.0]
        )

    @property
    def wheel_actuators(self):  
        return self.__wheel_actuators
    
    @property
    def distance_sensors(self):  
        return self.__distance_sensors
    
    @property
    def light_sensors(self):  
        return self.__light_sensors
    
    @property
    def led_actuators(self):  
        return self.__led_actuators
    
    # @property
    # def bump_sensors(self):  
    #     return self.__bumpers

    @property
    def GPSs(self):  
        return self.__gps

    @property
    def receivers(self):  
        return self.__receivers

    @property
    def emitters(self):  
        return self.__emitters
