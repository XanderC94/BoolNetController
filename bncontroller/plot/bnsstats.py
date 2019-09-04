
import re as regx
import numpy as np
import statistics
import matplotlib.pyplot as plotter
import matplotlib.patches as mpatches
import bncontroller.plot.utils as pu
import bncontroller.filelib.utils as fu
# from mpl_toolkits.mplot3d import Axes3D
from pandas import DataFrame, Series
from pathlib import Path
from collections import OrderedDict
from collections.abc import Iterable
from bncontroller.jsonlib.utils import read_json
from bncontroller.collectionslib.utils import transpose
from bncontroller.filelib.utils import cpaths, get_dir
from bncontroller.sim.utils import GLOBALS, Config, load_global_config
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.plot.colors import get_cmap
from bncontroller.plot.utils import save_plots
from bncontroller.boolnet.structures import BooleanNetwork

fn_pattern = r'n(?P<N>\d+)_k(?P<K>\d+)_nrho(?P<nRho>\d+.?\d+)_(ttau|trho)(?P<tTau>\d+.?\d+)_(iphi|if)(?P<if>\d+)'

def plot_constraints(title: str, xs: list, ys: list):

    fig, ax = plotter.subplots(num=title, figsize=(19, 11), dpi=138)

    __x = 10
    xt = __x
    
    ax.set_title(title)
    ax.set_xlabel('Modelskin')
    ax.set_ylabel('Success Rate')
    ax.set_ylim([0, 1.01])
    ax.set_xlim([0, len(data) * __x + __x])
    ticks = []

    ymax = round(max(ys), 3)
    ymin = round(min(ys), 3)
    ymean = round(sum(ys)/len(ys), 3)

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
        [0, ax.get_xlim()[1]],
        [ymax, ymax],
        color='k',
        linewidth=0.5
    )

    ax.plot(
        [0, ax.get_xlim()[1]],
        [ymin, ymin],
        color='k',
        linewidth=0.5
    )

    ax.plot(
        [0, ax.get_xlim()[1]],
        [ymean, ymean],
        color='k',
        linewidth=0.5
    )

    ax.annotate(
        str(ymax), 
        xy=(__x, ymax+0.01), 
        xytext=(__x, ymax+0.01), 
        color='k', 
        textcoords="offset points",
        size=10, 
        va="center"
    )

    if ymean > 0:
        ax.annotate(
            str(ymean), 
            xy=(__x*2, ymean+0.01), 
            xytext=(__x*2, ymean+0.01), 
            color='k', 
            textcoords="offset points",
            size=10, 
            va="center"
        )

    if ymin > 0:
        ax.annotate(
            str(ymin), 
            xy=(__x*3, ymin+0.01), 
            xytext=(__x*3, ymin+0.01), 
            color='k', 
            textcoords="offset points",
            size=10, 
            va="center"
        )

    ax.tick_params(axis='x', labelsize=10)
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
    
    load_global_config()

    path = get_dir(GLOBALS.sim_data_path / 'stats/data', create_if_dir=True)

    print(path)

    data = dict()

    for p in path.iterdir():
    
        if p.name.startswith('dataframe') and 'json' in p.suffix:
            
            m = regx.search(fn_pattern, p.name)
            if m is not None:
                # print(p)
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
    
    def c2no1(bnname, c):
        # bnname, c = cols
        print(bnname)
        bn = BooleanNetwork.from_json(read_json(GLOBALS.bn_ctrl_model_path / 'stats/models' / bnname))
        return c if len(bn.atm.attractors) > 1 else False
    
    for ds in data.values():
        if 'c2no1' not in ds['frame']:             
            ds['frame']['c2no1'] = [
                c2no1(name, c2) 
                for name, c2 in ds['frame'][['bn', 'c2']].values
            ]

    params, frames1, frames2, frames2no1, frames3, frames4, frames123, frames1234 = transpose(
        [
            (
                tuple(ds['params'].values()), 
                ds['frame'].c1.mean(),
                ds['frame'].c2.mean(),
                ds['frame'].c2no1.mean(),
                ds['frame'].c3.mean(),
                ds['frame'].c4.mean(),
                ds['frame'][['c1', 'c2', 'c3']].agg(AND, axis=1).mean(),
                ds['frame'][['c1', 'c2', 'c3', 'c4']].agg(AND, axis=1).mean()

            ) 
            for ds in data.values()
        ]
    )

    labels_template = '_N_K_nRho_tTau_iPhi'

    f1, a1 = plot_constraints('Constr_1_Satisfaction' + labels_template, params, frames1)
    f2, a2 = plot_constraints('Constr_2_Satisfaction' + labels_template, params, frames2)
    f2no1, a2n01 = plot_constraints('Constr_2_no1s_Satisfaction' + labels_template, params, frames2no1)
    f3, a3 = plot_constraints('Constr_3_Satisfaction' + labels_template, params, frames3)
    f4, a4 = plot_constraints('Constr_4_Satisfaction' + labels_template, params, frames4)
    f123, a123 = plot_constraints('Constr_123_Satisfaction' + labels_template, params, frames123)
    f1234, a1234 = plot_constraints('Constr_1234_Satisfaction' + labels_template, params, frames1234)

    ################################################################################
    
    # plotter.show()

    save_plots(GLOBALS.plot_image_path / 'stats', [f1, f2, f2no1, f3, f4, f123, f1234])

