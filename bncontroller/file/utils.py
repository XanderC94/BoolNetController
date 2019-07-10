import json, datetime, logging
from pathlib import Path
from glob import glob

def iso8106(format_type=0, ms=0):
    
    max_ms = 6

    if format_type == 0:
        return f'{datetime.datetime.now():%Y%m%dT%H%M%S%f}'[:ms-max_ms]
    else:
        return f'{datetime.datetime.now():%Y%m%dT%H%M%S-%f}'[:ms-max_ms]

def get_fname(*args, uniqueness = iso8106, ftype='txt', template="{name}_{uniqueness}.{ext}"):
    '''
    '''
    
    return template.format(
        name='_'.join(filter(lambda s: s is not None and s != '', list(args))),
        uniqueness=uniqueness(),
        ext=ftype
    )

def check_path(path: Path or str, create_dirs=True, dir_checker=lambda x: x.replace('.', '').isnumeric or x == ''):
    '''
    Returns 1:Dir, 0:File, else raise exception
    '''
    if not path.exists():
        if dir_checker(path.suffix) and create_dirs:
            path.mkdir(parents=create_dirs, exist_ok=False)
        else:
            # check_path(path.parent, create_dirs=create_dirs, dir_checker=dir_checker)
            # path.touch()
            raise Exception('Given path is pointing to an unexistent file.')
    
    return path.is_dir()

def get_dir(path:Path, create_dirs=False):

    return (
        path
        if check_path(path, create_dirs=create_dirs)
        else path.parent
    )


if __name__ == "__main__":
    
    print(get_fname('a', 'b', 'c'))
    