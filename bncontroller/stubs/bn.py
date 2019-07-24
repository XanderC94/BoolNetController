from bncontroller.sim.utils import GLOBALS
from bncontroller.boolnet.factory import generate_rbn, RBNFactory, r_bool

def generate_simple_rbn():
    
    N, K, P, I, O = GLOBALS.bn_params
    
    return RBNFactory(N, K, P, P, I, O)

