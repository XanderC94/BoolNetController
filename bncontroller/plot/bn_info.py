
from pathlib import Path
from pandas import DataFrame
from pprint import pprint
from bncontroller.sim.utils import GLOBALS, load_global_config
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.boolnet.structures import BooleanNetwork
from bncontroller.jsonlib.utils import read_json
from bncontroller.filelib.utils import get_dir

if __name__ == "__main__":
    
    load_global_config()

    for path in get_dir(GLOBALS.bn_model_path).iterdir():
        
        if path.is_file():
            bn : BooleanNetwork = BooleanNetwork.from_json(
                read_json(path)
            )

            print(str(path))
            print(DataFrame(bn.atm.dtableau).T)
            print(bn.atm.tableau)
            for k, a in bn.atm.dattractors.items():
                print(k, a)
            print(bn.atm.attractors)
