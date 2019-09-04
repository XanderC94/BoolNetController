import bncontroller.typeslib.comparators as cmp
from bncontroller.collectionslib.utils import flat

def __mixed_compare(a, b, strat):
    '''
    Comparator able to match numerics and tuples. 

    It check equality for each positional element and 
    apply strat to the first mismatching elements or the last elements.
    '''
    # Transform inputs to sequence
    if a is None or b is None:
        return cmp.none_cmp(a, b)

    a = flat([a])
    b = flat([b])

    def __fill(a, b):
        return a[:len(b) + 1], type(b)([*b, 0.0])
                
    if len(a) > len(b):
        a, b = __fill(a, b)
    elif len(a) < len(b):
        b, a = __fill(b, a)

    while a[0] == b[0] and len(a) == len(b) and len(b) > 1:
        a = a[-len(a) + 1:]
        b = b[-len(b) + 1:]
        
    return strat(a[0], b[0])

def mixed_le(a, b):
    return __mixed_compare(a, b, cmp.lesserequal)

def mixed_ls(a, b):
    return __mixed_compare(a, b, cmp.lesser)

def mixed_gr(a, b):
    return __mixed_compare(a, b, cmp.greater)

def mixed_ge(a, b):
    return __mixed_compare(a, b, cmp.greaterequal)

def mixed_eq(a, b):
    return __mixed_compare(a, b, cmp.equal)
    