import re as regx
from pandas import DataFrame
from pathlib import Path
from bncontroller.jsonlib.utils import read_json
#################################################################################

fname_pattern = r'(\d{8,}T\d{6,})(?:.+it(\d+))?(?:.+in(\d+))?'

def isnone(x:str):
    return x is not None

def str2num(x:str):
        
        if isinstance(x, str):
            if x.isdigit():
                return int(x)
            elif x.isdecimal():
                return float(x)
        
        return x

def get_ids(x:str, pattern:str):
    m = regx.search(pattern, x)

    return m.groups() if m is not None else None

def orderedby(x:str, pattern:str):
    
    return tuple(
        reversed(list(map(str2num, get_ids(x, pattern))))
    )

def get_simple_name(s:str, pattern:str):
    return '_'.join(filter(isnone, get_ids(s, pattern)))

def check_file(path:Path, starts_with:str, ext:str):
    return path.is_file() and path.name.startswith(starts_with) and ext in path.suffix 

def get_data(f:Path, pattern:str, uniqueness=3):
 
    ids = get_ids(f.name, pattern)

    if ids is not None:
        
        return (
            '_'.join(filter(isnone, ids[:max(1, uniqueness)])), 
            DataFrame.from_dict(read_json(f))
        )
    else:
        raise Exception('filename does not match pattern')