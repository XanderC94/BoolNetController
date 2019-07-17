def compare_train_scores(a, b):
    '''
    Comparator able to match numerics and tuples
    '''
    if isinstance(a, (float, int, bool)) and isinstance(b, (float, int, bool)):
        return a < b
    # elif isinstance(new, list) and isinstance(old, list):
    #     nmean, nstdev = statistics.mean(new), statistics.stdev(new)
    #     omean, ostdev = statistics.mean(old), statistics.stdev(old)

    #     return nstdev < ostdev if nmean == omean else nmean < omean
    elif isinstance(a, tuple) and isinstance(b, tuple):
        amean, astdev, *_ = a
        bmean, bstdev, *_ = b

        return astdev < bstdev if amean == bmean else amean < bmean
    # elif isinstance(new, list) and isinstance(old, float):
    #     return statistics.mean(new) < old
    # elif isinstance(new, float) and isinstance(old, list):
    #     return new < statistics.mean(old)
    elif isinstance(a, tuple) and isinstance(b, float):
        return a[0] < b
    elif isinstance(a, float) and isinstance(b, tuple):
        return a < b[0]
    else:
        raise Exception(f'Uncomparable values {type(a)} and {type(b)}')