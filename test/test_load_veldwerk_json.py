import unittest
import os.path

from gistools.utils.collection import MemCollection
from gistools.tools.load_veldwerk_json import fielddata_to_memcollections

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestLoadVeldwerk(unittest.TestCase):
    def setUp(self):
        pass

    def test_fielddata_to_memcollection(self):
        """test fill MemCollection with json data from file"""

        json_file = os.path.join(os.path.dirname(__file__), 'data', 'projectdata.json')
        meetplan_col = MemCollection(geometry_type='MultiLineString')
        
        meetplan_col.writerecords([
        {'geometry': {'type': 'LineString',
                          'coordinates': [(114231.0, 472589.0), (114238.0, 472587.0)]},
         'properties': {
            'DWPnr': '267'}}
        ])
        

        point_col, profile_col, ttlr_col = fielddata_to_memcollections(json_file, meetplan_col,'DWPnr')

        # 217 meetpunten in json file, waarvan 99 met coordinaten
        self.assertEqual(len(point_col), 217)
                
        # test in bron volledig correct gevuld profiel
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
                             {'prof_pk': 5,
                              'prof_ids': '279',
                              'prof_hpeil': -1.75,
                              'prof_lpeil': -1.8,
                              'prof_rpeil': -1.76,
                              'prof_wpeil': -1.75,
                              'prof_opm': '1=Beschoeiing ',
                              'volgnr': 0,
                              'project_id': 'p1',
                              'proj_name': 'project_1',
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
                              'gps_z_afw': None,
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
                              '_bk_wp': -42,
                              '_ok_nap': -1.33,
                              '_ok_wp': -42,
                              })           

        # 217 punten in dataset, waarvan 24 punten met een 22 code, 
        # waarvan 2 punten via meetplan en 2 zonder coordinaten = 22 met coordinaten
        self.assertEqual(len(ttlr_col), 22)
        point = None

        for p in ttlr_col.filter():
            if p['properties']['ids'] == '279' and p['properties']['code'] == '22L':
                point = p
                break

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (114216.10686321165, 472040.14822950924)})

        self.assertDictEqual(dict(point['properties']),
                             {'wpeil_bron': 'manual',
                              'code': '22L',
                              'afstand': 0.00,
                              'y_coord': 472040.14822950924,
                              'z': -1.7967513668576456,
                              'datum': '14/06/2017',
                              'ids': '279',
                              'x_coord': 114216.10686321165,
                              'prof_pk': 5,
                              'project_id': 'p1',
                              'proj_name': 'project_1',
                              'wpeil': -1.75,
                              'breedte': 3.446765493694888,
                              'gps_breed': 3.446765493694888,
                              'h_breedte': None,
                              'm99_breed': 3.19                              
                              })

        point = None
        for p in ttlr_col.filter():
            if p['properties']['ids'] == '279' and p['properties']['code'] == '22R':
                point = p
                break

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (114219.05704747832, 472038.3659261789)})

        self.assertDictEqual(dict(point['properties']),
                             {'wpeil_bron': 'manual',
                              'code': '22R',
                              'afstand': 3.45,
                              'y_coord': 472038.3659261789,
                              'z': -1.7637636573671327,
                              'datum': '14/06/2017',
                              'ids': '279',
                              'x_coord': 114219.05704747832,
                              'prof_pk': 5,
                              'project_id': 'p1',
                              'proj_name': 'project_1',                              
                              'wpeil': -1.75,
                              'breedte': 3.446765493694888,
                              'gps_breed': 3.446765493694888,
                              'h_breedte': None,
                              'm99_breed': 3.19                              
                              })

        # profile 267 heeft geen coordinaten bij de 22-punten
        point = None
        for p in ttlr_col.filter():
            if p['properties']['ids'] == '267' and p['properties']['code'] == '22L':
                point = p
                break
            
        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (114231.0, 472589.0)})

        self.assertDictEqual(dict(point['properties']),
                             {'wpeil_bron': 'manual',
                              'code': '22L',
                              'afstand': 0.00,
                              'y_coord': 472589.0,
                              'z': '',
                              'datum': '20/06/2017',
                              'ids': '267',
                              'x_coord': 114231.0,
                              'prof_pk': 2,
                              'project_id': 'p1',
                              'proj_name': 'project_1',                              
                              'wpeil': -5.36,
                              'breedte': 7.70,
                              'gps_breed': None,
                              'h_breedte': None,
                              'm99_breed': 7.70                              
                              })
        
        # profile 269 heeft geen coordinaten bij de 22-punten en geen entry in meetplan        
        point ={'geometry': {'type': 'Point', 'coordinates': (0.0, 0.0)}, 'properties': {''}, 'id': 999}
        for p in ttlr_col.filter():
            if p['properties']['ids'] == '269' and p['properties']['code'] == '22L':
                point = p
                break
        
        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 0.0)})
        