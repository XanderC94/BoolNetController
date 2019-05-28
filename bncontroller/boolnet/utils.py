import json
from pathlib import Path

def check_to_json_existence(value):
    if hasattr(value, 'to_json') and callable(value.to_json):
        return value.to_json() 
    else:
        return value

def read_json(path) -> dict:
    _path = path if isinstance(path, Path) else Path(path)
    _obj = {}
    with open(_path, 'r') as fp:
        _obj = json.load(fp, indent=4)

    return _obj

def write_json(obj, path):

    _path = path if isinstance(path, Path) else Path(path)
    _obj = obj if hasattr(obj, 'to_json') else vars(obj)

    with open(_path, 'w') as fp:
        json.dump(_obj, fp, indent=4)
