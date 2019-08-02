import re as regx
from pandas import DataFrame
from pathlib import Path
from collections import OrderedDict
from collections.abc import Iterable
from bncontroller.jsonlib.utils import read_json
from bncontroller.typeslib.utils import isnotnone, hasnotnone, str2num
from bncontroller.file.utils import get_parts_id, get_simple_fname, FNAME_PATTERN

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

def collect_data(
        paths: Iterable, fpattern:str,
        key_sort=lambda x: orderedby(x.name, FNAME_PATTERN),
        recursively=False, ds_merge_level=3, 
        data_getter=get_data):

    sortbykey = lambda x: x[0]

    def go(paths: Iterable):

        data = OrderedDict()

        for p in paths:
            
            print(p)
            
            if p.is_file():
                name, df = data_getter(p, fpattern, uniqueness=ds_merge_level)
                data[name] = data[name].append(df, ignore_index=True) if name in data else df

            elif p.is_dir() and recursively:
                
                data.update(
                    **data, 
                    **go(
                        sorted(
                            p.iterdir(), 
                            key=key_sort
                        )
                    )
                )

        return data

    return OrderedDict(sorted(go(paths).items(), key=sortbykey))