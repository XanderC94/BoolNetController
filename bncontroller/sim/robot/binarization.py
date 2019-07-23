def phototaxis(lsv:dict, ths:float):
    return dict((str(k), lsv[k] > ths) for k in lsv)
    
def antiphototaxis(lsv:dict, ths:float):
    return dict((str(k), lsv[k] <= ths) for k in lsv)