import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as colors
import matplotlib.patches as mpatches
import matplotlib.cm as cmx

import random, math, argparse
import numpy as np
from pandas import DataFrame
from pathlib import Path
from collections import OrderedDict
from bncontroller.json.utils import read_json
from bncontroller.sim.config import parse_args_to_config, SimulationConfig

###############################################################################

def interactive_legend(ax=None):
    if ax is None:
        ax = plotter.gca()
    if ax.legend_ is None:
        ax.legend()

    return InteractiveLegend(ax.legend_)

class InteractiveLegend(object):

    def __init__(self, legend):

        self.legend = legend
        self.fig = legend.axes.figure

        self.lookup_artist, self.lookup_handle = self._build_lookups(legend)
        self._setup_connections()

        self.update()

    def _setup_connections(self):
        for artist in self.legend.texts + self.legend.legendHandles:
            artist.set_picker(10) # 10 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def _build_lookups(self, legend):
        labels = [t.get_text() for t in legend.texts]
        handles = legend.legendHandles
        label2handle = dict(zip(labels, handles))
        handle2text = dict(zip(handles, legend.texts))

        lookup_artist = {}
        lookup_handle = {}
        for artist in legend.axes.get_children():
            if artist.get_label() in labels:
                handle = label2handle[artist.get_label()]
                lookup_handle[artist] = handle
                lookup_artist[handle] = artist
                lookup_artist[handle2text[handle]] = artist

        lookup_handle.update(zip(handles, handles))
        lookup_handle.update(zip(legend.texts, handles))

        return lookup_artist, lookup_handle

    def on_pick(self, event):
        handle = event.artist
        if handle in self.lookup_artist:
            artist = self.lookup_artist[handle]
            artist.set_visible(not artist.get_visible())
            self.update()

    def on_click(self, event):
        if event.button == 3:
            visible = False
        elif event.button == 2:
            visible = True
        else:
            return

        for artist in self.lookup_artist.values():
            artist.set_visible(visible)
        self.update()

    def update(self):
        for artist in self.lookup_artist.values():
            handle = self.lookup_handle[artist]
            if artist.get_visible():
                handle.set_visible(True)
            else:
                handle.set_visible(False)
        self.fig.canvas.draw()

    def show(self):
        plotter.show()

################################################################################

def get_cmap(n, name='hsv'):
    '''
    Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.
    '''
    return plotter.cm.get_cmap(name, n)

#################################################################################

def plot_data(data:dict, config:SimulationConfig):

    cmap = get_cmap(len(data), name='rainbow')

    # Model Tests -- Scores distribution #

    bpfig, bpax = plotter.subplots()

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

    # Model Tests -- rDist distribution #

    bp2fig, bp2ax = plotter.subplots()

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

    # Model Tests -- TP / FP #

    bfig, bax = plotter.subplots()

    bax.set_title(f'Model Tests -- TP & TN -- score <= {config.test_positives_threshold}')

    bax.set_xlabel('BN model')
    bax.set_ylabel('TP|TN (%)')

    x = 0

    for k in data:
        
        tp = sum(s <= config.test_positives_threshold for s in data[k]['scores'])

        bax.bar(
            x = [x+1, x+2],
            height = [
                tp / len(data[k]),
                 1 - tp / len(data[k]), # len(data[k]['scores']) - tp
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

    plotter.show()
    
    # # Model Tests -- Scores / Initial Distance distribution #

    sfig, sax = plotter.subplots()

    sax.set_title('Model Tests -- Scores / Initial Distance (m) distribution')

    sax.set_xlabel('Initial Distance (m)')
    sax.set_ylabel('Score')

    sax.set_ylim([0.0, 1.5e-05])

    sax.ticklabel_format(axis='y', style='sci', scilimits=(0,0))

    for i, k in enumerate(data):

        sax.scatter(
            x = data[k]['idist'],
            y = data[k]['scores'],
            color=cmap(i),
            label=k
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

    s3dax = plotter.figure().gca(projection='3d')

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

#######################################################################

def orderedby(x):

    s = x.with_suffix('').name.split('_')
    v1 = int(s[-1].replace('it', ''))
    v2 = s[-2]

    return (v2, v1)

if __name__ == "__main__":
    
    config = parse_args_to_config()

    data = OrderedDict()

    if config.test_data_path.is_dir():

        for f in sorted(config.test_data_path.iterdir(), key=orderedby):
            if f.is_file() and 'json' in f.suffix and f.name.startswith('rtest_data_bn'):
                d = read_json(f)
                data[f.with_suffix('').name] = DataFrame.from_dict(d)
    else:
        d = read_json(config.test_data_path)
        data[config.test_data_path.with_suffix('').name] = DataFrame.from_dict(d)

    plot_data(data, config)
