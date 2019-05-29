
def bnstate_distance(s1:dict, s2:dict, comp = lambda v1, v2: v1 == v2, crit = lambda ds: ds.count(0)):
    '''
    Return the distance between 2 states of a BN.
    The default criterium count the number of states 
    that don't hold the same value.
    '''
    ds = [comp(s2[k1], v1) for k1, v1 in s1.items()]
    return crit(ds)