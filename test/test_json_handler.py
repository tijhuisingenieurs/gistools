import unittest
import os.path

from gistools.utils.collection import MemCollection
from gistools.utils.json_handler import json_to_dict

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestJsonHandler(unittest.TestCase):
    def setUp(self):
        pass

    def test_json_to_dict(self):
        """test fill dictionary with json data from file"""

        point_col = MemCollection(geometry_type='MultiPoint')
        json_file = os.path.join(os.path.dirname(__file__), 'data', 'projectdata.json')

        json_dict = json_to_dict(json_file)

        self.assertEqual(len(json_dict), 2)
        self.assertEqual(json_dict['p1']['name'], 'project_1')
        self.assertEqual(len(json_dict['p1']['predefined_profiles']), 3)
        self.assertEqual(len(json_dict['p1']['measured_profiles']), 12)

        self.assertEqual(json_dict['p2']['name'], 'project_2')
        self.assertEqual(len(json_dict['p2']['predefined_profiles']), 3)
        self.assertEqual(len(json_dict['p2']['measured_profiles']), 0)
