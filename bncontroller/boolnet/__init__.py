from bncontroller.boolnet.atm import DEFAULT_ATM_WS_PATH
from bncontroller.file.utils import check_path

check_path(DEFAULT_ATM_WS_PATH, create_if_file=True)