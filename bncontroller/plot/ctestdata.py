import matplotlib.pyplot as plotter

import random, math, argparse
import numpy as np
import bncontroller.plot.utils as pu
import bncontroller.plot.plotter as plots
import bncontroller.filelib.utils as fu
from pandas import DataFrame
from collections import OrderedDict
from bncontroller.jsonlib.utils import read_json
from bncontroller.filelib.utils import cpaths
from bncontroller.sim.utils import Config
from bncontroller.parse.utils import parse_args
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.collectionslib.utils import flat, transpose
from bncontroller.stubs.aggregators import weighted_pt, weighted_apt

#################################################################################

def plot_data(data: dict, positives_threshold: float, ascending=True):

    simple_keys = set(map(lambda x: fu.get_simple_fname(x, fu.FNAME_PATTERN, parts=['%s','%s','%s'], uniqueness=2), data.keys()))

    # print(simple_keys)

    model = 'all' if len(simple_keys) > 1 else simple_keys.pop()

    print(model)

    ds = DataFrame()

    c = ['score', 'wscore', 'idist', 'fdist', 'yrot']

    for k in data:
        data[k]['bn'] = k
        data[k]['wscore'] = weighted_pt(data[k]['score'], data[k]['idist'], data[k]['fdist'])
        data[k]['yrot'] = data[k]['yrot'].apply(pu.to_deg)
        ds = ds.append(data[k][['bn'] + c], ignore_index=True, sort=False)

    means = DataFrame(ds[['bn', 'score', 'wscore']]).groupby(by=['bn'], as_index=False).mean()
    
    ranks = DataFrame(dict(
        bn=means['bn'].values,
        mscore=means['score'].rank(axis=0, method='dense', numeric_only=True, ascending=ascending).values,
        mwscore=means['wscore'].rank(axis=0, method='dense', numeric_only=True, ascending=ascending).values
    ))

    ranks['rscore'] = ranks.sum(axis=1)
    ranks['frank'] = ranks['rscore'].rank(axis=0, method='dense', numeric_only=True, ascending=True)
    # ranks.sort_values(by=['frank'], inplace=True)
    
    ds['mfrank'] = float('+inf')
    means['frank'] = float('+inf')

    for k, r in ranks[['bn', 'frank']].values:
        means.loc[means['bn'] == k, ['frank']] = r
        ds.loc[ds['bn'] == k, ['mfrank']] = r

    means.sort_values(by=['frank'], inplace=True)
    ds.sort_values(by=['mfrank'], inplace=True)

    print(means)

    keys = ds['bn'].unique()

    (
        scores, wscores, idists, fdists, yrots
    ) = ds[['bn'] + c].groupby(by=['bn'], sort=False)[c].agg(list).T.values

    # Model Tests -- Scores distribution #

    bpfig, bpax = plots.boxplot(
        y=scores,
        x=keys,
        window=f'test_score_boxplot_{model}',
        title='Model Tests -- Scores distribution (Less is Better)',
        xlabel='Model',
        ylabel='Score',
        ylims=[0.0, 2.5e-05]
    )

    bp1fig, bp1ax = plots.boxplot(
        y=wscores,
        x=keys,
        window=f'test_wscore_boxplot_{model}',
        title='Model Tests -- wScores distribution (Less is Better)',
        xlabel='Model',
        ylabel='wScore',
        ylims=[0.0, 2.5e-05]
    )

    # Model Tests -- rDist distribution #

    bp2fig, bp2ax = plots.boxplot(
        y=fdists,
        x=keys,
        window=f'test_fDist_boxplot_{model}',
        title='Model Tests -- final Distance distribution (Less is Better)',
        xlabel='Model',
        ylabel='Final Distance (m)',
        ylims=[0.0, 2.6]
    )

    # Model Tests -- TP / FP #

    fi_ratio = 1.0 / 3.0

    thresholds = flat([positives_threshold])
    wthresholds = [
        round(t * fi_ratio, 7) 
        for t in thresholds
    ] if ascending else [
        round(t * 1.0 / fi_ratio, 7) for t in thresholds
    ]

    sign = '<' if ascending else '>'

    bfig, bax = plots.tbars(
        y=[
            *map(
                lambda __scores: [
                    sum(s < t if ascending else s > t for s in __scores) / len(__scores) 
                    for t in thresholds
                ],
                scores
            )
        ],
        x=keys,
        thresholds=thresholds,
        window=f'test_positives_bars_{model}',
        title=f'Model Tests -- Success Rate by Thresholds -- score {sign} {thresholds}',
        xlabel='Model',
        ylabel='Success Rate (%)',
        ylims=[0, 1.1],
        legend_label_fmt=f'score {sign} '+'{k}'
    )

    b1fig, b1ax = plots.tbars(
        y=[
            *map(
                lambda __wscores: [
                    sum(ws < wt if ascending else ws > wt for ws in __wscores) / len(__wscores) 
                    for wt in wthresholds
                ],
                wscores
            )
        ],
        x=keys,
        thresholds=wthresholds,
        window=f'test_wpositives_bars_{model}',
        title=f'Model Tests -- Success Rate by Thresholds -- wscore {sign} {wthresholds}',
        xlabel='Model',
        ylabel='Success Rate (%)',
        ylims=[0, 1.1],
        legend_label_fmt=f'wscore {sign} '+'{k}'
    )

    b2fig, b2ax = plots.tbars(
        y=[
            *map(
                lambda __wscores: [
                    sum(ws < t if ascending else ws > t for ws in __wscores) / len(__wscores) 
                    for t in thresholds
                ],
                wscores
            )
        ],
        x=keys,
        thresholds=thresholds,
        window=f'test_wtpositives_bars_{model}',
        title=f'Model Tests -- Success Rate by Thresholds -- wscore {sign} {thresholds}',
        xlabel='Model',
        ylabel='Success Rate (%)',
        ylims=[0, 1.1],
        legend_label_fmt=f'wscore {sign} '+'{k}'
    )

    # plotter.show()
    
    # # Model Tests -- Scores / Initial Distance distribution #

    sfig, sax = plots.scatter2d(
        y=scores, 
        x=idists,
        k=keys,
        window=f'test_scores_by_iDist_scatter_{model}',
        title=f'Model Tests -- Scores / Initial Distance (m) distribution',
        xlabel='Initial Distance (m)',
        ylabel='Score',
        ylims=[0.0, 2.5e-05]
    )
    

    s1fig, s1ax = plots.scatter2d(
        y=wscores, 
        x=idists,
        k=keys,
        window=f'test_wscores_by_iDist_scatter_{model}',
        title=f'Model Tests -- wScores / Initial Distance (m) distribution',
        xlabel='Initial Distance (m)',
        ylabel='wScore',
        ylims=[0.0, 2.5e-05]
    )
    
    # interactive_legend(sax).show()

    # Model Tests -- Scores / Initial Distance / yRot Distribution #

    s3fig, s3dax = plots.scatter3d(
        y=yrots, 
        x=idists, 
        z=scores,
        k=keys,
        window=f'test_scores_by_iDist_yRot_scatter3d_{model}',
        title=f'Model Tests -- Scores / Initial Distance (m) / yRot (°) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='Score',
        zlims=[0, 2.5e-05]
    )
    
    # interactive_legend(s3dax).show()

    s31fig, s31dax = plots.scatter3d(
        y=yrots, 
        x=idists, 
        z=wscores,
        k=keys,
        window=f'test_wscores_by_iDist_yRot_scatter3d_{model}',
        title=f'Model Tests -- wScores / Initial Distance (m) / yRot (°) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='wScore',
        zlims=[0, 2.5e-05]
    )
    
    # interactive_legend(s31dax).show()

    # Model Tests -- Final Distance / Initial Distance / yRot Distribution #

    f3fig, f3dax = plots.scatter3d(
        y=yrots, 
        x=idists, 
        z=fdists,
        k=keys,
        window=f'test_fDist_by_iDist_yRot_scatter3d_{model}',
        title=f'Model Tests -- Final Distance (m) / Initial Distance (m) / yRot (°) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='Final Distance (m)',
        zlims=[0, 2.6]
    )
    
    # interactive_legend(f3dax).show()

    fsfig, fsdax = plots.scatter3d(
        y=fdists, 
        x=idists, 
        z=wscores,
        k=keys,
        window=f'test_wscore_by_iDist_fDist_scatter3d_{model}',
        title=f'Model Tests -- wScore / Initial Distance (m) / Final Distance (m) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='Final Distance (m)',
        zlabel='wScore',
        zlims=[0, 2.5e-05]
    )
    
    # interactive_legend(fsdax).show()

    # fsdax.show()

    # plotter.show()
    
    # exit(1)

    return model, [
        (bpfig, bpax),
        (bp1fig, bp1ax),
        (bp2fig, bp2ax),
        (bfig, bax),
        (b1fig, b1ax),
        (b2fig, b2ax),
        (sfig, sax),
        (s1fig, s1ax),
        (s3fig, s3dax),
        (s31fig, s31dax),
        (f3fig, f3dax),
        (fsfig, fsdax),
    ]

#######################################################################

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

    args = parse_args(parser=parser, config_converter=Config.from_file)

    data = OrderedDict(**pu.collect_data(
        cpaths(args.config.test_data_path),
        fpattern=r'rtest_data_(?:bn_subopt_)?' + f'{fu.FNAME_PATTERN}.json',
        recursively=args.recursively, 
        ds_merge_level=args.merge_level
    ))

    if args.merge_level == 3:

        q = set(data.keys())

        for k, d in data.items():
            
            if k in q:

                ks = {k: d}

                for l in q:
                    if k != l and k.split('_')[:2] == l.split('_')[:2]:
                        ks.update({l: data[l]})  

                q.difference_update(set(ks.keys()))

                model, figs = plot_data(
                    ks, args.config.plot_positives_threshold, 
                    ascending=args.config.webots_agent_controller == "phototaxis"
                )

                pu.save_plots(
                    fu.get_dir(args.config.plot_image_path / model, create_if_dir=True), 
                    transpose(figs)[0]
                )
    else:
        model, figs = plot_data(
            data, args.config.plot_positives_threshold, 
            ascending=args.config.webots_agent_controller == "phototaxis"
        )

        pu.save_plots(
            fu.get_dir(args.config.plot_image_path / model, create_if_dir=True), 
            transpose(figs)[0]
        )


