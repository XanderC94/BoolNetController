import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches

import random, math, argparse, itertools
import numpy as np
import re as regx
import statistics
import bncontroller.plot.utils as pu
import bncontroller.file.utils as fu
from pandas import DataFrame
from pathlib import Path
from collections import OrderedDict
from collections.abc import Iterable
from bncontroller.jsonlib.utils import read_json
from bncontroller.file.utils import cpaths
from bncontroller.sim.utils import GLOBALS
from bncontroller.parse.utils import parse_args
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.plot.colors import get_cmap
from bncontroller.plot.outputdata import plot_output
from bncontroller.collectionslib.utils import flat

#################################################################################

def plot_data(data: dict, positives_threshold: float):

    cmap = get_cmap(len(data), name='rainbow')

    # Model Tests -- Scores distribution #

    bpfig, bpax = plotter.subplots(num=f'test_score_boxplot')

    bpax.set_title('Model Tests -- Scores distribution (Less is Better)')
    bpax.set_xlabel('BN model')
    bpax.set_ylabel('Score')

    bpax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    bpax.set_ylim([0.0, 2.5e-05])

    bpax.boxplot(
        x=list(data[k]['score'] for k in data),
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

    bp2ax.set_ylim([0.0, 2.6])

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

    bfig, bax = plotter.subplots(num=f'test_positives_bars')

    bax.set_title(f'Model Tests -- Positives by Thresholds -- score <= {positives_threshold}')

    bax.set_xlabel('BN model')
    bax.set_ylabel('P|N (%)')

    bax.set_ylim([0, 1.1])

    x = 0

    thresholds = (
        [positives_threshold] 
        if isinstance(positives_threshold, float) 
        else positives_threshold
    )

    cmap_bars = get_cmap(len(thresholds), 'rainbow')
    colors = [cmap_bars(i) for i in range(len(thresholds))]

    for k in data:
        
        ps = [sum(s < t for s in data[k]['score']) / len(data[k]) for t in thresholds]
        
        bax.bar(
            x=[x+i for i in range(len(thresholds))],
            height=ps,
            color=colors,
            align='center'
        )

        x+=len(thresholds) + 3

    plotter.xticks(
        np.arange(1.5, len(data) * (len(thresholds) + 3), len(thresholds) + 3),
        list(data.keys()), 
        rotation=15
    )

    plotter.legend(handles=[
        mpatches.Patch(color=cmap_bars(i), label=f'score < {str(k)}')
        for i, k in enumerate(thresholds)
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
            y = data[k]['score'],
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

    s3dax.set_title(f'Model Tests -- Scores / Initial Distance (m) / yRot (°) Distribution')
    
    s3dax.set_xlabel('Initial Distance (m)')
    s3dax.set_ylabel('yRot (°)')
    s3dax.set_zlabel('Score')

    s3dax.set_zlim3d(0, 2.5e-05)

    s3dax.ticklabel_format(axis='z', style='sci', scilimits=(0,0))
    
    for i, k in enumerate(data):
        
        s3dax.scatter(
            xs=data[k]['idist'],
            ys=[r * 180 /math.pi for r in data[k]['yrot']],
            zs=data[k]['score'],
            # cmap=plotter.get_cmap('rainbow'),
            color= cmap(i), # np.random.rand(3,),
            label=k
        )

    interactive_legend(s3dax).show()

    # Model Tests -- Final Distance / Initial Distance / yRot Distribution #

    f3dax = plotter.figure(num=f'test_fDist_by_iDist_yRot_scatter3d').gca(projection='3d')

    f3dax.set_title(f'Model Tests -- Final Distance (m) / Initial Distance (m) / yRot (°) Distribution')
    
    f3dax.set_xlabel('Initial Distance (m)')
    f3dax.set_ylabel('yRot (°)')
    f3dax.set_zlabel('Final Distance (m)')

    f3dax.ticklabel_format(axis='z', style='sci', scilimits=(0,0))

    f3dax.set_zlim3d(0, 2.6)

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

def collect_data(
        paths:Iterable, fpattern:str,
        recursively=False, ds_merge_level=3, 
        data_getter=pu.get_data):

    sortbykey = lambda x: x[0]

    def go(paths:Iterable, recursively, ds_merge_level):

        data = OrderedDict()

        for p in paths:
            
            print(p)
            
            if p.is_file():
                name, df = data_getter(p, fpattern, uniqueness=ds_merge_level)
                data[name] = data[name].append(df, ignore_index=True) if name in data else df

            elif p.is_dir() and recursively:
                
                data.update(
                    **data, 
                    **go(
                        sorted(
                            p.iterdir(), 
                            key=lambda x: pu.orderedby(x.name, fu.FNAME_PATTERN)
                        ),
                        recursively=recursively, 
                        ds_merge_level=ds_merge_level
                    )
                )

        return data

    return OrderedDict(sorted(go(paths, recursively, ds_merge_level).items(), key=sortbykey))

######################################################################

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser('Test Data plotter arguments parser.')

    parser.add_argument(
        '-m', '--merge_level', 
        default=3, 
        type=int,
        choices=[1, 2, 3],
        help='Level of merge between dataset of the same model.'
    )

    parser.add_argument(
        '-r', '--recursively', 
        default=True,
        help='DO NOT Recursively explore directories for valid datasets.',
        action='store_false'
    )

    args, *_ = parse_args(parser=parser)

    # print(args.config.test_data_path)

    data = OrderedDict(**collect_data(
        cpaths(args.config.test_data_path),
        fpattern=r'rtest_data_(?:bn_subopt_)?' + f'{fu.FNAME_PATTERN}.json',
        recursively=args.recursively, 
        ds_merge_level=args.merge_level
    ))

    plot_data(data, args.config.plot_positives_threshold)


