from typing import Callable

Comparator = Callable[[object, object], bool]

def none_cmp(a, b): 
    return a and not(b)

def lesser(a, b):
    return a < b

def greater(a, b):
    return a > b

def lesserequal(a, b):
    return a <= b

def greaterequal(a, b):
    return a >= b

def seq_compare(a, b, strat:Comparator, fallback=lambda *args: False):
    '''
    Comparator able to match numerics and tuples
    '''
    def __fill(a, b):
        return a[:len(b) + 1], type(b)([*b, 0.0])
        
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        
        if len(a) > len(b):
            a, b = __fill(a, b)
        elif len(a) < len(b):
            b, a = __fill(b, a)

        while a[0] == b[0] and len(a) == len(b) > 1:
            a = a[-len(a) + 1:]
            b = b[-len(b) + 1:]
        
        return strat(a[0], b[0])
    
    else:
        return fallback(a, b, strat)


def mixed_compare(a, b, strat:Comparator, fallback=lambda *args: False):

    if isinstance(a, (list, tuple)) and isinstance(b, (int, float, bool)):
        return strat(a[0], b)
    elif isinstance(b, (list, tuple)) and isinstance(a, (int, float, bool)):
        return strat(a, b[0])
    elif a is None or b is None:
        return none_cmp(a, b)
    else:
        return fallback(a, b, strat)