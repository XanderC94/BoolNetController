import json
from pathlib import Path
from collections import defaultdict
from bncontroller.file.utils import iso8106
from bncontroller.collectionslib.utils import transpose
from rpy2 import robjects as robjs
from rpy2.robjects.packages import importr

rBoolNet = importr('BoolNet')
rDiffeRenTES = importr('diffeRenTES')
rJSONlite = importr('jsonlite')

DEFAULT_ATM_WS_PATH = Path(f'./tmp/atm-workspace_{iso8106()}.txt')

class AttractorsTransitionMatrix(object):
    '''
    Attractors Transition Matrix for Boolean Networks.

    Bridges R-lang C API of BoolNet to produce Attractors and ATM 
    of a given BN in extended Boolean Network Format (ebnf).
    '''

    def __init__(self, ebnf_str: str):

        self.id = hash(ebnf_str)
        # print(ebnf_str)
        self.N = len(list(filter(lambda x: x, ebnf_str.split('\n')[1:])))
        
        # print(self.N)

        Path(DEFAULT_ATM_WS_PATH).write_text(ebnf_str, encoding='UTF-8')
        
        net = rBoolNet.loadNetwork(str(DEFAULT_ATM_WS_PATH))

        # atm_ws_path.unlink()
        atm = rDiffeRenTES.getATM(
                net, 
                rBoolNet.getAttractors(net)
            )
        
        # print(atm)

        jATM = json.loads(rJSONlite.toJSON(atm)[0])

        # print(jATM)

        self.tableau, self.attractors = self.__from_parts(
            jATM['ATM'], jATM['attractors']['binary']
        )

    @property
    def dtableau(self) -> dict:
        return defaultdict(
            lambda: defaultdict(lambda:0.0), 
            (
                (f'a{ki}', dict((f'a{kj}', p) for kj, p in enumerate(self.tableau[ki])))
                for ki, t in enumerate(self.tableau)
            )
        )

    @property
    def dattractors(self) -> dict:
        return dict(
            (f'a{ki}', t) 
            for ki, t in enumerate(self.attractors)
        )

    def __from_parts(self, atm: dict, attractors: dict):
        
        return (
            atm,
            [transpose(a[:self.N]) for _, a in attractors.items()]   
        )
        