from pathlib import Path
from argparse import ArgumentParser, Action
from bncontroller.sim.config import SimulationConfig, CONFIG_CLI_NAMES

class AutoConfigParser(Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):

        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        
        setattr(namespace, self.dest, SimulationConfig.from_file(values))

def parse_args(parser=ArgumentParser('Configuration Parse Unit.')):

    parser.add_argument(
        *CONFIG_CLI_NAMES, 
        type=Path, 
        action=AutoConfigParser,
        help= 'Path to Configuration file.',
        dest='config',
        metavar='/path/to/config.json'
    )

    # args = parser.parse_args()
    args, *_ = parser.parse_known_args()

    return args

def parse_args_to_config() -> SimulationConfig:

    return parse_args().config