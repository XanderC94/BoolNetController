import re
import numpy as np
import matplotlib.pyplot as plotter
from pandas import DataFrame
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.plot.utils import get_simple_name, fname_pattern

output_pattern = r'old:\s?\(?(\d+\.\d+e[+-]?\d+)(?:,\s?(\d+\.\d+e[+-]?\d+)\))?'

def plot_output(dataset:str, data:list):

    fig, ax = plotter.subplots(num=f'train_score_trend_{fname}')

    ax.set_title('Model Train -- Scores trend')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Score')

    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    ax.plot(data, color='r')

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
    
    config = parse_args_to_config()

    files = (
        list(config.app_output_path.iterdir()) 
        if config.app_output_path.is_dir() 
        else [config.app_output_path]
    )
    plots = list()

    for f in files:

        fname = get_simple_name(f.name, fname_pattern)

        data = parse_output(f)
        
        if data:
            plots.append(plot_output(fname, data))

    plotter.show()