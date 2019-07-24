
from bncontroller.sim.utils import GLOBALS
from bncontroller.stubs.utils import clean_generated_worlds, clean_tmpdir

if __name__ == "__main__":

    clean_generated_worlds(GLOBALS.webots_world_path)
    clean_tmpdir()

    exit(1)