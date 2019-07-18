
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.stubs.utils import clean_generated_worlds, clean_tmpdir

if __name__ == "__main__":

    template = parse_args_to_config()
    clean_generated_worlds(template.webots_world_path)
    clean_tmpdir()

    exit(1)