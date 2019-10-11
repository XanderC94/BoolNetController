import matplotlib.pyplot as plotter
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D

import random, math, argparse, itertools
import numpy as np
import re as regx
import statistics
import bncontroller.plot.utils as pu
import bncontroller.filelib.utils as fu
import bncontroller.plot.plotter as plot

from pandas import DataFrame, concat, Series
from pathlib import Path
from collections import OrderedDict
from collections.abc import Iterable
from bncontroller.jsonlib.utils import read_json
from bncontroller.filelib.utils import cpaths
from bncontroller.sim.utils import GLOBALS, Config, Point3D, load_global_config
from bncontroller.stubs.aggregators import weighted_pt, weighted_apt
from bncontroller.parse.utils import parse_args
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.plot.colors import get_cmap
from bncontroller.collectionslib.utils import flat, transpose
from bncontroller.boolnet.selector import SelectiveBooleanNetwork

#################################################################################

to_world_ref_system = {
    0: 315*math.pi/180,
    0.77: 0,
    1.27: math.pi/6,
    1.87: math.pi/3,
    2.37: math.pi/2,
    3.14159: math.pi/2 + math.pi/4,
    4.21: 195*math.pi/180,
    5.21: 255*math.pi/180,
}

def meta_str(info: dict):

    return '{N}_{K}_{T}'.format(
        N=info['N'],
        K=info['K'],
        T='%d_%d' % (
            info['atm'][0][0]*100, info['atm'][1][1]*100,
        )
    )

#########################################################################################

def aggregate_data(data: dict, infos: dict, phase_len: int, light_intensity: float, least_opt_wpt_score: float):

    ds = DataFrame()

    cols1 = [
        'bn', 
        'pt_score', 'apt_score', 'wpt', 'wapt',
        'pt_idist', 'pt_fdist', 'apt_idist', 'apt_fdist',
        'pt_yrot', 'apt_yrot', 'apt_fyrot',
        'n1a0p', 'n1a1p', 'n2a0p', 'n2a1p', 
        'n1rd', 'n2rd', 
        's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8',
        'ss', 'sr',
        'a0len', 'a1len',
        'pt_apos_x', 'pt_apos_z',
        'apt_apos_x', 'apt_apos_z',
    ]

    for k in data:
        
        data[k].replace(to_replace=np.nan, value=np.inf, inplace=True)

        data[k]['bn'] = f'{k}\n{meta_str(infos[k])}'

        data[k]['wpt'] = weighted_pt(
            data[k]['pt_score'] * light_intensity, 
            data[k]['pt_idist'], 
            data[k]['pt_fdist']
        )
                
        data[k]['wapt'] = weighted_apt(
            data[k]['apt_score'] * light_intensity, 
            data[k]['apt_idist'], 
            data[k]['apt_fdist']
        )
                    
        if 'noise1_score' in data[k] and 'noise2_score' in data[k]:
            data[k]['noise1_a1_count'] = phase_len / (1 + data[k]['noise1_score'])
            data[k]['noise1_a0_count'] = data[k]['noise1_score'] * data[k]['noise1_a1_count']
            data[k]['noise2_a1_count'] = phase_len / (1 + data[k]['noise2_score'])
            data[k]['noise2_a0_count'] = data[k]['noise2_score'] * data[k]['noise2_a1_count']
        
        data[k]['n1a0p'] = data[k]['noise1_a0_count'] / (data[k]['noise1_a1_count'] + data[k]['noise1_a0_count'])
        data[k]['n1a1p'] = 1.0 - data[k]['n1a0p']
        data[k]['n2a0p'] = data[k]['noise2_a0_count'] / (data[k]['noise2_a1_count'] + data[k]['noise2_a0_count'])
        data[k]['n2a1p'] = 1.0 - data[k]['n2a0p']
        
        data[k]['n1rd'] = abs(1.0 - data[k]['noise1_a0_count'] / data[k]['noise1_a1_count'])
        data[k]['n2rd'] = abs(1.0 - data[k]['noise2_a0_count'] / data[k]['noise2_a1_count'])
            
        mrho_a0 = infos[k]['atm'][0][0] * 0.5 + infos[k]['atm'][1][0] * 0.5
        mrho_a1 = infos[k]['atm'][0][1] * 0.5 + infos[k]['atm'][1][1] * 0.5
        
        data[k]['s1'] = (abs(data[k]['n1a0p'] - mrho_a0) < 0.1) & (abs(data[k]['n1a1p'] - mrho_a1) < 0.1)
        data[k]['s2'] = (abs(data[k]['n2a0p'] - mrho_a0) < 0.1) & (abs(data[k]['n2a1p'] - mrho_a1) < 0.1)
        data[k]['s3'] = data[k]['pt_fdist'] - data[k]['pt_idist'] < 0.35
        data[k]['s4'] = data[k]['apt_fdist'] - data[k]['apt_idist'] > 0.35
        data[k]['s5'] = data[k]['wpt'] <= least_opt_wpt_score
        data[k]['s6'] = data[k]['wapt'] >= data[k]['wpt']
        
        # print(data[k][['pt_a01_ratio', 'apt_a01_ratio']])

        if infos[k]['ai_map']['0'] == 'a0':
            data[k]['s7'] = 1 / data[k]['pt_a01_ratio'] < 0.15
            data[k]['s8'] = data[k]['apt_a01_ratio'] < 0.15
        else:
            data[k]['s7'] = data[k]['pt_a01_ratio'] < 0.15
            data[k]['s8'] = 1 / data[k]['apt_a01_ratio'] < 0.15
            
            
        data[k]['ss'] = data[k][['s1','s2','s3','s4','s5','s6', 's7', 's8']].mean(axis=1)
        data[k]['sr'] = data[k]['ss'] == 1.0
        
        data[k]['pt_score'] *= light_intensity
        data[k]['apt_score'] *= light_intensity
        # data[k]['delta_score'] = data[k]['apt_score'] * light_intensity - data[k]['pt_score'] * light_intensity
        
        # data[k]['pt_yrot'] = data[k]['pt_yrot'].apply(lambda x: pu.to_deg(x - math.pi / 2))
        data[k]['pt_yrot'] = data[k]['pt_yrot'].apply(lambda x: pu.to_deg(to_world_ref_system[x]))
        # data[k]['apt_yrot'] = data[k]['apt_yrot'].apply(lambda x: pu.to_deg(x - math.pi / 2))
        data[k]['apt_yrot'] = data[k]['apt_yrot'].apply(lambda x: pu.to_deg(to_world_ref_system[x]))
        
        if 'apt_fyrot' not in data[k]:
            data[k]['apt_fyrot'] = 180
        else:
            # data[k]['apt_fyrot'] = data[k]['apt_fyrot'].apply(lambda x: pu.to_deg(x - math.pi / 2))
            data[k]['apt_fyrot'] = pu.to_deg(data[k]['apt_fyrot'] - math.pi / 2)
        
        data[k]['a0len'] = infos[k]['a_len']['a0']
        data[k]['a1len'] = infos[k]['a_len']['a1']

        data[k][['pt_apos_x', 'pt_apos_y', 'pt_apos_z']] = data[k]['pt_apos'].apply(Series)
        
        data[k][['apt_apos_x', 'apt_apos_y', 'apt_apos_z']] = data[k]['apt_apos'].apply(Series)
                
        ds = ds.append(data[k][cols1], ignore_index=True)
                
        # print(data[k][['pt_score', 'wpt', 'pt_idist', 'pt_fdist', 'apt_score', 'wapt', 'apt_fdist']])
    
    return ds
            
def round_data(ds: DataFrame):

    ds['pt_score'] = round(ds['pt_score'], 7)
    ds['apt_score'] = round(ds['apt_score'], 7)
    
    ds['n1a0p'] = round(ds['n1a0p'], 3)
    ds['n1a1p'] = round(ds['n1a1p'], 3)
    ds['n2a0p'] = round(ds['n2a0p'], 3)
    ds['n2a1p'] = round(ds['n2a1p'], 3)
    ds['n1rd'] = round(ds['n1rd'], 3)
    ds['n2rd'] = round(ds['n2rd'], 3)

    ds['wpt'] = round(ds['wpt'], 7)
    ds['wapt'] = round(ds['wapt'], 7)
    ds['ss'] = round(ds['ss'], 3)

    try:
        ds['pt_idist'] = round(ds['pt_idist'], 3)
        ds['pt_fdist'] = round(ds['pt_fdist'], 3)
        ds['apt_idist'] = round(ds['apt_idist'], 3)
        ds['apt_fdist'] = round(ds['apt_fdist'], 3)

        ds['pt_yrot'] = round(ds['pt_yrot'], 1)
        ds['apt_yrot'] = round(ds['apt_yrot'], 1)
        ds['apt_fyrot'] = round(ds['apt_fyrot'], 1)
    except Exception:
        pass

    try:
        ds['s1'] = round(ds['s1'], 3)
        ds['s2'] = round(ds['s2'], 3)
        ds['s3'] = round(ds['s3'], 3)
        ds['s4'] = round(ds['s4'], 3)
        ds['s5'] = round(ds['s5'], 3)
        ds['s6'] = round(ds['s6'], 3)
        ds['s7'] = round(ds['s7'], 3)
        ds['s8'] = round(ds['s8'], 3)
    except Exception:
        pass

    try:
        ds['sr'] = round(ds['sr'], 3)
    except Exception:
        pass

    return ds
#########################################################################################

def plot_data(data: dict, infos: dict, positives_threshold: float, light_intensity: float, phase_len: int):

    thresholds = [t * light_intensity for t in flat([positives_threshold])]
    
    LEAST_OPT_WPT_SCORE = round(sum(thresholds) / len(thresholds), 7) # round(max(thresholds) * 1.0 / 3.0, 7) 
    
    # LEAST_OPT_WAPT_SCORE = round(max(thresholds) * 3.0 / 1.0, 7) 

    simple_keys = set(map(lambda x: fu.get_simple_fname(x, fu.FNAME_PATTERN, parts=['%s','%s','%s'] ,uniqueness=2), data.keys()))

    model = 'all' if len(simple_keys) > 1 else simple_keys.pop()

    #######################################################################################
    
    cols = [
        'bn', 
        'pt_score', 'apt_score', 'wpt', 'wapt',
        # 'pt_idist', 'pt_fdist', 'apt_idist', 'apt_fdist',
        # 'pt_yrot', 'apt_yrot', 'apt_fyrot',
        'n1a0p', 'n1a1p', 'n2a0p', 'n2a1p', 
        'n1rd', 'n2rd',
        's1', 's2', 's3', 's4', 's5', 's6', 
        's7', 's8', 
        'ss', 'sr',
        'a0len', 'a1len',
        'pt_apos_x', 'pt_apos_z',
        'apt_apos_x', 'apt_apos_z',
    ]

    ds = aggregate_data(data, infos, phase_len, light_intensity, LEAST_OPT_WPT_SCORE)
    
    # ds = round_data(ds)

    ds.set_index([ds.index, 'bn'])

    data.clear()
    
    means = DataFrame(ds[cols]).groupby(by=['bn'], as_index=False).mean()

    means = round_data(means)

    ranks = DataFrame({
        'bn': means['bn'].values,
        'wpt': means['wpt'].rank(axis=0, method='dense', numeric_only=True, ascending=True).values,
        'wapt': means['wapt'].rank(axis=0, method='dense', numeric_only=True, ascending=False).values,
        'n1rd': means['n1rd'].rank(axis=0, method='dense', numeric_only=True, ascending=True).values,
        'n2rd': means['n2rd'].rank(axis=0, method='dense', numeric_only=True, ascending=True).values,
        'ss': means['ss'].rank(axis=0, method='dense', numeric_only=True, ascending=False).values,
        'sr': means['sr'].rank(axis=0, method='dense', numeric_only=True, ascending=False).values,
    })

    ranks['rscore'] = ranks.sum(axis=1)

    ranks['frank'] = ranks['rscore'].rank(axis=0, method='dense', numeric_only=True, ascending=True)

    ranks.sort_values(by=['frank'], inplace=True)

    ds['mrscore'] = float('+inf')
    ds['mfrank'] = float('+inf')
    means['rscore'] = float('+inf')
    means['frank'] = float('+inf')

    for k, r in ranks[['bn', 'frank']].values:
        means.loc[means['bn'] == k, ['frank']] = r
        ds.loc[ds['bn'] == k, ['mfrank']] = r

    for k, r in ranks[['bn', 'rscore']].values:
        means.loc[means['bn'] == k, ['rscore']] = r
        ds.loc[ds['bn'] == k, ['mrscore']] = r

    means.sort_values(by=['frank'], inplace=True)
    ds.sort_values(by=['mfrank'], inplace=True)
    
    print(means)

    # exit(1)
    
    b0fig, b0ax = plot.htwin_bars(
        x1=[*reversed(means[['sr']].values)],
        x2=[*reversed(means[['ss']].values)],
        y=[*reversed(means['bn'].values)],
        window=f'test_score_bars_{model}',
        title='Model Tests -- Satisfactions (Wider is better) -- by Rank (Upper-most is Better)',
        ylabel='Model',
        x1label='Satisfaction Rate (%)',
        x2label='Satisfaction Score',
        x1lims=[0, 1.1],
        x2lims=[0, 1.1],
        legend_labels=['Sat. Rate (%)', 'Sat. Score']
    )
    
    b1fig, b1ax = plot.bars(
        y=means[['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']].values,
        x=means['bn'].values,
        window=f'test_constraints_bars_{model}',
        title='Model Tests -- Test <i> Satisfaction (%) (Higher is better) -- by Rank (Left-most is Better)',
        xlabel='Model',
        ylabel='Test Satisfaction (%)',
        ylims=[0.0, 1.1],
        legend_labels=[
            'noise phase 1 -- | a[i] - mean(atm[i]) | < 0.15',
            'noise phase 2 -- | a[i] - mean(atm[i]) | < 0.15',
            'pt -- fdist - idist < 0.35',
            'apt -- fdist - idist > 0.35',
            f'wpt <= {LEAST_OPT_WPT_SCORE}',
            f'wapt >= wpt',
            '|APT| / |PT| < 0.15    (pt)',
            '|PT| / |APT| < 0.15    (apt)',
        ]
    )

    b2fig, b2ax = plot.bars(
        y=means[['a0len', 'a1len']].values,
        x=means['bn'].values,
        window=f'test_attr_length_bars_{model}',
        title='Model Tests -- Attractors Length -- by Rank (Left-most is Better)',
        xlabel='Model',
        ylabel='Attractor <i> length',
        ylims=[],
        legend_labels=[
            'a0',
            'a1'
        ]
    )
    
    # # Model Tests -- Scores distribution #

    keys = ds['bn'].unique()
    
    c = [
        'pt_score', 'apt_score', 
        'wpt', 'wapt', 
        'pt_idist', 'apt_idist', 
        'pt_fdist', 'apt_fdist', 
        'pt_yrot', 'apt_yrot', 'apt_fyrot',
        'pt_apos_x', 'pt_apos_z',
        'apt_apos_x', 'apt_apos_z',
    ]

    (
        pt,         apt,
        wpt,        wapt,
        ptidist,    aptidist,
        ptfdist,    aptfdist,
        ptyrot,     aptyrot,    aptfyrot,
        pt_apos_x, pt_apos_z,
        apt_apos_x, apt_apos_z,

    ) = ds[['bn'] + c].groupby(by=['bn'], sort=False)[c].agg(list).T.values

    bp11fig, bp11ax = plot.boxplot(
        y=wpt,
        x=keys,
        window=f'test_wpt_score_boxplot_{model}',
        title='Model Tests -- wPT scores distribution (Lower is Better)',
        xlabel='Model',
        ylabel='wPT Score',
        ylims=[-0.1e-05, 2.5e-05]
    )

    bp12fig, bp12ax = plot.boxplot(
        y=pt,
        x=keys,
        window=f'test_pt_score_boxplot_{model}',
        title='Model Tests -- PT scores distribution (Lower is Better)',
        xlabel='Model',
        ylabel='PT Score',
        ylims=[-0.1e-05, 2.5e-05]
    )

    bp21fig, bp21ax = plot.boxplot(
        y=wapt,
        x=keys,
        window=f'test_wapt_score_boxplot_{model}',
        title='Model Tests -- wAPT scores distribution (High is Better)',
        xlabel='Model',
        ylabel='wAPT Score',
        ylims=[-0.1e-05, 5e-05]
    )

    bp22fig, bp22ax = plot.boxplot(
        y=apt,
        x=keys,
        window=f'test_apt_score_boxplot_{model}',
        title='Model Tests -- APT scores distribution (High is Better)',
        xlabel='Model',
        ylabel='APT Score',
        ylims=[-0.1e-05, 2.5e-05]
    )

    bp31fig, bp31ax = plot.boxplot(
        y=[
            [a/b for a, b in zip(__apt, __pt)]
            for __apt, __pt in zip(apt, pt)
        ],
        x=keys,
        window=f'test_apt_pt_score_ratio_boxplot_{model}',
        title='Model Tests -- APT/PT scores ratio distribution (High is Better)',
        xlabel='Model',
        ylabel='APT/PT Score Ratio',
        ylims=[0, 3]
    )

    bp32fig, bp32ax = plot.boxplot(
        y=[
            [wa/wb for wa, wb in zip(__wapt, __wpt)]
            for __wapt, __wpt in zip(wapt, wpt)
        ],
        x=keys,
        window=f'test_wapt_wpt_score_ratio_boxplot_{model}',
        title='Model Tests -- wAPT/wPT scores ratio distribution (High is Better)',
        xlabel='Model',
        ylabel='wAPT/wPT Score Ratio',
        ylims=[0, 100]
    )

    # Model Tests -- rDist distribution #
    
    # plotter.show()
    
    # # # Model Tests -- Scores | Initial Distance distribution #
    
    sp1fig, sp1ax = plot.scatter2d(
        pt, 
        ptidist, 
        keys,
        window=f'test_pt_scores_by_iDist_scatter_{model}',
        title=f'Model Tests -- PT Scores | Initial Distance (m) distribution',
        xlabel='Initial Distance (m)',
        ylabel='PT Score',
        ylims=[-0.1e-05, 2.5e-05]
    )
    
    sp11fig, sp11ax = plot.scatter2d(
        wpt, 
        ptidist, 
        keys,
        window=f'test_wpt_scores_by_iDist_scatter_{model}',
        title=f'Model Tests -- wPT Scores | Initial Distance (m) distribution',
        xlabel='Initial Distance (m)',
        ylabel='wPT Score',
        ylims=[-0.1e-05, 2.5e-05]
    )

    # interactive_legend(sp1ax).show()

    sp2fig, sp2ax = plot.scatter2d(
        apt, 
        aptidist, 
        keys,
        window=f'test_apt_scores_by_iDist_scatter_{model}',
        title=f'Model Tests -- APT Scores | Initial Distance (m) distribution',
        xlabel='Initial Distance (m)',
        ylabel='APT Score',
        ylims=[-0.1e-05, 5e-05]
    )

    sp21fig, sp21ax = plot.scatter2d(
        wapt, 
        aptidist, 
        keys,
        window=f'test_wapt_scores_by_iDist_scatter_{model}',
        title=f'Model Tests -- wAPT Scores | Initial Distance (m) distribution',
        xlabel='Initial Distance (m)',
        ylabel='wAPT Score',
        ylims=[-0.1e-05, 5e-05]
    )

    # interactive_legend(sp2ax).show()

    sp3fig, sp3ax = plot.scatter2d(
        wapt, 
        aptfdist, 
        keys,
        window=f'test_wapt_scores_by_fDist_scatter_{model}',
        title=f'Model Tests -- wAPT Scores | Final Distance (m) distribution',
        xlabel='Final Distance (m)',
        ylabel='APT Score',
        ylims=[-0.1e-05, 5e-05]
    )

    # interactive_legend(sp3ax).show()

    # # Model Tests -- Scores | Initial Distance / yRot Distribution #

    sp3d11fig, sp3d11ax = plot.scatter3d(
        ptyrot, 
        ptidist, 
        pt, 
        keys,
        window=f'test_pt_scores_by_iDist_yRot_scatter3d_{model}',
        title=f'Model Tests -- PT Scores | Initial Distance (m) | yRot (°) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='PT Score',
        zlims=[0, 2.5e-05]
    )

    sp3d14fig, sp3d14ax = plot.scatter3d(
        ptyrot, 
        ptidist, 
        wpt, 
        keys,
        window=f'test_wpt_scores_by_iDist_yRot_scatter3d_{model}',
        title=f'Model Tests -- wPT Scores | Initial Distance (m) | yRot (°) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='wPT Score',
        zlims=[0, 2.5e-05]
    )

    # interactive_legend(sp3d14ax).show()
    
    sp3d12fig, sp3d12ax = plot.scatter3d(
        ptfdist, 
        ptidist, 
        pt, 
        keys,
        window=f'test_pt_scores_by_iDist_fDist_scatter3d_{model}',
        title=f'Model Tests -- PT Scores | Initial Distance (m) | Final Distance (m) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='Final Distance (m)',
        zlabel='PT Score',
        zlims=[0, 2.5e-05]
    )

    # interactive_legend(sp3d12ax).show()

    sp3d13fig, sp3d13ax = plot.scatter3d(
        ptfdist, 
        ptidist, 
        wpt, 
        keys,
        window=f'test_wpt_scores_by_iDist_fDist_scatter3d_{model}',
        title=f'Model Tests -- wPT Scores | Initial Distance (m) | Final Distance (m) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='Final Distance (m)',
        zlabel='wPT Score',
        zlims=[0, 2.5e-05]
    )

    # interactive_legend(sp3d13ax).show()
    
    sp3d21fig, sp3d21ax = plot.scatter3d(
        aptfdist, 
        aptidist, 
        apt, 
        keys,
        window=f'test_apt_scores_by_iDist_yrot_scatter3d_{model}',
        title=f'Model Tests -- APT Scores | Initial Distance (m) | Final Distance (m) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='Final Distance (m)',
        zlabel='APT Score',
        zlims=[0, 2.5e-05]
    )
    
    sp3d23fig, sp3d23ax = plot.scatter3d(
        aptyrot, 
        aptidist, 
        apt, 
        keys,
        window=f'test_apt_scores_by_iDist_fDist_scatter3d_{model}',
        title=f'Model Tests -- APT Scores | Initial Distance (m) | yRot (°)  Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='APT Score',
        zlims=[0, 2.5e-05]
    )

    # interactive_legend(sp3d21ax).show()

    sp3d22fig, sp3d22ax = plot.scatter3d(
        y=aptfdist, 
        x=aptidist, 
        z=wapt, 
        k=keys,
        window=f'test_wapt_scores_by_iDist_fDist_scatter3d_{model}',
        title=f'Model Tests -- wAPT Scores | Initial Distance (m) | Final Distance (m) Distribution',
        xlabel='Initial Distance (m)',
        ylabel='Final Distance (m)',
        zlabel='wAPT Score',
        zlims=[0, 5e-05]
    )

    sp3d24fig, sp3d24ax = plot.scatter3d(
        y=aptyrot, 
        x=aptidist, 
        z=wapt, 
        k=keys,
        window=f'test_wapt_scores_by_iDist_yrot_scatter3d_{model}',
        title=f'Model Tests -- wAPT Scores | Initial Distance (m) | yRot (°)  Distribution',
        xlabel='Initial Distance (m)',
        ylabel='yRot (°)',
        zlabel='wAPT Score',
        zlims=[0, 5e-05]
    )

    sp3d25fig, sp3d25ax = plot.scatter3d(
        y=aptfyrot, 
        x=aptfdist, 
        z=wapt, 
        k=keys,
        window=f'test_wapt_scores_by_fDist_fyrot_scatter3d_{model}',
        title=f'Model Tests -- wAPT Scores | Final Distance (m) | Final yRot (°)  Distribution',
        xlabel='Final Distance (m)',
        ylabel='Final yRot (°)',
        zlabel='wAPT Score',
        zlims=[0, 5e-05]
    )

    # sp4d1fig, sp4d1ax = plot.scatter3d(
    #     y=pt_apos_z, 
    #     x=pt_apos_x, 
    #     z=ptyrot, 
    #     # w=wpt, 
    #     k=keys,
    #     window=f'test_wpt_scores_by_idist_fDist_yrot_scatter4d_{model}',
    #     title=f'Model Tests -- wPT Scores | Initial Distance (m) | Final Distance (m) | yRot (°)  Distribution',
    #     xlabel='Initial Distance (m)',
    #     ylabel='yRot (°)',
    #     zlabel='Final Distance',
    #     zlims=[0, 360]
    # )

    # interactive_legend(sp4d1ax).show()

    # plotter.show()

    # exit(1)

    return model, [
        (b0fig, b0ax),
        (b1fig, b1ax),
        (b2fig, b2ax),
        (bp11fig, bp11ax),
        (bp12fig, bp12ax),
        (bp21fig, bp21ax),
        (bp22fig, bp22ax),
        (bp31fig, bp31ax),
        (bp32fig, bp32ax),
        (sp1fig, sp1ax),
        (sp11fig, sp11ax),
        (sp2fig, sp2ax),
        (sp21fig, sp21ax),
        (sp3fig, sp3ax),
        (sp3d11fig, sp3d11ax),
        (sp3d12fig, sp3d12ax),
        (sp3d13fig, sp3d13ax),
        (sp3d14fig, sp3d14ax),
        (sp3d21fig, sp3d21ax),
        (sp3d22fig, sp3d22ax),
        (sp3d23fig, sp3d23ax),
        (sp3d24fig, sp3d24ax),
        (sp3d25fig, sp3d25ax),
        # (sp4d1fig, sp4d1ax),
    ]

#######################################################################

def get_data(f: Path, pattern:str, uniqueness=3, parts=['%s','%s','%s']):

    key, df = pu.get_data(f, pattern, uniqueness, parts)

    return (
        key,
        concat([
            df['score'].apply(Series), 
            df['fdist'].apply(Series),
            # df[['pt_yrot', 'apt_yrot', '']]
            # df.drop(['score', 'fdist'], axis=1)
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

    for path in cpaths(args.config.bn_model_path, recursive=3):
        if path.is_file() and 'json' in path.suffix and 'bn' in path.name:

            jsonrepr = read_json(path)

            try:

                bn = SelectiveBooleanNetwork.from_json(jsonrepr)
    
                info = jsonrepr['gen_params']
                info['atm'] = bn.atm.tableau
                info['ai_map'] = bn.attractors_input_map
                info['a_len'] = dict(map(lambda a: (a[0], len(a[1])), bn.atm.dattractors.items()))

                name = pu.get_simple_fname(path.name, fu.FNAME_PATTERN, parts=['%s','%s','%s'], uniqueness=2)
                
                name = set(filter(
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

                model, figs = plot_data(
                    ks, bis, 
                    args.config.plot_positives_threshold, 
                    args.config.sim_light_intensity,
                    args.config.sim_run_time_s * 1000 / args.config.sim_timestep_ms / 4
                )

                pu.save_plots(
                    fu.get_dir(args.config.plot_image_path / model, create_if_dir=True), 
                    transpose(figs)[0]
                )

    else:
        model, figs = plot_data(
            data, bninfos, 
            args.config.plot_positives_threshold, 
            args.config.sim_light_intensity,
            args.config.sim_run_time_s * 1000 / args.config.sim_timestep_ms / 4
        )

        pu.save_plots(
            fu.get_dir(args.config.plot_image_path / model, create_if_dir=True), 
            transpose(figs)[0]
        )

