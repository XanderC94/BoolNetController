import matplotlib.pyplot as plotter
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D

import math, itertools
import numpy as np
import statistics

from pandas import DataFrame, concat, Series
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.plot.colors import get_cmap, get_weighted_cmap
from bncontroller.collectionslib.utils import flat

def boxplot(
        y: list, x: list,
        window: str, title: str, xlabel: str, ylabel: str, ylims: list):

    cmap = get_cmap(len(y), name='rainbow')

    # Model Tests -- Scores distribution #

    fig, ax = plotter.subplots(num=window, figsize=(19, 11), dpi=138)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    ax.set_ylim(ylims)

    ax.boxplot(
        x=y,
        labels=x,
        # whis=[5, 95], # 1.5,
        # meanline=True,
        flierprops=dict(markerfacecolor='r', marker='D'),
    )

    plotter.xticks(
        list(range(1, len(x) + 1)),
        x, 
        rotation=15,
        size=10
    )

    fig.subplots_adjust(
        left=0.04,
        right=0.95,
        bottom=0.13,
        top=0.95,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def twin_bars(
        y1: list, y2:list, x: list,
        window: str, title: str, 
        xlabel: str, 
        y1label: str, y2label: str, 
        y1lims: list, y2lims: list,
        legend_labels: list,
        bars_offset=5):

    cmap = get_cmap(2, 'rainbow')

    colors = [cmap(i) for i in range(2)]

    fig, ax = plotter.subplots(num=window, figsize=(19, 11), dpi=138)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(y1label, color=colors[0])

    if y1lims:
        ax.set_ylim(y1lims)
    
    ax.tick_params('y', colors=colors[0])

    __x = 0.0

    for h1 in y1:
                
        ax.bar(
            x=__x,
            height=h1,
            color=colors[0],
            align='center',
            width=1.0
        )

        __x += 2 * bars_offset
    
    __x = 3.0

    plotter.xticks(
        np.arange(1.5, len(y1) * (2 * bars_offset), 2 * bars_offset),
        x, 
        rotation=15,
        size=10
    )

    plotter.legend(handles=[
        mpatches.Patch(color=cmap(i), label=legend_labels[i])
        for i in range(2)
    ])

    ax2 = ax.twinx()
    
    for h2 in y2:
                
        ax2.bar(
            x=__x,
            height=h2,
            color=colors[1],
            align='center',
            width=1.0
        )

        __x += 2 * bars_offset
    
    ax2.set_ylabel(y2label, color=colors[1])
    if y2lims:
        ax.set_ylim(y2lims)
    ax2.tick_params('y', colors=colors[1])

    fig.subplots_adjust(
        left=0.04,
        right=0.95,
        bottom=0.13,
        top=0.95,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def htwin_bars(
        x1: list, x2:list, y: list,
        window: str, title: str, 
        x1label: str, x2label: str,
        ylabel: str,
        x1lims: list, x2lims: list,
        legend_labels: list,
        bars_offset=5):

    cmap = get_cmap(2, 'rainbow')

    colors = [cmap(i) for i in range(2)]

    fig, ax = plotter.subplots(num=window, figsize=(19, 11), dpi=138)

    ax.set_title(title)
    ax.set_xlabel(x1label, color=colors[0])
    ax.set_ylabel(ylabel)
    if x1lims:
        ax.set_xlim(x1lims)
    ax.tick_params('x', colors=colors[0])

    __y = 0.0

    for w1 in x1:
                
        ax.barh(
            y=__y,
            width=w1,
            color=colors[0],
            align='center',
            height=1.0
        )

        __y += 2 * bars_offset
    
    __y = 3.0

    plotter.yticks(
        np.arange(1.5, len(x1) * (2 * bars_offset), 2 * bars_offset),
        y, 
        rotation=15,
        size=10
    )

    plotter.legend(handles=[
        mpatches.Patch(color=cmap(i), label=legend_labels[i])
        for i in range(2)
    ])

    ax2 = ax.twiny()
    
    for w2 in x2:
                
        ax2.barh(
            y=__y,
            width=w2,
            color=colors[1],
            align='center',
            height=1.0
        )

        __y += 2 * bars_offset
    
    ax2.set_xlabel(x2label, color=colors[1])
    if x2lims:
        ax.set_xlim(x2lims)
    ax2.tick_params('x', colors=colors[1])

    fig.subplots_adjust(
        left=0.10,
        right=0.95,
        bottom=0.05,
        top=0.875,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def bars(
        y: list, x: list,
        window: str, title: str, xlabel: str, ylabel: str, ylims: list,
        legend_labels: list,
        bars_offset=5):

    n = len(y[0])

    fig, ax = plotter.subplots(num=window, figsize=(19, 11), dpi=138)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if ylims:
        ax.set_ylim(ylims)

    cmap = get_cmap(n, 'rainbow')

    colors = [cmap(i) for i in range(n)]

    __x = 0

    for h in y:
                
        ax.bar(
            x=[__x + i for i in range(n)],
            height=h,
            color=colors,
            align='center'
        )

        __x += len(h) + bars_offset

    plotter.xticks(
        np.arange(1.5, len(y) * (n + bars_offset), n + bars_offset),
        x, 
        rotation=15,
        size=10
    )

    ax.legend(prop={'size': 7}, handles=[
        mpatches.Patch(color=cmap(i), label=legend_labels[i])
        for i in range(n)
    ])
    
    fig.subplots_adjust(
        left=0.04,
        right=0.95,
        bottom=0.13,
        top=0.95,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def hbars(
        x: list, y: list,
        window: str, title: str, xlabel: str, ylabel: str, xlims: list,
        legend_labels: list,
        bars_offset=5):

    n = len(x[0])

    fig, ax = plotter.subplots(num=window, figsize=(19, 11), dpi=138)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xlims:
        ax.set_xlim(xlims)

    cmap = get_cmap(n, 'rainbow')

    colors = [cmap(i) for i in range(n)]

    __y = 0

    for w in x:
                
        ax.barh(
            y=[__y + i for i in range(n)],
            width=w,
            color=colors,
            align='center'
        )

        __y += len(w) + bars_offset

    plotter.yticks(
        np.arange(1.5, len(x) * (n + bars_offset), n + bars_offset),
        y, 
        rotation=15,
        size=10
    )

    plotter.legend(handles=[
        mpatches.Patch(color=cmap(i), label=legend_labels[i])
        for i in range(n)
    ])

    fig.subplots_adjust(
        left=0.10,
        right=0.95,
        bottom=0.05,
        top=0.95,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def tbars(
        y: list, x: list,
        thresholds: list,
        window: str, title: str, xlabel: str, ylabel: str, ylims: list, 
        legend_label_fmt: str):

    fig, ax = plotter.subplots(num=window, figsize=(19, 11), dpi=138)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if ylims:
        ax.set_ylim(ylims)

    cmap = get_cmap(len(thresholds), 'rainbow')

    colors = [cmap(i) for i in range(len(thresholds))]

    __x = 0

    for h in y:
                
        ax.bar(
            x=[__x + i for i in range(len(thresholds))],
            height=h,
            color=colors,
            align='center'
        )

        __x += len(thresholds) + 3

    plotter.xticks(
        np.arange(1.5, len(y) * (len(thresholds) + 3), len(thresholds) + 3),
        x, 
        rotation=15,
        size=10
    )

    plotter.legend(handles=[
        mpatches.Patch(color=cmap(i), label=legend_label_fmt.format(k=k))
        for i, k in enumerate(thresholds)
    ])

    fig.subplots_adjust(
        left=0.04,
        right=0.95,
        bottom=0.13,
        top=0.95,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def scatter2d(
        y: list, x: list, k: list,
        window: str, title: str, xlabel: str, ylabel: str, ylims: list):
    
    cmap = get_cmap(len(k), name='rainbow')

    fig, ax = plotter.subplots(num=window, figsize=(19, 11), dpi=138)

    ax.set_title(title)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.set_ylim(ylims)

    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    for i, _k in enumerate(k):

        ax.scatter(
            x = x[i],
            y = y[i],
            color=cmap(i),
            label=_k
        )
    
    ax.legend(prop={'size': 10})

    fig.subplots_adjust(
        left=0.04,
        right=0.95,
        bottom=0.13,
        top=0.95,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def scatter3d(
        y: list, x: list, z: list,
        k: list,
        window: str, title: str, xlabel: str, ylabel: str, zlabel: str, zlims: list):

    cmap = get_cmap(len(k), name='rainbow')

    fig = plotter.figure(num=window, figsize=(19, 11), dpi=138)
    ax = fig.gca(projection='3d')

    ax.set_title(title)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    ax.set_zlim3d(zlims)

    ax.ticklabel_format(axis='z', style='sci', scilimits=(0,0))
    
    for i, _k in enumerate(k):
        
        ax.scatter(
            xs=x[i],
            ys=y[i],
            zs=z[i],
            color= cmap(i),
            label=_k
        )
    
    ax.view_init(elev=30, azim=225)
        
    ax.legend(prop={'size': 10})

    return fig, ax

    pass

def scatter4d(
    y: list, x: list, z: list, w: list,
    k: list,
    window: str, title: str, xlabel: str, ylabel: str, zlabel: str, zlims: list):

    cmap = get_weighted_cmap(flat(w), name='rainbow')

    fig = plotter.figure(num=window, figsize=(19, 11), dpi=138)
    ax = fig.gca(projection='3d')

    ax.set_title(title)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    ax.set_zlim3d(zlims)

    ax.ticklabel_format(axis='z', style='sci', scilimits=(0,0))

    for i, _k in enumerate(k):
        
        ax.scatter(
            xs=x[i],
            ys=y[i],
            zs=z[i],
            color=cmap.to_rgba(w[i]),
            label=_k
        )
        
    ax.legend(prop={'size': 10})

    return fig, ax

    pass