import matplotlib.pyplot as plotter
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D

import random, math, argparse, itertools
import numpy as np
import re as regx
import statistics
import bncontroller.plot.utils as pu
import bncontroller.file.utils as fu
import bncontroller.plot.plotter as plot

from pandas import DataFrame, concat, Series
from pathlib import Path
from collections import OrderedDict
from collections.abc import Iterable
from bncontroller.jsonlib.utils import read_json
from bncontroller.file.utils import cpaths
from bncontroller.sim.utils import GLOBALS, Config, Point3D, load_global_config
from bncontroller.parse.utils import parse_args
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.plot.colors import get_cmap
from bncontroller.collectionslib.utils import flat, transpose
from bncontroller.boolnet.selector import SelectiveBooleanNetwork

#################################################################################

def meta_str(info: dict):
    return '{N}_{K}_{T}'.format(
        N=info['N'],
        K=info['K'],
        T=round(info['tRho']*100)
    )

def plot_data(data: dict, infos: dict, positives_threshold: float):

    keys = [
        f'{k}\n{meta_str(infos[k])}'
        for k in data
    ]

    # # Model Tests -- Scores distribution #
    
    bp1fig, bp1ax = plot.boxplot(
        y=list(data[k]['apt_score'] - data[k]['pt_score'] for k in data),
        x=keys,
        window=f'test_delta_score_boxplot',
        title='Model Tests -- APT-PT Delta scores distribution (Higher is Better)',
        xlabel='Model',
        ylabel='Score',
        ylims=[-0.05e-06, 1e-06]
    )

    bp11fig, bp11ax = plot.boxplot(
        y=list(data[k]['pt_score'] for k in data),
        x=keys,
        window=f'test_pt_score_boxplot',
        title='Model Tests -- PT scores distribution (Lower is Better)',
        xlabel='Model',
        ylabel='Score',
        ylims=[-0.05e-06, 1e-06]
    )

    bp12fig, bp12ax = plot.boxplot(
        y=list(data[k]['apt_score'] - data[k]['pt_score'] for k in data),
        x=keys,
        window=f'test_apt_score_boxplot',
        title='Model Tests -- APT scores distribution (High is Better)',
        xlabel='Model',
        ylabel='Score',
        ylims=[-0.05e-06, 1e-06]
    )

    # Model Tests -- rDist distribution #

    bp2fig, bp2ax = plot.boxplot(
        y=list(data[k]['apt_fdist'] - data[k]['pt_fdist'] for k in data),
        x=keys,
        window=f'test_delta_fDist_boxplot',
        title='Model Tests -- APT-PT Delta final Distance distribution (Positive is Better)',
        xlabel='Model',
        ylabel='PT Distance (m)',
        ylims=[-0.25, 5]

    )

    bp21fig, bp21ax = plot.boxplot(
        y=list(data[k]['pt_fdist'] for k in data),
        x=keys,
        window=f'test_pt_fDist_boxplot',
        title='Model Tests -- PT final Distance distribution (Less is Better)',
        xlabel='Model',
        ylabel='PT Distance (m)',
        ylims=[-0.25, 5]

    )

    bp22fig, bp22ax = plot.boxplot(
        y=list(data[k]['apt_fdist'] for k in data),
        x=keys,
        window=f'test_apt_fDist_boxplot',
        title='Model Tests -- APT final Distance distribution (Higher is Better)',
        xlabel='Model',
        ylabel='APT Distance (m)',
        ylims=[-0.25, 5]

    )
    
    # # Model Tests -- TP / FP #

    thresholds=(
        [positives_threshold] 
        if isinstance(positives_threshold, float) 
        else positives_threshold
    )

    tb1fig, tb1ax = plot.tbars(
        y=[
            [sum(s < t for s in data[k]['pt_score']) / len(data[k]) for t in thresholds]
            for k in data
        ],
        x=keys,
        thresholds=thresholds,
        window=f'test_pt_positives_bars',
        title=f'Model Tests -- PT Positives by Thresholds -- score < {thresholds}',
        xlabel='Model',
        ylabel='P (%)',
        ylims=[0, 1.1],
        legend_label_fmt='score < {k}'
    )

    tb2fig, tb2ax = plot.tbars(
        y=[
            [sum(s > t for s in data[k]['apt_score']) / len(data[k]) for t in thresholds]
            for k in data
        ],
        x=keys,
        thresholds=thresholds,
        window=f'test_apt_positives_bars',
        title=f'Model Tests -- APT Positives by Thresholds -- score > {thresholds}',
        xlabel='Model',
        ylabel='P (%)',
        ylims=[0, 1.1],
        legend_label_fmt='score > {k}'
    )

    plotter.show()
    
    # # # Model Tests -- Scores / Initial Distance distribution #
    
    def to_deg(x):

        __x = flat([x])
        m = sum(__x) / max(1, len(__x))

        return m * 180 / math.pi

    y1, y2, x1, x2, r1, r2 = transpose([
        (
            data[k]['pt_score'],
            data[k]['apt_score'],
            data[k]['pt_idist'],
            data[k]['apt_idist'],
            data[k]['pt_yrot'].apply(to_deg),
            data[k]['apt_yrot'].apply(to_deg)
        ) 
        for i, k in enumerate(data)
    ])

    sp1fig, sp1ax = plot.scatter2d(
        y1, x1,
        list(data.keys()),
        window=f'test_pt_scores_by_iDist_scatter',
        title=f'Model Tests -- APT Scores / Initial Distance (m) distribution',
        xlabel='Initial Distance (m)',
        ylabel='Score',
        ylims=[0.0, 1.0e-06]
    )

    interactive_legend(sp1ax).show()

    sp2fig, sp2ax = plot.scatter2d(
        y2, x2,
        list(data.keys()),
        window=f'test_apt_scores_by_iDist_scatter',
        title=f'Model Tests -- APT Scores / Initial Distance (m) distribution',
        xlabel='Initial Distance (m)',
        ylabel='Score',
        ylims=[0.0, 1.0e-06]
    )

    interactive_legend(sp2ax).show()

    # # # Model Tests -- Scores / yRot distribution #

    # # Model Tests -- Scores / Initial Distance / yRot Distribution #

    sp3d1fig, sp3d1ax = plot.scatter3d(
        r1, x1, y1,
        list(data.keys()),
        window=f'test_pt_scores_by_iDist_yRot_scatter3d',
        title=f'Model Tests -- PT Scores / Initial Distance (m) / yRot (°) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='Score',
        zlims=[0, 1.0e-06]
    )

    interactive_legend(sp3d1ax).show()

    sp3d2fig, sp3d2ax = plot.scatter3d(
        r2, x2, y2,
        list(data.keys()),
        window=f'test_apt_scores_by_iDist_yRot_scatter3d',
        title=f'Model Tests -- APT Scores / Initial Distance (m) / yRot (°) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='Score',
        zlims=[0, 1.0e-06]
    )

    interactive_legend(sp3d2ax).show()

    # # Model Tests -- Final Distance / Initial Distance / yRot Distribution #

    # f3dax = plotter.figure(num=f'test_fDist_by_iDist_yRot_scatter3d').gca(projection='3d')

    # f3dax.set_title(f'Model Tests -- Final Distance (m) / Initial Distance (m) / yRot (°) Distribution')
    
    # f3dax.set_xlabel('Initial Distance (m)')
    # f3dax.set_ylabel('yRot (°)')
    # f3dax.set_zlabel('Final Distance (m)')

    # f3dax.ticklabel_format(axis='z', style='sci', scilimits=(0,0))

    # f3dax.set_zlim3d(0, 2.6)

    # for i, k in enumerate(data):
        
    #     f3dax.scatter(
    #         xs=data[k]['idist'],
    #         ys=[r * 180 / math.pi for r in data[k]['yrot']],
    #         zs=data[k]['fdist'],
    #         # cmap=plotter.get_cmap('rainbow'),
    #         color= cmap(i), # np.random.rand(3,),
    #         label=k
    #     )

    # interactive_legend(f3dax).show()

#######################################################################

def get_data(f: Path, pattern:str, uniqueness=3, parts=['%s','%s','%s']):

    key, df = pu.get_data(f, pattern, uniqueness, parts)

    return (
        key,
        concat([
            df['score'].apply(Series), 
            df['fdist'].apply(Series), 
            df.drop(['score', 'fdist'], axis=1)
        ], axis=1)
    )

######################################################################

if __name__ == "__main__":
    
    load_global_config()

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

    args = parse_args(parser=parser, config_converter=Config.from_file)

    data = OrderedDict(**pu.collect_data(
        cpaths(args.config.test_data_path),
        fpattern=r'rtest_data_(?:bn_subopt_)?' + f'{fu.FNAME_PATTERN}.json',
        recursively=args.recursively, 
        ds_merge_level=args.merge_level,
        data_getter=get_data
    ))

    bninfos = OrderedDict()

    for path in cpaths(args.config.bn_ctrl_model_path):

        if path.is_file() and 'json' in path.suffix and 'bn' in path.name:

            jsonrepr = read_json(path)

            try:

                bn = SelectiveBooleanNetwork.from_json(jsonrepr)
    
                info = jsonrepr['gen_params']
                info['atm'] = bn.atm.dattractors
                info['ai_map'] = bn.attractors_input_map

                name = pu.get_simple_fname(path.name, fu.FNAME_PATTERN, parts=['%s','%s','%s'], uniqueness=2)

                name = list(filter(
                    lambda x: '_'.join(x.split('_')[:2]) == name,
                    data.keys()
                ))

                for k in name:
                    bninfos.update({k: info})

            except Exception:
                pass

    if args.merge_level == 3:
        
        q = set(data.keys())

        for k, d in data.items():
            
            if k in q:

                ks = {k: d}
                bis = {k: bninfos[k]}

                for l in q:
                    if k != l and k.split('_')[:2] == l.split('_')[:2]:
                        ks.update({l: data[l]})  
                        bis.update({l: bninfos[l]})

                q.difference_update(set(ks.keys()))

                plot_data(ks, bis, args.config.plot_positives_threshold)

    else:
        plot_data(data, bninfos, args.config.plot_positives_threshold)


