import json, datetime, logging
from pathlib import Path
from glob import glob

def collection_diff(first, second):
        _second = set(second)
        return [item for item in first if item not in _second]

def iso8106():
    return f'{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}'

def generate_file_name(*args, uniqueness_gen = iso8106, ftype=''):
    return '.'.join(filter(lambda s: s is not None and s != '', (*args, uniqueness_gen(), ftype)))

def getAllFilesIn(target:str or Path, extension:str) -> list:

    path = target if isinstance(target, Path) else Path(target)

    return filter(
        lambda f: extension in f.suffix,
        [item for item in path.iterdir()] if path.is_dir() else [path]
    )

if __name__ == "__main__":
    
    print(generate_file_name('a', 'b', 'c'))
    