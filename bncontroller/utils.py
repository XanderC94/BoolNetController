import json, datetime, logging
from pathlib import Path
from glob import glob

def iso8106():
    return f'{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}'

def generate_file_name(*args, uniqueness_gen = iso8106):
    """
    """
    return '.'.join((*args, uniqueness_gen()))

def recursiveExtractDictWithIntKey(json)-> dict:
    connectivities = {}
    for K,V in json.items():
        if isinstance(V, dict):
            connectivities.update({int(K): recursiveExtractDictWithIntKey(V)})
        else:
            connectivities.update({int(K): V})
    return connectivities

def getAllFilesIn(target:str or Path, extension:str) -> list:

    path = target if isinstance(target, Path) else Path(target)

    return filter(
        lambda f: extension in f.suffix,
        [item for item in path.iterdir()] if path.is_dir() else [path]
    )

if __name__ == "__main__":
    
    print(generate_file_name('a', 'b', 'c'))
    