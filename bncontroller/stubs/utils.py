import re
from pathlib import Path
from bncontroller.sim.config import CONFIG_CLI_NAMES
from bncontroller.file.utils import check_path

def generate_webots_worldfile(template_path: Path, target_path:Path, config_path:Path):

    if template_path.is_dir() or target_path.is_dir():
        raise Exception('Simuation world path is not a file.')
    
    check_path(target_path.parent)

    template = r'\s*controllerArgs\s\"(?:{names})=\\\"(.*)\\\"\"\n'
    pattern = template.format(names='|'.join(CONFIG_CLI_NAMES))

    def sub(x:re.Match, s:str):
        return ''.join([x.string[:x.start(1)], s, x.string[x.end(1):]])

    with open(template_path, 'r') as temp:

        text = temp.readlines()

        p = str(config_path).replace('\\', '/')

        for i, line in enumerate(text):
            
            text[i] = re.sub(pattern, lambda x: sub(x, p), line)

            # m = re.search(pattern, line)
            # if m is not None:
            #     text[i] = sub(m, p)

        with open(target_path, 'w') as tar:
            tar.write(''.join(text))
