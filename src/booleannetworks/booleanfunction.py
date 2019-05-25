import itertools, random, string, hashlib, unicodedata, json
from boolean import r_bool, truth_values, Boolean

def test(*args, f):
    print(args)
    
    return f(args)

class BooleanFunction(object):
    """ 
    A Boolean Function with k parameters implemented as a dictonary wrapper. 

    Can trasparently implements Deterministic or Probabilistic Boolean Functions / Truth Tables

    It's initialized randomly through a generator function. Default: deterministic Boolean generator.
    """
    def __init__(self, k: int, result_generator = lambda *args: Boolean(r_bool())):
        
        self.__k = k

        tt = list(itertools.product(truth_values, repeat=k))
        
        self.__truth_table = dict()

        for args in tt: self.__truth_table[args] = result_generator(*args)

    def __setitem__(self, params: tuple, new_value):
        if isinstance(new_value, Boolean):
            self.__truth_table[params] = new_value
        elif isinstance(new_value, (bool, int, float)):
            self.__truth_table[params].set_bias(new_value)
        else:
            raise Exception(f'Boolean functions do not accept {type(new_value)} as truth value.')

    def __getitem__(self, params: tuple) -> Boolean:
        return self.__truth_table[params]
    
    def set_by_index(self, idx, new_value):
        k = list(self.__truth_table.keys())[idx]
        self[k] = new_value

    def by_index(self, idx) -> (tuple, Boolean):
        k = list(self.__truth_table.keys())[idx]
        return (k, self[k])

    def get_k(self) -> int:
        return self.__k

    def __call__(self, params: tuple) -> bool:
        """
        Return the function evaluation for the given tuple of bools
        """ 
        return bool(self.__truth_table[params])

    def __str__(self):
        return '\n'.join([f'{k}:{v}' for k, v in self.__truth_table.items()])
    
    def __len__(self):
        return self.__k

    def to_json(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object
        """
        return {'k':len(self), 'truthtable':list(map(lambda e: {'params':e[0],'hold':e[1].to_json()}, self.__truth_table.items()))}

    @staticmethod
    def from_json(json:dict):
        _bf = BooleanFunction(json['k'])

        for e in json['truthtable']:
            _bf[e['params']] = Boolean.from_json(e['hold'])

if __name__ == "__main__":

    dbf = BooleanFunction(3)
    pbf = BooleanFunction(3, result_generator = lambda *args: Boolean(random.choice([0.2, 0.35, 0.5, 0.65, 0.8])))

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
        json.dump(dbf.to_json(), fp, indent=2)

    # print(pbf.toJson())