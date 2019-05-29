import json
from pathlib import Path

class Jsonkin(object):
    """
    A mixin class that enable json serialization and deserialization 
    for the objects of the inheriting classes
    """
    def __init__(self):
        pass

    def to_json(self) -> dict:
        """
        Return a (valid) json representation of the object as a dictionary
        """
        return vars(self)
    
    @staticmethod
    def from_json(json: dict):
        """
        Map the json rapresentation into an object of this class
        """
        return Jsonkin()
    
    def __str__(self):
        return str(self.to_json())

def check_to_json_existence(value):
    if hasattr(value, 'to_json') and callable(value.to_json):
        return value.to_json() 
    else:
        return value

def read_json(path: Path or str) -> dict:
    _path = path if isinstance(path, Path) else Path(path)
    _obj = {}
    with open(_path, 'r') as fp:
        _obj = json.load(fp)

    return _obj

def write_json(obj, path: Path or str):

    def check(obj) -> dict:
        if isinstance(obj, dict):
            return obj
        elif hasattr(obj, 'to_json') and callable(obj.to_json):
            return obj.to_json()
        else:
            return vars(obj)

    _path = path if isinstance(path, Path) else Path(path)
    _obj = check(obj)

    with open(_path, 'w') as fp:
        json.dump(_obj, fp, indent=4, default=lambda x: x.__dict__)
