
class EPuckDevicesLabels(object):

    def __init__(self,
            n_gps,
            n_distance_sensors,
            n_light_sensors,
            n_bumpers,
            n_leds,
            n_wheels):

        self.distance_sensor_template = 'ps{id}'
        self.light_sensor_template = 'ls{id}'
        self.led_actuator_template = 'led{id}'
        self.touch_sensor_template = 'bs{id}'
        self.wheel_actuator_template = '{id} wheel motor'
        self.wheel_position_template = '{id} wheel sensor'
        self.gps_template = 'gps{id}'

        self.distance_sensors_labels = produce_labels(self.distance_sensor_template, n_distance_sensors)
        self.light_sensors_labels = produce_labels(self.light_sensor_template, n_light_sensors)
        self.bump_sensors_labels = produce_labels(self.touch_sensor_template, n_bumpers)
        self.gps_sensors_labels = produce_labels(self.gps_template, n_gps)
        self.wheel_position_sensors_labels = produce_labels(self.wheel_position_template, n_wheels)
        
        self.led_actuators_labels = produce_labels(self.led_actuator_template, n_leds)
        self.wheel_actuators_labels = produce_labels(self.wheel_actuator_template, n_wheels)

def produce_labels(template, n):
    labels = dict()

    label_filler = range(n) if isinstance(n, int) else list(n)

    for i in label_filler:
        labels[i] = template.format(id = i)
    
    return labels
