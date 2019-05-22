import itertools, random, string, hashlib, unicodedata, json
from boolean import rBool, truthValues, Boolean

def test(*args, f):
    print(args)
    
    return f(args)

class BooleanFunction(object):
    """ 
    A Boolean Function with k parameters implemented as a dictonary wrapper. 

    Can trasparently implements Deterministic or Probabilistic Boolean Functions / Truth Tables

    It's initialized randomly through a generator function. Default: deterministic Boolean generator.
    """
    def __init__(self, k: int, generator = lambda *args: Boolean(rBool())):
        
        self.__k = k

        _table = list(itertools.product(truthValues, repeat=k))
        
        self.__truth_table = dict([(args, generator(*args)) for args in _table])

    def __setitem__(self, params: tuple, newValue):
        if isinstance(newValue, Boolean):
            self.__truth_table[params] = newValue
        elif isinstance(newValue, (bool, int, float)):
            self.__truth_table[params] = Boolean(newValue)
        else:
            raise Exception(f'Boolean functions do not accept {type(newValue)} as truth value.')

    def __getitem__(self, params: tuple) -> Boolean:
        return self.__truth_table[params]
    
    def setByIndex(self, idx, newValue):
        k = list(self.__truth_table.keys())[idx]
        self[k] = newValue

    def getByIndex(self, idx):
        k = list(self.__truth_table.keys())[idx]
        return self[k]

    def __call__(self, params: tuple) -> bool:
        """
        Return the function evaluation for the given tuple of bools
        """ 
        return bool(self.__truth_table[params])

    def __str__(self):
        return '\n'.join([f'{k}:{v}' for k, v in self.__truth_table.items()])
    
    def __len__(self):
        return self.__k

    def toJson(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object
        """
        return {'k':len(self), 'truthtable':list(map(lambda e: {'params':e[0],'hold':e[1].toJson()}, self.__truth_table.items()))}

    @staticmethod
    def fromJson(json:dict):
        _bf = BooleanFunction(json['k'])

        for e in json['truthtable']:
            _bf[e['params']] = Boolean.fromJson(e['hold'])

if __name__ == "__main__":

    dbf = BooleanFunction(3)
    pbf = BooleanFunction(3, generator = lambda *args: Boolean(random.choice([0.2, 0.35, 0.5, 0.65, 0.8])))

    print(dbf)
    print()
    print(pbf)
    print()
    
    print()
    print(pbf[(True, True, False)])
    pbf[(True, True, False)] = True
    print(pbf[(True, True, False)])
    print()

    with open('tt.json', 'w') as fp:
        json.dump(dbf.toJson(), fp, indent=2)

    # print(pbf.toJson())