import time
from bncontroller.parse.utils import parse_args
from bncontroller.sim.utils import GLOBALS

t = time.perf_counter()

try:
    GLOBALS.config = parse_args().config
    print('Global Configuration loaded from file...')
except Exception as ex:
    print('Unable to load Global Config...')
    pass
    
from pprint import pprint
print(time.perf_counter() - t)
# print(type(GLOBALS.webots_world_path))
# pprint(vars(GLOBALS), indent=4)

# exit(1)