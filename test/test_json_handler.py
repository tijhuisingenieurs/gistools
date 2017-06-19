import unittest
import os.path

from gistools.utils.collection import MemCollection
from gistools.utils.json_handler import fielddata_to_memcollection, json_to_dict

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestWit(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_json_to_dict(self):
        """test fill dictionary with json data from file"""
         
        json_data_col = MemCollection(geometry_type='MultiPoint')
        json_file = os.path.join(os.path.dirname(__file__),'data', 'projectdata.json')
        
        json_dict = json_to_dict(json_file)
            
        self.assertEqual(len(json_dict),2)
        self.assertEqual(json_dict['p1']['name'], 'project_1')
        self.assertEqual(len(json_dict['p1']['predefined_profiles']), 3)
        self.assertEqual(len(json_dict['p1']['measured_profiles']), 10)
        
        self.assertEqual(json_dict['p2']['name'], 'project_2')
        self.assertEqual(len(json_dict['p2']['predefined_profiles']), 3)
        self.assertEqual(len(json_dict['p2']['measured_profiles']), 0)
          
    def test_fielddata_to_memcollection(self):
        """test fill MemCollection with json data from file"""
         
        json_data_col = MemCollection(geometry_type='MultiPoint')
        json_file = os.path.join(os.path.dirname(__file__),'data', 'projectdata.json')
        
        # dicts voor genereren WDB tabellen
        project_dict = {}
        profile_dict = {}
        
        json_data_col, project_dict, profile_dict = fielddata_to_memcollection(json_file)
        
        #187 punten in dataset, waarvan 106 handmatig - 81 met geometrie
        self.assertEqual(len(json_data_col),81)

        for i,j in enumerate (json_data_col):
            if j['properties']['profiel'] == '279' and j['properties']['datetime'] == '2017-06-14T12:40:59.321Z':
                profile_index = i
                break
                
        self.assertDictEqual(json_data_col[profile_index]['geometry'],
                             {'type': 'Point',
                              'coordinates': (114215.59920829066, 472040.7198625375)})
        self.assertDictEqual(json_data_col[profile_index]['properties'],
                             { 'pro_id': 3,
                                'profiel': '279',
                                'volgnr': 0,
                                'puntcode': '1',
                                'z': -1.3267445101445259,
                                'datetime': '2017-06-14T12:40:59.321Z',
                                'code': '1',
                                'method': 'OK met GPS',
                                'pole_length': '2',
                                'l_one_length': '0.13428',
                                'rd_coordinates': [
                                    114215.59920829066,
                                    472040.7198625375,
                                    -1.3267445101445259
                                ],
                                'wgs_coordinates': [
                                    52.2349214,
                                    4.790167,
                                    43.999000549316406
                                ],
                                'accuracy': 3.9000000953674316,
                                'altitude_accuracy': None,
                                'distance': '0.00',
                                'distance_source': 'gps',
                                'distance_accuracy': 3.9000000953674316,
                                'lower_level': '',
                                'lower_level_source': '',
                                'lower_level_accuracy': '',
                                'lower_level_unit': '',
                                'upper_level': '-1.33',
                                'upper_level_source': 'gps',
                                'upper_level_accuracy': None,
                                'upper_level_unit': 'mNAP'})
        self.assertEqual(project_dict[1],'p1')
        self.assertEqual(profile_dict[3]['profiel'],'279') 
        self.assertEqual(profile_dict[3]['project'],'p1')         