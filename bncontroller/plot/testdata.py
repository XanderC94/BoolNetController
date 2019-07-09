import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as colors
import matplotlib.patches as mpatches
import matplotlib.cm as cmx

import random, math, argparse
import numpy as np
import re as regx
from pandas import DataFrame
from pathlib import Path
from collections import OrderedDict
from bncontroller.jsonlib.utils import read_json
from bncontroller.sim.config import parse_args_to_config, SimulationConfig
from bncontroller.plot.utils import interactive_legend, get_cmap

patterns = OrderedDict({
    -1 : {
        'pattern': r'in\d+',
        'cleaner': lambda t: int(t.replace('in', '')),
        'orderidx': 1
    },
    -2 : {
        'pattern': r'it\d+',
        'cleaner': lambda t: int(t.replace('it', '')),
        'orderidx': 0
    },
    -3 : {
        'pattern': r'\d{8,}T\d{6,}',
        'cleaner': lambda t: t,
        'orderidx': 2
    },
})

#################################################################################

def plot_data(data:dict, config:SimulationConfig):

    cmap = get_cmap(len(data), name='rainbow')

    # Model Tests -- Scores distribution #

    bpfig, bpax = plotter.subplots(num=f'test_score_boxplot')

    bpax.set_title('Model Tests -- Scores distribution (Less is Better)')
    bpax.set_xlabel('BN model')
    bpax.set_ylabel('Score')

    bpax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    bpax.boxplot(
        x=list(data[k]['scores'] for k in data),
        labels=list(data.keys()),
        whis=[5, 95], # 1.5,
        # meanline=True,
        flierprops=dict(markerfacecolor='r', marker='D'),
    )

    plotter.xticks(
        list(range(1, len(data) + 1)),
        list(data.keys()), 
        rotation=15
    )

    bpfig.subplots_adjust(
        left=0.04,
        right=0.96,
        bottom=0.13,
        top=0.96,
        wspace= 0.0,
        hspace=0.0
    )

    # Model Tests -- rDist distribution #

    bp2fig, bp2ax = plotter.subplots(num=f'test_fDist_boxplot')

    bp2ax.set_title('Model Tests -- final Distance distribution (Less is Better)')

    bp2ax.set_xlabel('BN model')
    bp2ax.set_ylabel('Final Distance (m)')

    bp2ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    bp2ax.boxplot(
        x=list(data[k]['fdist'] for k in data),
        labels=list(data.keys()),
        whis=[5, 95], # 1.5,
        # meanline=True,
        flierprops=dict(markerfacecolor='r', marker='D'),
    )

    plotter.xticks(
        list(range(1, len(data) + 1)),
        list(data.keys()), 
        rotation=15
    )

    bp2fig.subplots_adjust(
        left=0.04,
        right=0.96,
        bottom=0.13,
        top=0.96,
        wspace= 0.0,
        hspace=0.0
    )

    # Model Tests -- TP / FP #

    bfig, bax = plotter.subplots(num=f'test_posneg_bars')

    bax.set_title(f'Model Tests -- Pos / Neg -- score <= {config.test_positives_threshold}')

    bax.set_xlabel('BN model')
    bax.set_ylabel('P|N (%)')

    x = 0

    for k in data:
        
        p = sum(s <= config.test_positives_threshold for s in data[k]['scores'])

        bax.bar(
            x = [x+1, x+2],
            height = [
                p / len(data[k]),
                 1 - p / len(data[k]), # len(data[k]['scores']) - tp
            ],
            color=['#99ffcc', 'salmon'],
            align='center'
        )

        x+=2

    plotter.xticks(
        np.arange(1.5, len(data) * 2 + 1, 2),
        list(data.keys()), 
        rotation=15
    )

    plotter.legend(handles=[
        mpatches.Patch(color='#99ffcc', label='TP'),
        mpatches.Patch(color='salmon', label='TN'),
    ])

    bfig.subplots_adjust(
        left=0.04,
        right=0.96,
        bottom=0.13,
        top=0.96,
        wspace= 0.0,
        hspace=0.0
    )

    plotter.show()
    
    # # Model Tests -- Scores / Initial Distance distribution #

    sfig, sax = plotter.subplots(num=f'test_scores_by_iDist_scatter')

    sax.set_title('Model Tests -- Scores / Initial Distance (m) distribution')

    sax.set_xlabel('Initial Distance (m)')
    sax.set_ylabel('Score')

    sax.set_ylim([0.0, 2.5e-05])

    sax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    for i, k in enumerate(data):

        sax.scatter(
            x = data[k]['idist'],
            y = data[k]['scores'],
            color=cmap(i),
            label=k
        )
    
    sfig.subplots_adjust(
        left=0.04,
        right=0.96,
        bottom=0.13,
        top=0.96,
        wspace= 0.0,
        hspace=0.0
    )

    interactive_legend(sax).show()

    # # Model Tests -- Scores / yRot distribution #

    # s2fig, s2ax = plotter.subplots()

    # s2ax.set_title('Model Tests -- Scores / yRot distribution')

    # s2ax.set_ylim([0.0, 1.5e-05])

    # s2ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    # for k in data:
    #     s2ax.scatter(
    #         x = [r * 180 / math.pi for r in data[k]['yrot']],
    #         y = data[k]['scores'],
    #         color=np.random.rand(3,),
    #         label=k
    #     )
    
    # interactive_legend(s2ax).show()

    # Model Tests -- Scores / Initial Distance / yRot Distribution #

    s3dax = plotter.figure(num=f'test_scores_by_iDist_yRot_scatter3d').gca(projection='3d')

    s3dax.ticklabel_format(axis='z', style='sci', scilimits=(0,0))

    s3dax.set_title(f'Model Tests -- Scores / Initial Distance (m) / yRot (°) Distribution')
    
    s3dax.set_xlabel('Initial Distance (m)')
    s3dax.set_ylabel('yRot (°)')
    s3dax.set_zlabel('Score')

    for i, k in enumerate(data):
        
        s3dax.scatter(
            xs=data[k]['idist'],
            ys=[r * 180 /math.pi for r in data[k]['yrot']],
            zs=data[k]['scores'],
            # cmap=plotter.get_cmap('rainbow'),
            color= cmap(i), # np.random.rand(3,),
            label=k
        )

    interactive_legend(s3dax).show()

    # Model Tests -- Final Distance / Initial Distance / yRot Distribution #

    f3dax = plotter.figure(num=f'test_fDist_by_iDist_yRot_scatter3d').gca(projection='3d')

    f3dax.ticklabel_format(axis='z', style='sci', scilimits=(0,0))

    f3dax.set_title(f'Model Tests -- Final Distance (m) / Initial Distance (m) / yRot (°) Distribution')
    
    f3dax.set_xlabel('Initial Distance (m)')
    f3dax.set_ylabel('yRot (°)')
    f3dax.set_zlabel('Final Distance (m)')

    for i, k in enumerate(data):
        
        f3dax.scatter(
            xs=data[k]['idist'],
            ys=[r * 180 / math.pi for r in data[k]['yrot']],
            zs=data[k]['fdist'],
            # cmap=plotter.get_cmap('rainbow'),
            color= cmap(i), # np.random.rand(3,),
            label=k
        )

    interactive_legend(f3dax).show()


#######################################################################

def orderedby(x):

    s = x.with_suffix('').name.split('_')
    
    vs = OrderedDict()

    for t in s[-3:]:
        for k in patterns:
            
            m = regx.match(patterns[k]['pattern'], t)

            if m is not None:
                vs.update({
                    patterns[k]['orderidx']:patterns[k]['cleaner'](t)
                })
    
    r = [vs[k] for k in sorted(vs.keys(), reverse=True)]

    return tuple(r) if len(r) else tuple(x)

if __name__ == "__main__":
    
    config = parse_args_to_config()

    data = OrderedDict()

    if config.test_data_path.is_dir():

        for f in sorted(config.test_data_path.iterdir(), key=orderedby):
            print(f)
            if f.is_file() and 'json' in f.suffix and f.name.startswith('rtest_data_bn'):
                d = read_json(f)
                data[f.with_suffix('').name] = DataFrame.from_dict(d)
    else:
        d = read_json(config.test_data_path)
        data[config.test_data_path.with_suffix('').name] = DataFrame.from_dict(d)

    plot_data(data, config)
