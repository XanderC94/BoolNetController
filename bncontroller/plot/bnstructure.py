from bncontroller.boolnet.bnstructures import BooleanNetwork
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plotter
import matplotlib.colors as colors
import matplotlib.cm as cmx
from bncontroller.sim.config import parse_args_to_config
from bncontroller.jsonlib.utils import read_json

def __nodes_std_positioning(I, H, O, ydim=(25, 0, -25)):

    iy, hy, oy = ydim
    ix, hx, ox = -int(len(I)/2), -int(len(H)/2), -int(len(O)/2)

    spos = dict()

    for k in set(I + H + O):

        if k in I:
            spos[k] = (ix, iy)
            ix += 1.0
        elif k in O:
            spos[k] = (ox, oy)
            ox += 1.0
        else:
            spos[k] = (hx, hy)
            hx += 1.0
    
    return spos

#########################################################################

def __fill_nx_legend(ax, legend, cmap):

    norm_color = colors.Normalize(vmin=0, vmax=1.0)
    scalar_map = cmx.ScalarMappable(norm=norm_color, cmap=cmap)

    for label, color in legend.items():
        ax.scatter([],[], color=scalar_map.to_rgba(color), label=label)

#########################################################################

def plot_booleannetwork(bn: BooleanNetwork, I:list = [], O:list = []):

    # Build DiGraph #

    dg = nx.DiGraph()

    for k, node in bn:
        if len(node.predecessors) == 0:
            dg.add_node(k)
        else:
            dg.add_edges_from([(p, k) for p in node.predecessors])

    # Coloring #
    color_legend = {'I':0.5, 'H':0.0, 'O':1.0}

    val_map = defaultdict(lambda: color_legend['H'])
    val_map.update([(k, color_legend['I']) for k in I])
    val_map.update([(k, color_legend['O']) for k in O])

    nodes_colors = [val_map[node] for node in dg.nodes()]

    ## https://matplotlib.org/examples/color/colormaps_reference.html
    color_map = plotter.get_cmap('rainbow')

    # Node Standard Positioning #
    spos = __nodes_std_positioning(I, [k for k in dg.nodes() if k not in I + O], O)

    # fixed=list(k for k in dg.nodes() if k in I + O)
    # print(fixed)

    # pos = nx.spring_layout(dg, pos=spos, k=5.0, center=(0,0))
    dis = dict((k, dict((p, 1.0) for p in dg.nodes() if p != k))for k in dg.nodes())
    # dis = None
    pos = nx.kamada_kawai_layout(dg, dist= dis, pos=spos, center=(0,0))

    # Plotting #

    fig = plotter.figure()
    ax = fig.add_subplot(1,1,1)

    __fill_nx_legend(ax, color_legend, color_map)

    nx.draw_networkx(
        dg, pos, 
        ax = ax,
        cmap=color_map,
        node_color=nodes_colors, 
        node_size=500,
        with_labels=True,
        arrows=True
    )

    plotter.legend(
        frameon=False,
        loc='upper right'
    )
    plotter.show()

################################################################

if __name__ == "__main__":
    
    config = parse_args_to_config()

    i, o = config.bn_n_inputs, config.bn_n_outputs

    bn = BooleanNetwork.from_json(read_json(config.bn_model_path))

    plot_booleannetwork(bn, list(map(str, range(i))), list(map(str, range(i, i+o))))
