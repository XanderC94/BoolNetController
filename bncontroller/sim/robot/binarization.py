def light_sensor_binarization(lsv:dict, ths:float):
    return dict((str(k), lsv[k] > ths) for k in lsv)