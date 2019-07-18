import re
import subprocess
import shutil
from pathlib import Path
from bncontroller.sim.config import CONFIG_CLI_NAMES
from bncontroller.file.utils import check_path
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.type.comparators import Comparator
from bncontroller.sim.config import SimulationConfig
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.search.parametric import VNSPublicContext
from bncontroller.file.utils import get_dir

class SimulationArena(object):

    def __init__(self):

        self.floor_size = (3, 3)
        self.controller_args = str(Path('.'))

def generate_webots_worldfile(template_path: Path, target_path:Path, config_path:Path):

    if template_path.is_dir() or target_path.is_dir():
        raise Exception('Simuation world path is not a file.') 

    check_path(target_path.parent, create_if_dir=True)

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
    
#####################################################################################

def run_simulation(config: SimulationConfig, bn: OpenBooleanNetwork) -> dict:

    # Save model (inside or outside of the config? mumble rumble)
    write_json(bn.to_json(), config.bn_model_path) # BN Model
    write_json(config.to_json(), config.sim_config_path, indent=True) # Simulation Configuration

    # Run Webots    
    subprocess.run([
        str(config.webots_path), *config.webots_launch_opts, str(config.webots_world_path)
    ])

    return read_json(config.sim_data_path)

#####################################################################################


def save_subopt_model(config: SimulationConfig, bnjson:dict, ctx:VNSPublicContext, compare:Comparator):
        
    bnjson.update({'sim_info': dict()})

    bnjson['sim_info'].update({'eval_score':ctx.score})
    bnjson['sim_info'].update({'idist':config.sim_light_position.dist(config.sim_agent_position)})
    bnjson['sim_info'].update({'n_it':ctx.it})

    model_dir = get_dir(config.bn_model_path)

    if compare(ctx.score, config.train_save_suboptimal_models): 
        # Save only if <sd_save_suboptimal_models> >= score
        write_json(bnjson, model_dir / config.globals['subopt_model_name'].format(
            date=config.globals['date'],
            it=config.globals['it_suffix'].format(it=ctx.it)
        ))
        
    # Always save the last suboptimal model (overwrite)
    write_json(bnjson, model_dir / config.globals['subopt_model_name'].format(
        date=config.globals['date'], 
        it=''
    ))

def clean_generated_worlds(template_world:Path):
    parts = template_world.name.split('.')
    for p in template_world.parent.iterdir():
        if any(part in p.name for part in parts) and ('wbt' in p.suffix or 'wbproj' in p.suffix):
            p.unlink()

def clean_tmpdir():
    shutil.rmtree('./tmp/')
