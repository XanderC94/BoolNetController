import re
from pathlib import Path
from bncontroller.sim.config import CONFIG_CLI_NAMES
from bncontroller.file.utils import check_path

def generate_webots_worldfile(template_path: Path, target_path:Path, config_path:Path):

    if template_path.is_dir() or target_path.is_dir():
        raise Exception('Simuation world path is not a file.') 

    check_path(target_path.parent, create_dirs=True)

    TEMPLATE = r'\s*controllerArgs\s\"(?:{names})=\\\"(.*)\\\"\"\n'

    pattern = TEMPLATE.format(names='|'.join(CONFIG_CLI_NAMES))

    text = ''

    def sub(x:re.Match, s = config_path.resolve()):
        return ''.join([x.string[:x.start(1)], str(s).replace('\\', '/'), x.string[x.end(1):]])

    with open(template_path, 'r') as temp:

        text = temp.readlines()

        for i, line in enumerate(text):
            text[i] = re.sub(pattern, sub, line)

    with open(target_path, 'w') as tar:
        tar.write(''.join(text))
