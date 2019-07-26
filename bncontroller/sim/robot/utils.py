from collections import namedtuple

DeviceName = namedtuple(
    'DeviceName', 
    ['DISTANCE', 'LIGHT', 'LED', 'TOUCH', 'WHEEL_MOTOR', 'WHEEL_POS', 'GPS', 'RECEIVER', 'EMITTER'],
    defaults=['ps', 'ls', 'led', 'bs', 'wheel motor', 'wheel sensor', 'gps', 'receiver', 'emitter']
)()

class EPuckDevicesLabels(object):

    def __init__(self,
            n_distance_sensors,
            n_light_sensors,
            n_bumpers,
            n_leds,
            n_wheels):

        self.distance_sensor_template = ''.join([DeviceName.DISTANCE, '{id}'])
        self.light_sensor_template = ''.join([DeviceName.LIGHT, '{id}'])
        self.led_actuator_template = ''.join([DeviceName.LED, '{id}'])
        self.touch_sensor_template = ''.join([DeviceName.TOUCH, '{id}'])
        self.wheel_actuator_template = ' '.join(['{id}', DeviceName.WHEEL_MOTOR])
        self.wheel_position_template = ' '.join(['{id}', DeviceName.WHEEL_POS])
        self.gps_template = DeviceName.GPS
        self.receiver_template = DeviceName.RECEIVER
        self.emitter_template = DeviceName.EMITTER

        self.distance_sensors_labels = produce_labels(self.distance_sensor_template, n_distance_sensors)
        self.light_sensors_labels = produce_labels(self.light_sensor_template, n_light_sensors)
        self.bump_sensors_labels = produce_labels(self.touch_sensor_template, n_bumpers)
        self.wheel_position_sensors_labels = produce_labels(self.wheel_position_template, n_wheels)
        self.gps_sensors_labels = {-1: self.gps_template}
        self.receiver_labels = {-1: self.receiver_template}
        self.emitter_labels = {-1: self.emitter_template}
        
        self.led_actuators_labels = produce_labels(self.led_actuator_template, n_leds)
        self.wheel_actuators_labels = produce_labels(self.wheel_actuator_template, n_wheels)

def produce_labels(template, n):
    labels = dict()

    label_filler = range(n) if isinstance(n, int) else list(n)

    for i in label_filler:
        labels[i] = template.format(id = i)
    
    return labels
