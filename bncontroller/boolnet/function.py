import itertools
from collections import defaultdict
from bncontroller.boolnet.boolean import r_bool, TRUTH_VALUES, Boolean
from bncontroller.jsonlib.utils import Jsonkin, tuple_from_json, tuple_to_json

class BooleanFunction(Jsonkin):
    """ 
    A Boolean Function with k parameters implemented as a dictonary wrapper.

    Can trasparently implements Deterministic or Probabilistic Boolean Functions / Truth Tables

    It's initialized randomly through a generator function. Default: deterministic Boolean generator.
    """
    def __init__(self, k: int, result_generator=lambda *args: Boolean(r_bool())):
        
        self.__k = k

        tt = list(itertools.product(TRUTH_VALUES, repeat=k))
        
        self.__truth_table = defaultdict(lambda: Boolean(False))

        self.__tt_index = defaultdict(tuple)

        for i, args in zip(range(2**k), tt): 
            self[args] = result_generator(*args)
            self.__tt_index[i] = args

    def __setitem__(self, params: tuple, new_value):
        self.__truth_table[params].bias = new_value

    def __getitem__(self, params: tuple) -> Boolean:
        return self.__truth_table[params]
    
    def set_by_index(self, idx, new_value):
        args = self.__tt_index[idx]
        self[args] = new_value

    def by_index(self, idx) -> (tuple, Boolean):
        args = self.__tt_index[idx]
        return (args, self[args])

    @property
    def arity(self) -> int:
        """
        Returns the number of parameters (k) of the boolean function
        """
        return self.__k
    
    def __call__(self, params: tuple) -> bool:
        """
        Return the function evaluation for the given tuple of booleans

        This method differs from __getitem__ as it evaluates the Boolean wrapper.
        """
        return self.__truth_table[params].value

    def __str__(self):
        return '\n'.join([f'{k}:{v}' for k, v in self.__truth_table.items()])
    
    def __len__(self):
        return self.__k
    
    def __eq__(self, that):

        if isinstance(that, BooleanFunction):
            return self.arity == that.arity and all(
                self[e] == that[e] for e in list(itertools.product(TRUTH_VALUES, repeat=self.arity))
            )
        else:
            return False

    def to_json(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object
        """
        return {
            'arity': len(self), 
            'truth_table': list(map(lambda e: {
                'params': tuple_to_json(e[0]),
                'hold': e[1].to_json()
            }, self.__truth_table.items()))
        }

    @staticmethod
    def from_json(json: dict):
        _bf = BooleanFunction(json['arity'])

        for e in json['truth_table']:
            params = tuple_from_json(e['params'])
            _bf[params] = Boolean.from_json(e['hold'])
        
        return _bf
    
    def as_logic_expr(self, pnames: list) -> str:
        terms = []
        
        if pnames:
            for tte in self.__truth_table:
                if self(tte):
                    terms.append('({expr})'.format(
                        expr=' & '.join([f'{n}' if p else f'!{n}' for p, n in zip(tte, pnames)])
                    ))

        return ' | '.join(terms)
