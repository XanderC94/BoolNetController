import json, datetime, logging
from pathlib import Path
from glob import glob

def iso8106(format_type=0, ms=0):
    
    max_ms = 6

    if format_type == 0:
        return f'{datetime.datetime.now():%Y%m%dT%H%M%S%f}'[:ms-max_ms]
    else:
        return f'{datetime.datetime.now():%Y%m%dT%H%M%S-%f}'[:ms-max_ms]

def generate_file_name(*args, uniqueness_gen = iso8106, ftype='', name_format="{name}.{ext}"):
    '''
    '''
    return name_format.format(
        name='_'.join(filter(lambda s: s is not None and s != '', (*args, uniqueness_gen()))),
        ext=ftype
    )

def getAllFilesIn(target:str or Path, extension:str) -> list:

    path = target if isinstance(target, Path) else Path(target)

    return filter(
        lambda f: extension in f.suffix,
        [item for item in path.iterdir()] if path.is_dir() else [path]
    )

if __name__ == "__main__":
    
    print(generate_file_name('a', 'b', 'c'))
    