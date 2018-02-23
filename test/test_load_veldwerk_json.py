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

        json_file = os.path.join(os.path.dirname(__file__), 'data', 'projectdata_2.json')

        meetplan_col = MemCollection(geometry_type='MultiLineString')

        meetplan_col.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(69119.450, 406358.153), (69121.600, 406361.359)]},
             'properties': {
                 'DWPnr': 13031,
                 'DWPcode': "13031"}}
        ])

        point_col, profile_col, ttlr_col, fp_col, boor_col = fielddata_to_memcollections(json_file, meetplan_col,
                                                                                         profile_id_field='DWPcode')

        # 58 meetpunten in json file
        self.assertEqual(len(point_col), 58)

        # 6 point notes in json file
        self.assertEqual(len(fp_col), 6)

        # test in bron volledig correct gevuld profiel
        point = None
        for p in point_col.filter():
            if p['properties']['prof_ids'] == '13032' and p['properties']['datumtijd'] == '2018-01-29T10:21:13.291Z':
                point = p
                break

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (69463.24580575209, 406248.62133429525)})
        self.maxDiff = None
        self.assertDictEqual(dict(point['properties']),
                             {'prof_pk': 1,
                              'prof_ids': '13032',
                              'prof_hpeil': -0.59,
                              'prof_lpeil': -0.5729728287114986,
                              'prof_rpeil': -0.5949266523676746,
                              'prof_wpeil': -0.59,
                              'prof_opm': 'Oude beschoeiing op 22lZie foto bij 22l',
                              'volgnr': 0,
                              'project_id': 'TI17247_scheldestromen_DG1_SM',
                              'proj_name': 'TI17247_scheldestromen_DG1_SM',
                              'datumtijd': '2018-01-29T10:21:13.291Z',
                              'code': '1',
                              'sub_code': '99',
                              'tekencode': "",
                              'opm': 'opmerking',
                              'method': 'OK met GPS',
                              'stok_len': 2.007,
                              'l1_len': 0.13428,
                              'gps_rd_x': 69463.24580575209,
                              'gps_rd_y': 406248.62133429525,
                              'gps_rd_z': 3.13924133377236,
                              'gps_wgs_x': 51.63855382666667,
                              'gps_wgs_y': 4.151526587999999,
                              'gps_wgs_z': 47.221,
                              'gps_h_afw': 0.006,
                              'gps_z_afw': 0.013,
                              'afstand': -7.208174397856045,
                              'afst_bron': 'gps',
                              'afst_afw': 0.013,
                              'ok': None,
                              'ok_bron': '',
                              'ok_afw': None,
                              'ok_eenheid': '',
                              'bk': 0.9979613337723601,
                              'bk_bron': 'gps',
                              'bk_afw': 0.013,
                              'bk_eenheid': 'mNAP',
                              '_bk_nap': 0.9979613337723601,
                              '_bk_wp': -159,
                              '_ok_nap': 0.9979613337723601,
                              '_ok_wp': -159,
                              'fotos': '',
                              'epsg': 28992.0,
                              'gps_z_nap_pole': 0.9979613337723601,
                              'last_modified': ""
                              })

        # 58 punten in dataset, 3 profielen, en 4 22 punten
        self.assertEqual(len(ttlr_col), 5)
        point = None

        for p in ttlr_col.filter():
            if p['properties']['ids'] == '13032' and p['properties']['code'] == '22L':
                point = p
                break

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (69459.77787734043, 406254.94045216736)})

        self.assertDictEqual(dict(point['properties']),
                             {'wpeil_bron': 'manual',
                              'code': '22L',
                              'afstand': 0.00,
                              'y_coord': 406254.94045216736,
                              'z': 1.5683071712885015,
                              'datum': '29/01/2018',
                              'ids': '13032',
                              'x_coord': 69459.77787734043,
                              'prof_pk': 1,
                              'project_id': 'TI17247_scheldestromen_DG1_SM',
                              'proj_name': 'TI17247_scheldestromen_DG1_SM',
                              'wpeil': -0.59,
                              'breedte': 5.188813223718082,
                              'gps_breed': 5.188813223718082,
                              'h_breedte': None,
                              'm99_breed': 5.140231798885141
                              })

        point = None
        for p in ttlr_col.filter():
            if p['properties']['ids'] == '13032' and p['properties']['code'] == '22R':
                point = p
                break

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (69457.17081247512, 406259.4267641782)})

        self.assertDictEqual(dict(point['properties']),
                             {'wpeil_bron': 'manual',
                              'code': '22R',
                              'afstand': 5.188813223718082,
                              'y_coord': 406259.4267641782,
                              'z': 1.5463533476323255,
                              'datum': '29/01/2018',
                              'ids': '13032',
                              'x_coord': 69457.17081247512,
                              'prof_pk': 1,
                              'project_id': 'TI17247_scheldestromen_DG1_SM',
                              'proj_name': 'TI17247_scheldestromen_DG1_SM',
                              'wpeil': -0.59,
                              'breedte': 5.188813223718082,
                              'gps_breed': 5.188813223718082,
                              'h_breedte': None,
                              'm99_breed': 5.140231798885141
                              })

        # profile 13031 heeft geen coordinaten bij de 22-punten
        point = None
        for p in ttlr_col.filter():
            if p['properties']['ids'] == '13031' and p['properties']['code'] == '22L':
                point = p
                break

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (69119.45, 406358.153)})

        self.assertDictEqual(dict(point['properties']),
                             {'wpeil_bron': 'manual',
                              'code': '22L',
                              'afstand': 0.00,
                              'y_coord': 406358.153,
                              'z': '',
                              'datum': '29/01/2018',
                              'ids': '13031',
                              'x_coord': 69119.45,
                              'prof_pk': 0,
                              'project_id': 'TI17247_scheldestromen_DG1_SM',
                              'proj_name': 'TI17247_scheldestromen_DG1_SM',
                              'wpeil': -0.59,
                              'breedte': 3.8061359397894665,
                              'gps_breed': None,
                              'h_breedte': None,
                              'm99_breed':  3.8061359397894665
                              })

        # profile 269 heeft geen coordinaten bij de 22-punten en geen entry in meetplan        
        point = {'geometry': {'type': 'Point', 'coordinates': (0.0, 0.0)}, 'properties': {''}, 'id': 999}
        for p in ttlr_col.filter():
            if p['properties']['ids'] == '13033' and p['properties']['code'] == '22R':
                point = p
                break

        self.assertDictEqual(point['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 0.0)})

        # Test collection of fixed points
        for p in fp_col.filter():
            # point 0 is complete
            if p['properties']['ids'] == '0':
                self.assertDictEqual(dict(p['properties']),
                                     {'project_id': 'TI17247_scheldestromen_DG1_SM',
                                      'proj_name': 'TI17247_scheldestromen_DG1_SM',
                                      'type': "Vast punt",
                                      'opm': "43D188",
                                      'fotos': "1517214684398-1516367554016",
                                      'datumtijd': "2018-01-29T08:31:00.235Z",
                                      'ids': '0',
                                      'x_coord': 72085.4317309772,
                                      'y_coord': 405657.9916649309,
                                      'z_nap': 1.1245780588627179,
                                      'vp_pk': 1
                                      })

            # point 0 has two photos
            if p['properties']['ids'] == '0':
                self.assertEqual(p['properties']['fotos'], "1517214684398-1516367554016")
                self.assertEqual(p['properties']['type'], "Vast punt")

            # point 1 has been set manually on the map
            if p['properties']['ids'] == '1':
                self.assertEqual(p['properties']['fotos'], "1517220431127")
                self.assertEqual(p['properties']['z_nap'], -9999)
                self.assertEqual(p['properties']['type'], "Inventarisatie")

            # point 3 has no photos
            if p['properties']['ids'] == '3':
                self.assertEqual(p['properties']['fotos'], "")
                self.assertEqual(p['properties']['z_nap'], 1.1325787993745715)

            # point 4 has no coordinates
            if p['properties']['ids'] == '4':
                self.assertEqual(p['geometry']['coordinates'], [0,0])

        # Test collection of boorpunten
        for bp in boor_col.filter():
            # boring in profile 13031, heeft geen coordinaten
            if bp['properties']['prof_ids'] == '13031' and bp['properties']['boring_nr'] == "":
                self.assertDictEqual(dict(bp['properties']),
                                     {'project_id': 'TI17247_scheldestromen_DG1_SM',
                                      'proj_name': 'TI17247_scheldestromen_DG1_SM',
                                      'prof_pk': 0,
                                      'prof_wpeil': -0.59,
                                      'code': 'Controle boring',
                                      'afstand': 1.73,
                                      'afst_bron': 'manual',
                                      'afst_afw': None,
                                      'bk_afw': None,
                                      'ok_eenheid': None,
                                      'opm': '',
                                      '_bk_nap': None,
                                      'fotos': '1517225956486',
                                      'datumtijd': '2018-01-29T11:41:57.994Z',
                                      'gps_rd_x': None,
                                      'gps_rd_y': None,
                                      'gps_rd_z': None,
                                      'boring_nr': '',
                                      '_bk_wp': None,
                                      '_ok_nap': None,
                                      '_ok_wp': None,
                                      'gps_h_afw': None,
                                      'bk': None,
                                      'bk_bron': None,
                                      'bk_eenheid': None,
                                      'epsg': None,
                                      'gps_wgs_x': None,
                                      'gps_wgs_y': None,
                                      'gps_wgs_z': None,
                                      'gps_z_afw': None,
                                      'gps_z_nap_pole': None,
                                      'l1_len': None,
                                      'last_modified': '',
                                      'method': '',
                                      'ok': None,
                                      'ok_afw': None,
                                      'ok_bron': None,
                                      'prof_hpeil': -0.59,
                                      'prof_ids': '13031',
                                      'prof_lpeil': None,
                                      'prof_opm': '',
                                      'prof_rpeil': None,
                                      'stok_len': None,
                                      'sub_code': '',
                                      'tekencode': '',
                                      'volgnr': 21
                                      })

            # Boring in profile 13033 has coordinates
            if bp['properties']['prof_ids'] == '13033' and bp['properties']['boring_nr'] == "":
                self.assertEqual(bp['geometry']['coordinates'], (68786.93810015894, 406581.3507081304))


    def test_fielddata_to_memcollection2(self):
        """test fill MemCollection with json data from file without point notes"""

        json_file = os.path.join(os.path.dirname(__file__), 'data', 'projectdata_2_noPointNotes.json')

        point_col, profile_col, ttlr_col, fp_col, boor_col = fielddata_to_memcollections(json_file)

        self.assertEqual(bool(point_col), True)
        self.assertEqual(bool(fp_col), False)
