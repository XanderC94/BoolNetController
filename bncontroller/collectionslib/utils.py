from collections.abc import Iterable

def collection_diff(first: Iterable, second: Iterable):

    return [item for item in first if item not in set(second)]

def flat(x: Iterable, to=list, exclude=dict):

    l = []

    for e in x:
        if not isinstance(e, exclude) and isinstance(e, Iterable):
            for i in e:
                l.append(i)
        else:
            l.append(e)

    return to(l)
