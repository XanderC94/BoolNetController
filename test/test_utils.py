import unittest
from pathlib import Path
from bncontroller.stubs.utils import ArenaParams
from bncontroller.stubs.utils import generate_webots_worldfile
from bncontroller.stubs.utils import generate_webots_props_file

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
                controller_args='path/to/controller/config.json'
            )
        )

        text2 = ''

        with open(p.parent / 'test.wbt', 'r') as temp:
            text2 = '\n'.join(temp.readlines())

        self.assertTrue(text2 != text1 and len(text2) != 0 and len(text2) != 0)
        self.assertTrue('path/to/controller/config.json' in text2)
        self.assertTrue(str((30, 30))[1:-1].replace(',', '') in text2)

    def test_webots_props_file_generation(self):

        p = Path('./test/boolnetcontroller.wbt')
        p2 = p.parent / 'test.wbt'

        props1, props2 = generate_webots_props_file(p, p2)

        self.assertTrue(props1.read_text() == props2.read_text())
        self.assertFalse(generate_webots_props_file(Path('./foo1.wbt'), Path('./foo2.wbt')))

        pass



