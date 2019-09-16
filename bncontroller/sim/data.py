from bncontroller.jsonlib.utils import Jsonkin
from bncontroller.collectionslib.utils import flat
import json, random, math, enum, numpy as np
from collections import defaultdict
from pathlib import Path

class Point3D(Jsonkin):

    def __init__(self, x:float, y:float, z:float):

        self.x = x
        self.y = y
        self.z = z

    def __check_instance(self, that):
        if isinstance(that, Point3D):
            return that
        elif isinstance(that, dict):
            return Point3D.from_json(that)
        elif isinstance(that, (tuple, list)):
            return Point3D.from_tuple(that)
        else:
            raise Exception('Invalid 3D Point representation.')

    def dist(self, that) -> float:
        
        _that = self.__check_instance(that)

        return math.sqrt(
            (self.x - _that.x)**2 + (self.y - _that.y)**2 + (self.z - _that.z)**2
        )
    
    def to(self, x, y, z):
        self.x = x
        self.z = z
        self.y = y
        return self

    def __iter__(self):
        for c in [self.x, self.y, self.z]: 
            yield c
        
    def __add__(self, that):
        return Point3D(self.x + that.x, self.y + that.y, self.z + that.z)
    
    def __abs__(self):
        return Point3D(abs(self.x), abs(self.y), abs(self.z))

    def __eq__(self, that):
        if isinstance(that, Point3D):
            return self.x == that.x and self.y == that.y and self.z == that.z
        else:
            return False

    def to_json(self) -> dict:
        return vars(self)

    def to_tuple(self) -> tuple:
        return tuple(self)

    @staticmethod
    def from_polar(r, el, az):
        return Point3D(
                x = r * math.sin(el) * math.sin(az),
                y = r * math.cos(el),
                z = r * math.sin(el) * math.cos(az)
            )

    @staticmethod
    def from_json(json: dict):
        return Point3D(
            json['x'],
            json['y'],
            json['z']
        )

    @staticmethod
    def from_tuple(coordinates):
        return Point3D(coordinates[0], coordinates[1], coordinates[2])

#####################################################################

@enum.unique
class Axis(enum.Enum):
    X = lambda r, el, az: Point3D.from_polar(r, el=el, az=0.0)
    Y = lambda r, el, az: Point3D.from_polar(r, el=math.pi/2, az=az)
    Z = lambda r, el, az: Point3D.from_polar(r, el=el, az=math.pi/2)
    NONE = lambda r, el, az: Point3D.from_polar(r, el, az)

@enum.unique
class Quadrant(enum.Enum):
    PPP = lambda p: abs(p)
    PPN = lambda p: p.to( abs(p.x),  abs(p.y), -abs(p.z))
    PNN = lambda p: p.to( abs(p.x), -abs(p.y), -abs(p.z))
    NNN = lambda p: p.to(-abs(p.x), -abs(p.y), -abs(p.z))
    NNP = lambda p: p.to(-abs(p.x), -abs(p.y),  abs(p.z))
    NPP = lambda p: p.to(-abs(p.x),  abs(p.y),  abs(p.z))
    NPN = lambda p: p.to(-abs(p.x),  abs(p.y), -abs(p.z))
    PNP = lambda p: p.to( abs(p.x), -abs(p.y),  abs(p.z))
    ANY = lambda p: p

    @staticmethod
    def get(key):
        return getattr(Quadrant, key)

def r_point3d(O=Point3D(0.0, 0.0, 0.0), R=1.0, axis=Axis.NONE, quadrant=Quadrant.ANY):
    
    R = R if isinstance(R, (list, tuple)) and len(R) > 1 else flat([0.0, R])
    
    r = min(R) + abs(R[0] - R[1]) * np.random.uniform(0, 1.0)

    el = math.acos(1.0 - 2.0 * np.random.uniform(0.0, 1.0)) # better distribution
    # el = np.random.uniform(-1.0, 1.0) * math.pi 
    az = np.random.uniform(0.0, 1.0) * 2 * math.pi

    return O + quadrant(axis(r, el, az))

##################################################################

class SimulationStepData(Jsonkin):

    def __init__(self,
        n_step: int,
        position: Point3D,
        bnstate: dict,
        light_values: list,
        distance_values: list,
        bumps_values: list,
        noise: bool = None,
        attr: str = None,
        input: int = None
        ):

        self.n_step = n_step
        self.bnstate = bnstate
        self.position = position
        self.light_values = light_values
        self.distance_values = distance_values
        self.bumps_values = bumps_values
        self.noise = bumps_values
        self.attr = bumps_values
        self.input = bumps_values
        
    def to_json(self) -> dict:
        return {
            'n_step': self.n_step,
            'position': self.position.to_json(),
            'bnstate': self.bnstate,
            'light_values': self.light_values,
            'distance_values': self.distance_values,
            'bumps_values': self.bumps_values,
            'noise': self.noise,
            'attr': self.attr,
            'input': self.input
        }
    
    @staticmethod
    def from_json(json:dict):
        return SimulationStepData(
            json['n_step'],
            Point3D.from_json(json['position']),
            json['bnstate'],
            json['light_values'],
            json['distance_values'],
            json['bumps_values'],
            json['noise'],
            json['attr'],
            json['input']
        )

#######################################################################

class BNParams(object):
    '''
    Container for BN generation parameters
    '''
    def __init__(self, N: int, K: int, P: float, Q: float, I: int, O: int):
        
        self.N = N
        self.K = K
        self.P = P
        self.Q = Q
        self.I = I
        self.O = O
    
    def __iter__(self):
        for i in vars(self).values():
            yield i

class ArenaParams(object):
    '''
    Container for Webots Arena options
    '''
    def __init__(self, 
            floor_size=(3, 3), 
            sim_config=Path('.'),
            controller='void'):
        
        self.floor_size = floor_size
        self.sim_config = sim_config
        self.controller = controller
    
if __name__ == "__main__":
    
    from bncontroller.sim.data import r_point3d, Axis, Quadrant, Point3D
    import matplotlib.pyplot as plotter
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plotter.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')
    xs = []
    ys = []
    zs = []

    for _ in range(1000):
        p = r_point3d(O=Point3D(-0.0, 0.0, 0.0), R=[3.0, 3.0], axis=Axis.Y, quadrant=Quadrant.ANY)
        # print(p.to_tuple())
        xs.append(p.x)
        ys.append(p.y)
        zs.append(p.z)

    ax.scatter(xs, zs, ys)

    plotter.show()