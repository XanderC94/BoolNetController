import matplotlib.pyplot as plotter
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D

import math, itertools
import numpy as np
import statistics

from pandas import DataFrame, concat, Series
from bncontroller.plot.ilegend import interactive_legend
from bncontroller.plot.colors import get_cmap
from bncontroller.collectionslib.utils import flat

def boxplot(
        y: list, x: list,
        window: str, title: str, xlabel: str, ylabel: str, ylims: list, ):

    cmap = get_cmap(len(y), name='rainbow')

    # Model Tests -- Scores distribution #

    fig, ax = plotter.subplots(num=window)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    ax.set_ylim(ylims)

    ax.boxplot(
        x=y,
        labels=x,
        whis=[5, 95], # 1.5,
        # meanline=True,
        flierprops=dict(markerfacecolor='r', marker='D'),
    )

    plotter.xticks(
        list(range(1, len(x) + 1)),
        x, 
        rotation=15
    )

    fig.subplots_adjust(
        left=0.04,
        right=0.96,
        bottom=0.13,
        top=0.96,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def tbars(
        y: list, x: list,
        thresholds: list,
        window: str, title: str, xlabel: str, ylabel: str, ylims: list, 
        legend_label_fmt: str):

    fig, ax = plotter.subplots(num=window)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
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
        rotation=15
    )

    plotter.legend(handles=[
        mpatches.Patch(color=cmap(i), label=legend_label_fmt.format(k=k))
        for i, k in enumerate(thresholds)
    ])

    fig.subplots_adjust(
        left=0.04,
        right=0.96,
        bottom=0.13,
        top=0.96,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def scatter2d(
        y: list, x: list, k: list,
        window: str, title: str, xlabel: str, ylabel: str, ylims: list):
    
    cmap = get_cmap(len(k), name='rainbow')

    fig, ax = plotter.subplots(num=window)

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
    
    fig.subplots_adjust(
        left=0.04,
        right=0.96,
        bottom=0.13,
        top=0.96,
        wspace= 0.0,
        hspace=0.0
    )

    return fig, ax

def scatter3d(
        y: list, x: list, z: list,
        k: list,
        window: str, title: str, xlabel: str, ylabel: str, zlabel: str, zlims: list):

    cmap = get_cmap(len(k), name='rainbow')

    fig = plotter.figure(num=window)
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

    return fig, ax

    pass