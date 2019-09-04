import matplotlib.pyplot as plotter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as colors
import matplotlib.patches as mpatches
import matplotlib.cm as cmx

################################################################################

def get_cmap(n, name='hsv'):
    '''
    Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.
    '''
    return plotter.cm.get_cmap(name, n)

def get_weighted_cmap(ws, name='hsv'):

    return cmx.ScalarMappable(
            norm=plotter.get_cmap(name), 
            cmap=colors.Normalize(vmin=min(ws), vmax=max(ws))
        )