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

        input_point_col1.writerecords([
        {'geometry': {'type': 'Point',
                          'coordinates': [(10.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '1',
                'afstand': '-3.0',
                'bk_wp': '-80',
                'ok_wp': '-80'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(11.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '1',
                'afstand': '-1.0',
                'bk_wp': '-20',
                'ok_wp': '-20'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(11.5, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '22L',
                'afstand': '0',
                'bk_wp': '0',
                'ok_wp': '0'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(12.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '99',
                'afstand': '1.0',
                'bk_wp': '10',
                'ok_wp': '30'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(13.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '99',
                'afstand': '3.0',
                'bk_wp': '20',
                'ok_wp': '35'}},                                                                          
        {'geometry': {'type': 'Point',
                          'coordinates': [(14.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '99',
                'afstand': '5.0',
                'bk_wp': '15',
                'ok_wp': '25'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(14.5, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '22R',
                'afstand': '6.0',
                'bk_wp': '0',
                'ok_wp': '0'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(15.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '2',
                'afstand': '7.0',
                'bk_wp': '-30',
                'ok_wp': '-30'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(16.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '2',
                'afstand': '9.0',
                'bk_wp': '-90',
                'ok_wp': '-90'}}   
        ])
        
        input_point_col2.writerecords([
        {'geometry': {'type': 'Point',
                          'coordinates': [(10.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '1',
                'afstand': '-3.0',
                'bk_wp': '',
                'ok_wp': '-80'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(11.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '1',
                'afstand': '-1.0',
                'bk_wp': '-20',
                'ok_wp': ''}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(11.5, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '22L',
                'afstand': '0',
                'bk_wp': '',
                'bk_nap': '-5.36',
                'ok_wp': '0'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(12.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '99',
                'afstand': '1.0',
                'bk_wp': '',
                'ok_wp': ''}}
        ])                            
        
        input_line_col.writerecords([
        {'geometry': {'type': 'LineString',
                          'coordinates': [(12.0, 0.0), (14.0, 0.0)]},
         'properties': {'pk': '1',
            'ids': 'test123',
            'project_id': 'p1',
            'opm': 'Handmatig ingevoerd door begroeiing. 1 en 2 is beschoeiing ',
            'wpeil': '-5.36',
            'datum': '20/06/2017',
            'breedte': '6.0'}}
        ])
        
        # test complete dataset with scaling of line length
        line_col, point_col = create_fieldwork_output_shapes(input_line_col, input_point_col1)
        # test use result of complete dataset as input
        line_col1, point_col1 = create_fieldwork_output_shapes(line_col, point_col)                
        # test incomplete dataset with scaling of line length
        line_col2, point_col2 = create_fieldwork_output_shapes(input_line_col, input_point_col2)
        # test use result of incomplete dataset as input                    
        line_col3, point_col3 = create_fieldwork_output_shapes(line_col2, point_col2)        
        
        self.assertDictEqual(line_col[0]['geometry'],
                             {'type': 'LineString',
                              'coordinates': ((10.0, 0.0),(16.0, 0.0))})
        
        self.assertDictEqual(line_col[0]['properties'],
                             {'pk': '1',
                                'ids': 'test123',
                                'project_id': 'p1',
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
                                'afstand': -3.0,
                                'bk_wp': -80.0,
                                'bk_nap': -4.56,
                                'ok_wp': -80.0,
                                'ok_nap': -4.56,
                                'x': 7.0,
                                'y': 0.0})

        self.assertEqual(len(point_col1), 9)
        
        self.assertDictEqual(point_col1[0]['properties'],
                             {'prof_ids': 'test123',
                                'datum': '20/06/2017',
                                'code': '1',
                                'afstand': -3.0,
                                'bk_wp': -80.0,
                                'bk_nap': -4.56,
                                'ok_wp': -80.0,
                                'ok_nap': -4.56,
                                'x': 7.0,
                                'y': 0.0})

        self.assertEqual(len(point_col2), 4)
        
        self.assertDictEqual(point_col2[0]['properties'],
                     {'prof_ids': 'test123',
                        'datum': '20/06/2017',
                        'code': '1',
                        'afstand': -3.0,
                        'bk_wp': '',
                        'bk_nap': 'NoData',
                        'ok_wp': -80,
                        'ok_nap': -4.56,
                        'x': 7.0,
                        'y': 0.0})
        self.assertDictEqual(point_col2[1]['properties'],
                     {'prof_ids': 'test123',
                        'datum': '20/06/2017',
                        'code': '1',
                        'afstand': -1.0,
                        'bk_wp': -20.0,
                        'bk_nap': -5.16,
                        'ok_wp': -20.0,
                        'ok_nap': -5.16,
                        'x': 9.0,
                        'y': 0.0})      
        self.assertDictEqual(point_col2[2]['properties'],
                     {'prof_ids': 'test123',
                        'datum': '20/06/2017',
                        'code': '22L',
                        'afstand': 0.0,
                        'bk_wp': 0.0,
                        'bk_nap': -5.36,
                        'ok_wp': 0.0,
                        'ok_nap': -5.36,
                        'x': 10.0,
                        'y': 0.0})       
        self.assertDictEqual(point_col2[3]['properties'],
                     {'prof_ids': 'test123',
                        'datum': '20/06/2017',
                        'code': '99',
                        'afstand': 1.0,
                        'bk_wp': '',
                        'bk_nap': 'NoData',
                        'ok_wp': '',
                        'ok_nap': 'NoData',
                        'x': 11.0,
                        'y': 0.0})
        

        
        self.assertEqual(len(point_col3), 4)
        
        self.assertDictEqual(point_col3[0]['properties'],
                     {'prof_ids': 'test123',
                        'datum': '20/06/2017',
                        'code': '1',
                        'afstand': -3.0,
                        'bk_wp': '',
                        'bk_nap': 'NoData',
                        'ok_wp': -80,
                        'ok_nap': -4.56,
                        'x': 7.0,
                        'y': 0.0})
        self.assertDictEqual(point_col3[1]['properties'],
                     {'prof_ids': 'test123',
                        'datum': '20/06/2017',
                        'code': '1',
                        'afstand': -1.0,
                        'bk_wp': -20.0,
                        'bk_nap': -5.16,
                        'ok_wp': -20.0,
                        'ok_nap': -5.16,
                        'x': 9.0,
                        'y': 0.0})      
        self.assertDictEqual(point_col3[2]['properties'],
                     {'prof_ids': 'test123',
                        'datum': '20/06/2017',
                        'code': '22L',
                        'afstand': 0.0,
                        'bk_wp': 0.0,
                        'bk_nap': -5.36,
                        'ok_wp': 0.0,
                        'ok_nap': -5.36,
                        'x': 10.0,
                        'y': 0.0})       
        self.assertDictEqual(point_col3[3]['properties'],
                     {'prof_ids': 'test123',
                        'datum': '20/06/2017',
                        'code': '99',
                        'afstand': 1.0,
                        'bk_wp': '',
                        'bk_nap': 'NoData',
                        'ok_wp': '',
                        'ok_nap': 'NoData',
                        'x': 11.0,
                        'y': 0.0})