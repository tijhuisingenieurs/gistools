import unittest
import os.path

from gistools.utils.collection import MemCollection
from gistools.tools.create_veldwerk_output_shapes import create_fieldwork_output_shapes

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestCreateFieldworkOutputShapes(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_fieldwork_output_shapes(self):
        """test fill MemCollection with json data from file"""

        input_line_col = MemCollection(geometry_type='MultiLineString')
        input_point_col1 = MemCollection(geometry_type='MultiPoint')
        input_point_col2 = MemCollection(geometry_type='MultiPoint')
        input_boringen_col = MemCollection(geometry_type='MultiPoint')
        input_boringen_col2 = MemCollection(geometry_type='MultiPoint')

        input_point_col1.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': [(10.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '1',
                            'sub_code': '99',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '-3.0',
                            '_bk_wp': '-80',
                            '_ok_wp': '-80'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(11.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '1',
                            'sub_code': '1',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '-1.0',
                            '_bk_wp': '-20',
                            '_ok_wp': '-20'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(11.5, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '22L',
                            'sub_code': '',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '0',
                            '_bk_wp': '0',
                            '_ok_wp': '0'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(12.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '99',
                            'sub_code': '',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '1.0',
                            '_bk_wp': '10',
                            '_ok_wp': '30'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(13.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '99',
                            'sub_code': '',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '3.0',
                            '_bk_wp': '20',
                            '_ok_wp': '35'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(14.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '99',
                            'sub_code': '',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '5.0',
                            '_bk_wp': '15',
                            '_ok_wp': '25'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(14.5, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '22R',
                            'sub_code': '',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '6.0',
                            '_bk_wp': '0',
                            '_ok_wp': '0'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(15.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '2',
                            'sub_code': '2',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '7.0',
                            '_bk_wp': '-30',
                            '_ok_wp': '-30'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(16.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '2',
                            'sub_code': '99',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '9.0',
                            '_bk_wp': '-90',
                            '_ok_wp': '-90'}}
        ])

        input_point_col2.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': [(10.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '1',
                            'sub_code': '99',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '-3.0',
                            '_bk_wp': '',
                            '_ok_wp': '-80'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(11.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '1',
                            'sub_code': '1',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '-1.0',
                            '_bk_wp': '-20',
                            '_ok_wp': ''}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(11.5, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '22L',
                            'sub_code': '',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '0',
                            '_bk_wp': '',
                            '_bk_nap': '-5.36',
                            '_ok_wp': '0'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(12.0, 0.0)]},
             'properties': {'prof_ids': 'test123',
                            'code': '99',
                            'sub_code': '',
                            'tekencode': '999',
                            'fotos': "",
                            'afstand': '1.0',
                            '_bk_wp': '',
                            '_ok_wp': ''}}
        ])

        input_line_col.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(12.0, 0.0), (14.0, 0.0)]},
             'properties': {'pk': '1',
                            'ids': 'test123',
                            'project_id': 'p1',
                            'proj_name': 'project_1',
                            'opm': 'Handmatig ingevoerd door begroeiing. 1 en 2 is beschoeiing ',
                            'wpeil': '-5.36',
                            'datum': '20/06/2017',
                            'breedte': '6.0'}}
        ])

        input_boringen_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': [(13.0, 0.0)]},
             'properties': {'project_id': 'p1',
                            'proj_name': 'project_1',
                            'prof_ids': 'test123',
                            'boring_nr': '1',
                            'afstand': '3.0',
                            'fotos': 'Fotoname',
                            'opm': 'opmerking',
                            'datumtijd': '018-01-29T11:41:57.994Z'
                            }
             }
        ])

        # test complete dataset with scaling of line length
        line_col, point_col, boor_col = create_fieldwork_output_shapes(input_line_col, input_point_col1,
                                                                       input_boringen_col)
        # test use result of complete dataset as input
        line_col1, point_col1, boor_col = create_fieldwork_output_shapes(line_col, point_col, input_boringen_col)
        # test incomplete dataset with scaling of line length
        line_col2, point_col2, boor_col2 = create_fieldwork_output_shapes(input_line_col, input_point_col2,
                                                                          input_boringen_col2)
        # test use result of incomplete dataset as input                    
        line_col3, point_col3, boor_col2 = create_fieldwork_output_shapes(line_col2, point_col2, input_boringen_col2)

        self.assertDictEqual(line_col[0]['geometry'],
                             {'type': 'LineString',
                              'coordinates': ((10.0, 0.0),(16.0, 0.0))})

        self.assertDictEqual(line_col[0]['properties'],
                             {'pk': '1',
                              'ids': 'test123',
                              'project_id': 'p1',
                              'proj_name': 'project_1',
                              'opm': 'Handmatig ingevoerd door begroeiing. 1 en 2 is beschoeiing ',
                              'wpeil': -5.36,
                              'datum': '20/06/2017',
                              'breedte': 6.0,
                              'xb_prof': 10.0,
                              'yb_prof': 0.0,
                              'xe_prof': 16.0,
                              'ye_prof': 0.0})

        self.assertEqual(len(point_col), 9)

        self.assertDictEqual(point_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': (7.0, 0.0)})
        self.assertDictEqual(point_col[1]['geometry'],
                             {'type': 'Point',
                              'coordinates': (9.0, 0.0)})
        self.assertDictEqual(point_col[2]['geometry'],
                             {'type': 'Point',
                              'coordinates': (10.0, 0.0)})
        self.assertDictEqual(point_col[3]['geometry'],
                             {'type': 'Point',
                              'coordinates': (11.0, 0.0)})
        self.assertDictEqual(point_col[4]['geometry'],
                             {'type': 'Point',
                              'coordinates': (13.0, 0.0)})
        self.assertDictEqual(point_col[5]['geometry'],
                             {'type': 'Point',
                              'coordinates': (15.0, 0.0)})
        self.assertDictEqual(point_col[6]['geometry'],
                             {'type': 'Point',
                              'coordinates': (16.0, 0.0)})
        self.assertDictEqual(point_col[7]['geometry'],
                             {'type': 'Point',
                              'coordinates': (17.0, 0.0)})
        self.assertDictEqual(point_col[8]['geometry'],
                             {'type': 'Point',
                              'coordinates': (19.0, 0.0)})

        self.assertDictEqual(point_col[0]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '1',
                              'tekencode': "999",
                              'afstand': -3.0,
                              '_bk_wp': -80.0,
                              '_bk_nap': -4.56,
                              'wpeil': -5.36,
                              '_ok_wp': -80.0,
                              '_ok_nap': -4.56,
                              'x_coord': 7.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': '99'})

        self.assertEqual(len(point_col1), 9)

        self.assertDictEqual(point_col1[0]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '1',
                              'tekencode': "999",
                              'afstand': -3.0,
                              '_bk_wp': -80.0,
                              '_bk_nap': -4.56,
                              '_ok_wp': -80.0,
                              '_ok_nap': -4.56,
                              'wpeil': -5.36,
                              'x_coord': 7.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': '99'})

        self.assertEqual(len(point_col2), 4)

        self.assertDictEqual(point_col2[0]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '1',
                              'tekencode': "999",
                              'afstand': -3.0,
                              '_bk_wp': '',
                              '_bk_nap': '',
                              '_ok_wp': -80.0,
                              '_ok_nap': -4.56,
                              'wpeil': -5.36,
                              'x_coord': 7.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': '99'})

        self.assertDictEqual(point_col2[1]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '1',
                              'tekencode': "999",
                              'afstand': -1.0,
                              '_bk_wp': -20.0,
                              '_bk_nap': -5.16,
                              '_ok_wp': -20.0,
                              '_ok_nap': -5.16,
                              'wpeil': -5.36,
                              'x_coord': 9.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': '1'})

        self.assertDictEqual(point_col2[2]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '22L',
                              'tekencode': "999",
                              'afstand': 0.0,
                              '_bk_wp': 0.0,
                              '_bk_nap': -5.36,
                              '_ok_wp': 0.0,
                              '_ok_nap': -5.36,
                              'wpeil': -5.36,
                              'x_coord': 10.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': ''})

        self.assertDictEqual(point_col2[3]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '99',
                              'tekencode': "999",
                              'afstand': 1.0,
                              '_bk_wp': '',
                              '_bk_nap': '',
                              '_ok_wp': '',
                              '_ok_nap': '',
                              'wpeil': -5.36,
                              'x_coord': 11.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': ''})

        self.assertEqual(len(point_col3), 4)

        self.assertDictEqual(point_col3[0]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '1',
                              'tekencode': "999",
                              'afstand': -3.0,
                              '_bk_wp': '',
                              '_bk_nap': '',
                              '_ok_wp': -80,
                              '_ok_nap': -4.56,
                              'wpeil': -5.36,
                              'x_coord': 7.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': '99'})

        self.assertDictEqual(point_col3[1]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '1',
                              'tekencode': "999",
                              'afstand': -1.0,
                              '_bk_wp': -20.0,
                              '_bk_nap': -5.16,
                              '_ok_wp': -20.0,
                              '_ok_nap': -5.16,
                              'wpeil': -5.36,
                              'x_coord': 9.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': '1'})

        self.assertDictEqual(point_col3[2]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '22L',
                              'tekencode': "999",
                              'afstand': 0.0,
                              '_bk_wp': 0.0,
                              '_bk_nap': -5.36,
                              '_ok_wp': 0.0,
                              '_ok_nap': -5.36,
                              'wpeil': -5.36,
                              'x_coord': 10.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': ''})

        self.assertDictEqual(point_col3[3]['properties'],
                             {'prof_ids': 'test123',
                              'datum': '20/06/2017',
                              'code': '99',
                              'tekencode': "999",
                              'afstand': 1.0,
                              '_bk_wp': '',
                              '_bk_nap': '',
                              '_ok_wp': '',
                              '_ok_nap': '',
                              'wpeil': -5.36,
                              'x_coord': 11.0,
                              'y_coord': 0.0,
                              'fotos': '',
                              'sub_code': ''})
        # Test boorpunt
        self.assertDictEqual(boor_col[0]['properties'],
                             {'prof_ids': 'test123',
                              'project_id': "p1",
                              'proj_name': "project_1",
                              'datumtijd': '018-01-29T11:41:57.994Z',
                              'afstand': 3.0,
                              'boring_nr': "1",
                              'x_coord': 13.0,
                              'y_coord': 0.0,
                              'fotos': 'Fotoname',
                              'opm': 'opmerking'})
