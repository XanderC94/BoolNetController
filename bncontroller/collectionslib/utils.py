import os
from collections.abc import Iterable
from pathlib import Path

def cdiff(first: Iterable, second: Iterable, to=list):
    return to(item for item in first if item not in set(second))

def flat(x: Iterable, to=list, exclude=(dict, str)):
    '''
    Flatten any Collection of collections to a desired colletion. 
    It's not recursive so only flatten top level collections.

    can be specified withc collections type to exclude from being flattened.
    '''
    l = []

    for e in x:
        if not isinstance(e, exclude) and isinstance(e, Iterable):
            for i in e:
                l.append(i)
        else:
            l.append(e)

    return to(l)

def transpose(x:Iterable):
    '''
    Transpose the given collection of collection.
    Rows become Columns and so on.
    '''
    return list(map(list, zip(*x)))

def first(x: list or set):
    return x[0] if x else None
