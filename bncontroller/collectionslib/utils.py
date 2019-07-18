import os
from collections.abc import Iterable
from pathlib import Path, WindowsPath, PosixPath, _windows_flavour, _posix_flavour

def collection_diff(first: Iterable, second: Iterable):
    return [item for item in first if item not in set(second)]

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
    return list(map(list, zip(*x)))

################################################################
