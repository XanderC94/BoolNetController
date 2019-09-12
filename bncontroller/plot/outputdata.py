import re
import numpy as np
import matplotlib.pyplot as plotter
import bncontroller.plot.colors as colors
from bncontroller.plot.utils import save_plots
from bncontroller.collectionslib.utils import transpose
from bncontroller.filelib.utils import get_simple_fname, FNAME_PATTERN, cpaths, is_file
from bncontroller.sim.utils import GLOBALS, load_global_config

output_pattern = r'old:\s?\(?(\d+\.\d+e[+-]?\d+)(?:,\s?(\d+\.\d+e[+-]?\d+)\))?'

def plot_output(fname: str, data: list):

    fig, ax = plotter.subplots(num=f'development_score_trend_{fname}')

    ax.set_title('Network Development -- Iterations / Scores trend')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Score')

    ax.set_xlim([-10, 2500])
    ax.set_ylim([0.0, 3.5e-05])
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    for d in data:
        ax.plot(d, color='r')

    fig.subplots_adjust(
        left=0.05,
        right=0.96,
        bottom=0.05,
        top=0.96,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def parse_output(path, pattern=output_pattern) -> list:
    data = list()

    with open(path, 'r') as fp:

        for line in filter(lambda x: x.startswith('it'), fp.readlines()):
            
            m = re.search(pattern, str(line))
            if m is not None:
                data.append(float(m.group(1)))
    return data

if __name__ == "__main__":
    
    load_global_config()

    files = cpaths(GLOBALS.app_output_path, recursive=3)

    is_train_output = lambda x: (str(x.name).startswith('generate') or str(x.name).startswith('enhance')) and is_file(x)

    plots = list()

    ds = list()

    for f in filter(is_train_output, files):

        fname = get_simple_fname(f.name, FNAME_PATTERN, uniqueness=1)

        data = parse_output(f)
        
        ds.append(data)

        # if data:
        #     fig, ax = plot_output(fname, [data])
        #     save_plots(GLOBALS.plot_image_path / 'out' / fname, [fig])

    fig, ax = plot_output('all', ds)
    save_plots(GLOBALS.plot_image_path / 'all', [fig])