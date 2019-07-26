from pathlib import Path
from argparse import ArgumentParser, Action
from bncontroller.sim.config import Config, CONFIG_CLI_NAMES

def parse_args(parser=ArgumentParser('Configuration Parse Unit.'), config_converter=Path):
    '''
    Parses Command Line Arguments, returning the parsed arguments as objects
    '''
    parser.add_argument(
        *CONFIG_CLI_NAMES, 
        type= config_converter,
        # action=AutoConfigParser,
        help= 'Path to Configuration file.',
        dest='config',
        metavar='/path/to/config.json'
    )

    args, *_ = parser.parse_known_args()

    return args
    