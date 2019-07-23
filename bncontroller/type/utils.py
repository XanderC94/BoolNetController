
def isnone(x):
    return x is None

def isnotnone(x):
    return not isnone(x)

def hasnone(x):
    return None in x

def hasnotnone(x):
    return not hasnone(x)

def str2num(x:str):
        
    if isinstance(x, str):
        if x.isdigit() or (x[0] in ('+', '-') and x[1:].isdigit()):
            return int(x)
        elif x.isdecimal() or x.isnumeric():
            return float(x)
    
    return x

def first(x:list or set):
    return x[0] if x else None
