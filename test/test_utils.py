import unittest
import math
from pathlib import Path
from bncontroller.stubs.utils import ArenaParams
from bncontroller.stubs.utils import generate_webots_worldfile
from bncontroller.stubs.utils import generate_webots_props_file
from bncontroller.sim.data import r_point3d, Axis, Quadrant

class TestUtils(unittest.TestCase):

    def test_webots_world_file_generation(self):
        p = Path('./test/boolnetcontroller.wbt')

        text1 = ''
        with open(p, 'r') as temp:
            text1 = '\n'.join(temp.readlines())
        
        generate_webots_worldfile(
            p, p.parent / 'test.wbt',
            ArenaParams(
                floor_size=(30, 30),
                sim_config='path/to/controller/config.json',
                controller='banana'
            )
        )

        text2 = ''

        with open(p.parent / 'test.wbt', 'r') as temp:
            text2 = '\n'.join(temp.readlines())

        self.assertTrue(text2 != text1 and len(text2) != 0 and len(text2) != 0)
        self.assertTrue('path/to/controller/config.json' in text2)
        self.assertTrue(str((30, 30))[1:-1].replace(',', '') in text2)
        self.assertTrue('banana' in text2)

    def test_webots_props_file_generation(self):

        p = Path('./test/boolnetcontroller.wbt')
        p2 = p.parent / 'test.wbt'

        props1, props2 = generate_webots_props_file(p, p2)

        self.assertTrue(props1.read_text() == props2.read_text())
        self.assertFalse(generate_webots_props_file(Path('./foo1.wbt'), Path('./foo2.wbt')))

        pass

    def test_random_point3d_generation(self):
        
        R1, R2 = 1.0, 2.0

        for _ in range(100):
            p = r_point3d(R=R1, axis=Axis.Y)
            self.assertTrue(0.0 <= math.sqrt(p.x**2 + p.z**2 + p.y**2) <= R1)
        
        for _ in range(100):
            p = r_point3d(R=[R1, R2], axis=Axis.Y)
            self.assertTrue(R1 <= math.sqrt(p.x**2 + p.z**2 + p.y**2) <= R2)
        
        for _ in range(100):
            p = r_point3d(R=[R1, R2], axis=Axis.Y, quadrant=Quadrant.PPP)
            self.assertTrue(R1 <= math.sqrt(p.x**2 + p.z**2 + p.y**2) <= R2)
