'''
Install project as pip module.
'''
import subprocess
from pathlib import Path

if __name__ == "__main__":

    ws = Path('.')

    print(list(map(lambda p: p.name, ws.iterdir())))

    if ws.is_dir() and 'bncontroller' in list(map(lambda p: p.name, ws.iterdir())):
        subprocess.call(['pip', 'install', '-e', '.'])
    else:
        raise Exception('Place yourself in the project directory!')
