from bncontroller.parse.utils import parse_args
from bncontroller.sim.utils import GLOBALS
from singleton_decorator import singleton

try:
    __ARGS, __UNKNOWNS = parse_args()

    GLOBALS.config = __ARGS.config
    GLOBALS.args = __ARGS
    GLOBALS.unknowns = __UNKNOWNS
    
except Exception as ex:
    # print('Unable to load Global Config...')
    pass
    