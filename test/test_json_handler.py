import unittest
import os.path
import tempfile
import shutil

from gistools.utils.collection import MemCollection
from gistools.utils.json_handler import (fielddata_to_memcollections, json_to_dict)

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestWit(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_json_to_dict(self):
        """test fill dictionary with json data from file"""
         
        point_col = MemCollection(geometry_type='MultiPoint')
        json_file = os.path.join(os.path.dirname(__file__),'data', 'projectdata.json')
        
        json_dict = json_to_dict(json_file)
            
        self.assertEqual(len(json_dict),2)
        self.assertEqual(json_dict['p1']['name'], 'project_1')
        self.assertEqual(len(json_dict['p1']['predefined_profiles']), 3)
        self.assertEqual(len(json_dict['p1']['measured_profiles']), 10)
        
        self.assertEqual(json_dict['p2']['name'], 'project_2')
        self.assertEqual(len(json_dict['p2']['predefined_profiles']), 3)
        self.assertEqual(len(json_dict['p2']['measured_profiles']), 0)
          
    def test_fielddata_to_memcollections(self):
        """test fill MemCollection with json data from file"""
         
        point_col = MemCollection(geometry_type='MultiPoint')
        line_col = MemCollection(geometry_type='MultiLineString')
        ttlr_col = MemCollection(geometry_type='MultiPoint')
        
        json_file = os.path.join(os.path.dirname(__file__),'data', 'projectdata.json')
        
        # dicts voor genereren WDB tabellen
        project_dict = {}
        profile_dict = {}
        
        point_col, line_col, ttlr_col = fielddata_to_memcollections(json_file)
        
        #187 punten in dataset, waarvan 106 handmatig - 81 met geometrie
        self.assertEqual(len(point_col),81)

        for i,j in enumerate (point_col):
            if j['properties']['profiel'] == '279' and j['properties']['datetime'] == '2017-06-14T12:40:59.321Z':
                profile_index = i
                break
         
        print i
               
        pass     
        
