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
        json_file = os.path.join(os.path.dirname(__file__), 'data', 'projectdata.json')

        json_dict = json_to_dict(json_file)

        self.assertEqual(len(json_dict), 2)
        self.assertEqual(json_dict['p1']['name'], 'project_1')
        self.assertEqual(len(json_dict['p1']['predefined_profiles']), 3)
        self.assertEqual(len(json_dict['p1']['measured_profiles']), 10)

        self.assertEqual(json_dict['p2']['name'], 'project_2')
        self.assertEqual(len(json_dict['p2']['predefined_profiles']), 3)
        self.assertEqual(len(json_dict['p2']['measured_profiles']), 0)


    def test_fielddata_to_memcollection(self):
        """test fill MemCollection with json data from file"""

        json_data_col = MemCollection(geometry_type='MultiPoint')
        json_file = os.path.join(os.path.dirname(__file__), 'data', 'projectdata.json')

        # dicts voor genereren WDB tabellen
        project_dict = {}
        profile_dict = {}

        point_col, profile_col, ttlr_col = fielddata_to_memcollections(json_file)

        # 187 punten in dataset, waarvan 106 handmatig - 81 met geometrie
        self.assertEqual(len(point_col), 187)
        point = None
        for p in point_col.filter():
            if p['properties']['prof_ids'] == '279' and p['properties']['datumtijd'] == '2017-06-14T12:40:59.321Z':
                point = p
                break

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (114215.59920829066, 472040.7198625375)})
        self.maxDiff = None
        self.assertDictEqual(dict(point['properties']),
                             {'prof_pk': 3,
                              'prof_ids': '279',
                              'prof_hpeil': None,
                              'prof_lpeil': -1.8,
                              'prof_rpeil': -1.76,
                              'prof_wpeil': -1.78,
                              'prof_opm': '1=Beschoeiing ',
                              'volgnr': 0,
                              'project_id': 'p1',
                              'datumtijd': '2017-06-14T12:40:59.321Z',
                              'code': '1',
                              'opm': '',
                              'method': 'OK met GPS',
                              'stok_len': 2.0,
                              'l1_len': 0.13428,
                              'gps_rd_x': 114215.59920829066,
                              'gps_rd_y': 472040.7198625375,
                              'gps_rd_z': -1.3267445101445259,
                              'gps_wgs_x': 52.2349214,
                              'gps_wgs_y': 4.790167,
                              'gps_wgs_z': 43.999000549316406,
                              'gps_h_afw': 3.9000000953674316,
                              'gps_h_afw': None,
                              'afstand': 0.0,
                              'afst_bron': 'gps',
                              'afst_afw': 3.9000000953674316,
                              'ok': None,
                              'ok_bron': '',
                              'ok_afw': None,
                              'ok_eenheid': '',
                              'bk': -1.33,
                              'bk_bron': 'gps',
                              'bk_afw': None,
                              'bk_eenheid': 'mNAP',
                              '_bk_nap': -1.33,
                              '_bk_tov_wp': 45,
                              '_ok_nap': None,
                              '_ok_tov_wp': None,
                              })
        
         # 187 punten in dataset, waarvan 20 punten met een 22 code
        self.assertEqual(len(ttlr_col), 20)
        point = None
        
        for p in ttlr_col.filter():
            if p['properties']['ids'] == '279' and p['properties']['code'] == '22L':
                point = p
                break
            
        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (114216.10686321165,472040.14822950924)})
        
        self.assertDictEqual(dict(point['properties']),
                             {'wpeil_bron': '22L en 22R', 
                              'code': '22L', 
                              'afstand': 0.00, 
                              'y_coord': 472040.14822950924, 
                              'z': -1.7967513668576456, 
                              'datum': '14/06/2017', 
                              'ids': '279', 
                              'x_coord': 114216.10686321165, 
                              'prof_pk': 3, 
                              'project_id': 'p1', 
                              'wpeil': -1.78})
        
        for p in ttlr_col.filter():
            if p['properties']['ids'] == '279' and p['properties']['code'] == '22R':
                point = p
                break                      

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (114219.05704747832,472038.3659261789)})
        
        self.assertDictEqual(dict(point['properties']),
                             {'wpeil_bron': '22L en 22R', 
                              'code': '22R', 
                              'afstand': 3.45, 
                              'y_coord': 472038.3659261789, 
                              'z': -1.7637636573671327, 
                              'datum': '14/06/2017', 
                              'ids': '279', 
                              'x_coord': 114219.05704747832, 
                              'prof_pk': 3, 
                              'project_id': 'p1', 
                              'wpeil': -1.78})