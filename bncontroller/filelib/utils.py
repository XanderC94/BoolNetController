import datetime
import re as regx
from pathlib import Path
from bncontroller.typeslib.utils import isnotnone, hasnotnone, str2num

FNAME_PATTERN = r'(D?\d{8,}T\d{6,})(?:_(?:it)?([+-]?\d+))?(?:_(?:in)?([+-]?\d+))?'

FNAME_PARTS = ['%s', 'it%s', 'in%s']

def iso8106(format_type=0, ms=6):
    '''
    Return actual datetime under iso8106 standard.
    '''
    MAX_MS = 6
    ms = min(ms, 6)

    if format_type == 0:
        date = f'{datetime.datetime.now():%Y%m%dT%H%M%S%f}'
        return date if ms == MAX_MS else date[:ms-MAX_MS]
    else:
        date = f'{datetime.datetime.now():%Y-%m-%dT%H:%M:%S.%f}'
        return date if ms == MAX_MS else date[:ms-MAX_MS]

FROZEN_DATE = iso8106(ms=3)

def gen_fname(*args, uniqueness = iso8106, ftype='txt', template="{name}_{uniqueness}.{ext}"):
    '''
    Generate file name based on passed arguments and composed under the specified template string
    '''
    
    return template.format(
        name='_'.join(filter(lambda s: s is not None and s != '', list(args))),
        uniqueness=uniqueness(),
        ext=ftype
    )

def get_parts_id(x:str, pattern:str, default=None):
    '''
    return a tuple which holds the matching ids specified in the regex pattern
    '''

    m = regx.search(pattern, x)
    
    return m.groups(default='0') if m is not None else default

def get_simple_fname(s:str, pattern:str, parts=FNAME_PARTS, uniqueness=3):
    '''
    Given a file name or path extract the simplified name of the file.

    <date>_it<iterations>?_in<instance>?
    '''
    zip_parts = list(
        filter(hasnotnone, zip(parts, get_parts_id(s, pattern, s)))
    )[:max(1, uniqueness)]

    return '_'.join(a % b for a, b in zip_parts)

def check_file(path:Path, starts_with:str, ext:str):
    '''
    Check if is a file and matched the given properties
    '''
    return path.is_file() and path.name.startswith(starts_with) and ext in path.suffix 

DEFAULT_DIR_CHECKER = lambda x: x.replace('.', '').isnumeric() or x == ''

def check_path(path: Path or str, create_if_dir=False, create_if_file=False, dir_checker=DEFAULT_DIR_CHECKER):
    '''
    Check whether is a directory or a file.
    If is a directory (check through the dir_checker function)
    but doesn't exists it may creates the whole path (create_dirs=True)
    Same apply if it's a file. 

    Returns 1:Dir, 0:File, -1:Unexistent File, -2:Unexistent Dir if Silent
    '''
    if not path.exists():
        if dir_checker(path.suffix):
            if create_if_dir:
                path.mkdir(parents=create_if_dir, exist_ok=False)
            else:
                return -2
                # raise Exception('Given path is pointing to an unexistent directory.')
        elif create_if_file:
            check_path(path.parent, create_if_dir=True)
            path.touch()
        else:
            return -1
            # raise Exception('Given path is pointing to an unexistent file.')
    
    return path.is_dir()

def is_dir(p:Path):
    return p.is_dir()

def is_file(p:Path):
    return p.is_file()

def get_dir(path:Path, create_if_dir=False, dir_checker=DEFAULT_DIR_CHECKER):
    '''
    Return path if path is dir (checked through check_path), else path.parent
    If path is file and doesn't exists it raises an Exception
    '''
    return (
        path
        if check_path(path, create_if_dir=create_if_dir, dir_checker=dir_checker) in (1, -2)
        else path.parent
    )

def get_file(path:Path, create_if_file=False, dir_checker=DEFAULT_DIR_CHECKER):
    if check_path(path, create_if_file=create_if_file, dir_checker=dir_checker) == 0:
        return path
    else:
        raise Exception('Given path is pointing to a directory.')

def cpaths(p, limit=None, recursive=1) -> list:
    '''
    Recursively Collect paths in p into a list that can be limited to the first <limits> elements.

    Recursion depth can be limited by the <recursive:int> parameter.

    '''
    
    l = list()
    
    if not recursive:
        return [p]
    elif isinstance(p, (list, set, tuple)):
        for i in p:
            l.extend(cpaths(i, recursive=recursive-1)) 
    elif isinstance(p, Path) and p.is_dir():
        l.extend(cpaths(list(p.iterdir()), recursive=recursive))
    else:
        l.append(p)

    return l[:limit]
