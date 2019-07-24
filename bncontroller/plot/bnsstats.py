
import re as regx
import numpy as np
import statistics
import matplotlib.pyplot as plotter
import matplotlib.patches as mpatches
import bncontroller.plot.utils as pu
import bncontroller.file.utils as fu
# from mpl_toolkits.mplot3d import Axes3D
from pandas import DataFrame, Series
from pathlib import Path
from collections import OrderedDict
from collections.abc import Iterable
from bncontroller.jsonlib.utils import read_json
from bncontroller.collectionslib.utils import transpose
from bncontroller.file.utils import cpaths, get_dir
from bncontroller.sim.config import Config
from bncontroller.sim.utils import GLOBALS
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.plot.colors import get_cmap

fn_pattern = r'n(?P<N>\d+)_k(?P<K>\d+)_nrho(?P<nRho>\d+.?\d+)_trho(?P<tRho>\d+.?\d+)_if(?P<if>\d+)'

def plot_constraints(title: str, xs: list, ys:list, size_ths=0.5):

    fig, ax = plotter.subplots(num=title)

    __x = 10
    xt = __x
    
    ax.set_ylim([0, 1.1])
    ax.set_xlim([0, len(data) * __x + __x])
    
    ticks = []

    for x, y in zip(xs, ys):
        
        ticks.append(
            (xt, str(x).replace(' ', '')[1:-1])
        )
        
        ax.bar(
            x=[xt],
            height=y,
            align='center',
            width=3.0
        )

        xt += __x

    ax.plot(
        [0, len(data) * __x + __x],
        [size_ths, size_ths],
        color='k',
        linewidth=0.5
    )

    ax.tick_params(axis='x', labelsize=6)
    ax.set_xticks(transpose(ticks)[0])
    ax.set_xticklabels(transpose(ticks)[1], rotation=90)

    fig.subplots_adjust(
        left=0.03,
        right=0.99,
        bottom=0.1,
        top=0.99,
        wspace= 0.0,
        hspace=0.0
    )

    ticks.clear()

    return fig, ax

if __name__ == "__main__":
    
    path = get_dir(GLOBALS.bn_slct_model_path / 'stats/data', create_if_dir=True)

    data = dict()
    for p in path.iterdir():
    
        if p.name.startswith('dataframe') and 'json' in p.suffix:

            m = regx.search(fn_pattern, p.name)
            if m is not None:
                d = dict((k, int(float(v))) for k, v in m.groupdict().items())
                data.update({
                    p.name:{
                        'params': d,
                        'frame': DataFrame.from_dict(read_json(p))
                    }
                })
    
    #################################################################################

    def AND(s:Series):
        return all(s.tolist())

    params, frames1, frames2, frames3, frames4, frames123, frames1234 = transpose(
        [
            (
                tuple(ds['params'].values()), 
                ds['frame'].c1.mean(),
                ds['frame'].c2.mean(), 
                ds['frame'].c3.mean(),
                ds['frame'].c4.mean(),
                ds['frame'][['c1', 'c2', 'c3']].agg(AND, axis=1).mean(),
                ds['frame'][['c1', 'c2', 'c3', 'c4']].agg(AND, axis=1).mean()

            ) 
            for ds in data.values()
        ]
    )

    labels_template = ' {N},{K},{nRho},{tRho},{infix}'

    f1, a1 = plot_constraints('Constr. 1 Satisfaction' + labels_template, params, frames1, size_ths=0.5)
    f2, a2 = plot_constraints('Constr. 2 Satisfaction' + labels_template, params, frames2, size_ths=0.5)
    f3, a3 = plot_constraints('Constr. 3 Satisfaction' + labels_template, params, frames3, size_ths=0.5)
    f4, a4 = plot_constraints('Constr. 4 Satisfaction' + labels_template, params, frames4, size_ths=0.3)
    f123, a123 = plot_constraints('Constr. 1,2,3 Satisfaction' + labels_template, params, frames123, size_ths=0.1)
    f1234, a1234 = plot_constraints('Constr. 1,2,3,4 Satisfaction' + labels_template, params, frames1234, size_ths=0.1)

    ################################################################################
    
    plotter.show()

