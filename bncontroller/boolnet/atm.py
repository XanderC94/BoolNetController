from pathlib import Path
from bncontroller.jsonlib.utils import Jsonkin, json
from bncontroller.collectionslib.utils import transpose
from rpy2 import robjects as robjs
from rpy2.robjects.packages import importr

rBoolNet = importr('BoolNet')
rDiffeRenTES = importr('diffeRenTES')
rJSONlite = importr('jsonlite')

class AttractorsTransitionMatrix(object):
    '''
    Attractors Transition Matrix for Boolenat Networks.

    It bridges with R API of BoolNet to produce Attractors and ATM.
    '''

    def __init__(self, 
            ebnf_str: str, 
            atm_ws_path=Path('./atm-workspace.txt'), 
            encoding='UTF-8'):

        atm_ws_path.write_text(ebnf_str, encoding=encoding)

        net = rBoolNet.loadNetwork(str(atm_ws_path))

        atm_ws_path.unlink()

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