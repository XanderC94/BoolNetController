'''
JSON utilities module
'''
import json
import importlib
from typing import Callable
from types import FunctionType
from pathlib import Path
from collections.abc import Iterable

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
    
    # def to_file(self, fp: Path or str):
    #     write_json(self.to_json(), fp)
    
    # @staticmethod
    # def from_file(fp: Path or str):
    #     return Jsonkin()

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
    '''
    Serializer from object to JSON repr
    '''
    if isinstance(obj, Jsonkin) or issubclass(type(obj), Jsonkin):
        return obj.to_json()
    elif hasattr(obj, '__dict__'):
        return vars(obj)
    elif isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, float) and obj in (float('inf'), float('+inf'), float('-inf')):
        return str(obj)
    else:
        return obj

def objrepr(json_repr, obj_type, alt_type=None):
    '''
    Deserializer from JSON repr to defined object type
    '''

    if isinstance(json_repr, dict) and issubclass(obj_type, Jsonkin):
        return obj_type.from_json(json_repr)
    else:
        
        if alt_type and isinstance(json_repr, (alt_type, list)) and isinstance(json_repr, Iterable):
            return alt_type(objrepr(item, obj_type) for item in json_repr)
        else:
            return obj_type(json_repr)

def read_json(path: Path or str) -> dict:
    _path = path if isinstance(path, Path) else Path(path)
    _obj = {}
    with open(_path, 'r') as fp:
        _obj = json.load(fp)

    return _obj

def write_json(obj, path: Path or str, indent = False, default=jsonrepr):

    _path = path if isinstance(path, Path) else Path(path)
    _obj = jsonrepr(obj)

    with open(_path, 'w') as fp:
        if indent:
            json.dump(_obj, fp, indent=4, default=default)
        else:
            json.dump(_obj, fp, default=default)

class FunctionWrapper(Jsonkin, Callable[[object], object]):

    def __init__(self, definition: str or FunctionType):
        
        if callable(definition):
            self.__fnpointer = definition
            self.__def = '{module}::{func}'.format(
                module=definition.__module__,
                func=definition.__name__
            )
        elif isinstance(definition, str):
            self.__fnpointer = None
            self.__def = definition
        else:
            raise TypeError('Function definition is neither a name.space::func_name string or a function object!')

    def __call__(self, *args, **kwargs):
        # Lazy
        if self.__fnpointer is None:
            modulestr, methodstr = self.__def.split('::', 1)
            module = importlib.import_module(modulestr)
            self.__fnpointer = getattr(module, methodstr)

        return self.__fnpointer(*args, **kwargs)
    
    def to_json(self):
        return self.__def
    
    @staticmethod
    def from_json(json):
        return FunctionWrapper(json)