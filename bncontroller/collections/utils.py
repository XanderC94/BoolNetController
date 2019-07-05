def collection_diff(first, second):
        _second = set(second)
        return [item for item in first if item not in _second]

def flat_tuple(x):

    l = []

    for e in x:
        if isinstance(e, tuple):
            for i in e:
                l.append(i)
        else:
            l.append(e)

    return tuple(l)

