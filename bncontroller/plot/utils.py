import re as regx
from pandas import DataFrame
from pathlib import Path
from bncontroller.jsonlib.utils import read_json
from bncontroller.jsonlib.types import isnotnone, hasnotnone, str2num
from bncontroller.file.utils import get_parts_id, get_simple_fname

#################################################################################

def orderedby(x:str, pattern:str):

    ids = get_parts_id(x, pattern)

    return tuple(
        # reversed(
            map(str2num, ids)
        # )
    ) if ids else x

def get_data(f:Path, pattern:str, uniqueness=3, parts=['%s','%s','%s']):
 
    return (
        get_simple_fname(f.name, pattern, uniqueness=uniqueness, parts=parts), 
        DataFrame.from_dict(read_json(f))
    )
   