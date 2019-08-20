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
