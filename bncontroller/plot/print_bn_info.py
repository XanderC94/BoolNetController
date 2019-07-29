
from pathlib import Path
from pandas import DataFrame
from pprint import pprint
from bncontroller.sim.utils import GLOBALS
from bncontroller.boolnet.selector import SelectiveBooleanNetwork
from bncontroller.jsonlib.utils import read_json
from bncontroller.file.utils import get_dir

if __name__ == "__main__":
    
    for path in get_dir(GLOBALS.bn_slct_model_path).iterdir():
        
        if path.is_file():
            bn : SelectiveBooleanNetwork = SelectiveBooleanNetwork.from_json(
                read_json(path)
            )

            print(str(path))
            print(DataFrame(bn.atm.dtableau))
            print(bn.atm.tableau)
            for k, a in bn.atm.dattractors.items():
                print(k, a)
            print(bn.atm.attractors)
