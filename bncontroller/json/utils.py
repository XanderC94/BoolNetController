import json
from pathlib import Path

class Jsonkin(object):
    """
    A mixin class that enable json serialization and deserialization 
    for the objects of the inheriting classes
    """
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

    def __repr__(self):
        return str(self.to_json())

###############################################################

def tuple_to_json(t:tuple) -> dict:

    return dict((str(k), t[k]) for k in range(len(t)))

def tuple_from_json(json:dict) -> tuple:

    return tuple(json[k] for k in json)

################################################################

def jsonrepr(obj):
    if isinstance(obj, Jsonkin):
        return obj.to_json()
    elif hasattr(obj, '__dict__'):
        return vars(obj)
    elif isinstance(obj, Path):
        return str(obj)
    else:
        return obj

def objrepr(json_repr : dict, obj_type):
    if isinstance(json_repr, dict) and (
        issubclass(obj_type, Jsonkin) or isinstance(obj_type, Jsonkin)):
        return obj_type.from_json(json_repr)
    else:
        return obj_type(json_repr)
        
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

def write_json(obj, path: Path or str, indent = False):

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
        if indent:
            json.dump(_obj, fp, indent=4, default=lambda x: x.__dict__)
        else:
            json.dump(_obj, fp, default=lambda x: x.__dict__)


def recursiveExtractDictWithIntKey(json)-> dict:
    connectivities = {}
    for K,V in json.items():
        if isinstance(V, dict):
            connectivities.update({int(K): recursiveExtractDictWithIntKey(V)})
        else:
            connectivities.update({int(K): V})
    return connectivities