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
        json_file = os.path.join(os.path.dirname(__file__), 'data', 'projectdata_2.json')

        json_dict = json_to_dict(json_file)

        # json_dict is a dict with three or four elements:
        # - id = project_id
        # - name = project name
        # - measured_profiles = dict with profiles
        # - predifined_profiles = dict with planned locations (optional)

        self.assertEqual(len(json_dict), 4)
        self.assertEqual(json_dict['id'], 'TI17247_scheldestromen_DG1_SM')
        self.assertEqual(json_dict['name'], 'TI17247_scheldestromen_DG1_SM')
        self.assertEqual(len(json_dict['point_notes']), 6)
        self.assertEqual(len(json_dict['measured_profiles']), 3)

