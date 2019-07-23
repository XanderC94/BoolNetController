
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
from bncontroller.sim.config import SimulationConfig
from bncontroller.parse.utils import parse_args_to_config
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.plot.colors import get_cmap

fn_pattern = r'n(?P<N>\d+)_k(?P<K>\d+)_nrho(?P<nRho>\d+.?\d+)_trho(?P<tRho>\d+.?\d+)_if(?P<if>\d+)'

def plot_constraints(title:str, xs: list, ys:list, size_ths=0.5):

    fig, ax = plotter.subplots(num=title)

    ax.set_ylim([0, 1.1])
    ax.set_xlim([0, len(data) * 10 + 10])
    __x = 10
    xt = __x
    ticks = []

    for x, y in zip(xs, ys):
        
        if y > 0.5:
            ticks.append(
                str(x).replace(' ', '')[1:-1]
            )
        else:
            ticks.append('')

        ax.bar(
            x=[xt],
            height=y,
            align='center',
            width=3.0 if y > size_ths else 0.8
        )

        xt += __x

    plotter.xticks(
        np.arange(__x, __x + len(ticks) * __x, __x),
        ticks, 
        rotation=15
    )

    return fig, ax

if __name__ == "__main__":
    
    template = parse_args_to_config()
    path = get_dir(template.bn_slct_model_path / 'stats/data', create_if_dir=True)

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

    f1, a1 = plot_constraints('Constr. 1 Satisfaction', params, frames1)
    f2, a2 = plot_constraints('Constr. 2 Satisfaction', params, frames2)
    f3, a3 = plot_constraints('Constr. 3 Satisfaction', params, frames3)
    f4, a4 = plot_constraints('Constr. 3 Satisfaction', params, frames4)
    f123, a123 = plot_constraints('Constr. 1,2,3 Satisfaction', params, frames123)
    f1234, a1234 = plot_constraints('Constr. 1,2,3,4 Satisfaction', params, frames1234)

    ################################################################################
    
    plotter.show()

