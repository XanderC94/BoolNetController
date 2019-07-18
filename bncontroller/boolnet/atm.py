import json
from pathlib import Path
from bncontroller.collectionslib.utils import transpose
from rpy2 import robjects as robjs
from rpy2.robjects.packages import importr

rBoolNet = importr('BoolNet')
rDiffeRenTES = importr('diffeRenTES')
rJSONlite = importr('jsonlite')

DEFAULT_ATM_WS_PATH = Path('./tmp/atm-workspace.txt')

class AttractorsTransitionMatrix(object):
    '''
    Attractors Transition Matrix for Boolean Networks.

    Bridges R-lang C API of BoolNet to produce Attractors and ATM 
    of a given BN in extended Boolean Network Format (ebnf).
    '''

    def __init__(self, ebnf_str: str):

        self.id = hash(ebnf_str)

        Path(DEFAULT_ATM_WS_PATH).write_text(ebnf_str, encoding='UTF-8')
        
        net = rBoolNet.loadNetwork(str(DEFAULT_ATM_WS_PATH))

        # atm_ws_path.unlink()

        jATM = json.loads(rJSONlite.toJSON(
            rDiffeRenTES.getATM(
                net, 
                rBoolNet.getAttractors(net)
            )
        )[0])

        self.tableau, self.attractors = self.__from_parts(
            jATM['ATM'], jATM['attractors']['binary']
        )

    @property
    def dtableau(self) -> dict:
        return dict(
            (f'a{ki}', dict((f'a{kj}', p) for kj, p in enumerate(self.tableau[ki]))) 
            for ki, t in enumerate(self.tableau)
        )

    @property
    def dattractors(self) -> dict:
        return dict(
            (f'a{ki}', t) 
            for ki, t in enumerate(self.attractors)
        )

    def __from_parts(self, atm:dict, attractors:dict):
        
        return (
            transpose(atm),
            [transpose(a[:-1]) for _, a in attractors.items()]   
        )
        