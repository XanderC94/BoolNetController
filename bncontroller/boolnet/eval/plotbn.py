from bncontroller.boolnet.bnstructures import BooleanNetwork
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plotter
from bncontroller.sim.config import parse_args_to_config
from bncontroller.json.utils import read_json

def plot_booleannetwork(bn: BooleanNetwork, I:list, O:list):

    dg = nx.DiGraph()

    for k, node in bn:
        dg.add_edges_from([(p, k) for p in node.predecessors])

    val_map = defaultdict(lambda: 0.0)

    val_map.update([(k, 0.5) for k in I])
    val_map.update([(k, 1.0) for k in O])

    values = [val_map[node] for node in dg.nodes()]

    iy, hy, oy = 10.0, 0.0, -10.0
    ix, hx, ox = -int(len(I)/2), -int((len(bn) - len(I) - len(O))/2), -int(len(O)/2)

    spos = dict()

    for k in dg.nodes():

        if k in I:
            spos[k] = (ix, iy)
            ix += 1.0
        elif k in O:
            spos[k] = (ox, oy)
            ox += 1.0
        else:
            spos[k] = (hx, hy)
            hx += 1.0

    # fixed=list(k for k in dg.nodes() if k in I + O)

    # print(fixed)

    # pos = nx.spring_layout(dg, pos=spos, k=1.0, iterations=100, center=(0,0))
    pos = nx.kamada_kawai_layout(dg, pos=spos, center=(0,0))
    ## https://matplotlib.org/examples/color/colormaps_reference.html
    nx.draw_networkx_nodes(dg, pos, cmap=plotter.get_cmap('rainbow'), node_color = values, node_size = 500)

    nx.draw_networkx_labels(dg, pos)
    nx.draw_networkx_edges(dg, pos, edgelist=dg.edges(), arrows=True)

    plotter.legend(
        labels=['Input Nodes', 'Hidden Nodes', 'Output Nodes'], 
        frameon=False,
        loc='upper right'
    )
    plotter.show()

################################################################

if __name__ == "__main__":
    
    config = parse_args_to_config()

    i, o = config.bn_inputs, config.bn_outputs

    bn = BooleanNetwork.from_json(read_json(config.bn_model_path))

    plot_booleannetwork(bn, list(map(str, range(i))), list(map(str, range(i, i+o))))
