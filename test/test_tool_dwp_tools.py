import unittest
import os.path

from gistools.utils.collection import MemCollection
from  gistools.tools.dwp_tools import *

# import get_haakselijnen_on_points_on_line, flip_lines, 
# get_leggerprofiel, get_angles, get_global_intersect_angles, get_vertices_with_index,
# get_index_number_from_points


test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestDWPTools(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_haakselijnen_on_points_on_line(self):
        line_col = MemCollection(geometry_type='MultiLinestring')

        line_col.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (0.0, 3.0)),
                                          ((0.0, 4.0), (0.0, 4.6))]},
             'properties': {'id': 1, 'name': 'test name 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(1.0, 0.0), (1.0, 3.6)]},
             'properties': {'id': 2, 'name': 'line 2'}}
        ])

        point_col = MemCollection(geometry_type='MultiPoint')
        
        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 1.5)]},
             'properties': {'id': 1, 'name': 'test name 1_p1'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 2.9)]},
             'properties': {'id': 2, 'name': 'test name 1_p2'}},                                
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 4.3)]},
             'properties': {'id': 3, 'name': 'test name 1_p3'}},                                
            {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 1.2)]},
             'properties': {'id': 4, 'name': 'line 2_p1'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 2.4)]},
             'properties': {'id': 5, 'name': 'line 2_p2'}}                                
        ])

        haakselijn_col = get_haakselijnen_on_points_on_line(line_col, point_col, ['id', 'name'])

        self.assertEqual(len(haakselijn_col), 5)
        self.assertDictEqual(haakselijn_col[0]['geometry'],
                             {'type': 'LineString',
                              'coordinates': ((-7.5, 1.5), (0.0, 1.5), (7.5, 1.5))})
        self.assertDictEqual(haakselijn_col[1]['geometry'],
                             {'type': 'LineString',
                              'coordinates': ((-7.5, 2.9), (0.0, 2.9), (7.5, 2.9))})
        self.assertDictEqual(haakselijn_col[3]['geometry'],
                             {'type': 'LineString',
                              'coordinates': ((-6.5, 1.2), (1.0, 1.2), (8.5, 1.2))})
        self.assertDictEqual(haakselijn_col[4]['geometry'],
                             {'type': 'LineString',
                              'coordinates': ((-6.5, 2.4), (1.0, 2.4), (8.5, 2.4))})                                              

        self.assertDictEqual(haakselijn_col[0]['properties'],
                             {'id': 1, 'name': 'test name 1_p1'})
        self.assertDictEqual(haakselijn_col[3]['properties'],
                             {'id': 4, 'name': 'line 2_p1'})
        
    def test_get_flipped_line(self):
        """test flip line"""
        
        line_col = MemCollection(geometry_type='MultiLinestring')

        line_col.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (1.0, 1.0)),
                                          ((2.0, 2.0), (2.0, 4.0), (4.0, 4.0))]},
             'properties': {'id': 1, 'name': 'test name 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(1.0, 0.0), (1.0, 3.6)]},
             'properties': {'id': 2, 'name': 'line 2'}}
        ])

        flipped_line_col = flip_lines(line_col)
        
        self.assertEqual(len(flipped_line_col), 2)
        self.assertDictEqual(flipped_line_col[0]['geometry'],
                             {'type': 'MultiLineString',
                              'coordinates': [((4.0, 4.0), (2.0, 4.0), (2.0, 2.0)), 
                                              ((1.0, 1.0), (0.0, 0.0))]})
        self.assertDictEqual(flipped_line_col[1]['geometry'],
                             {'type': 'LineString',
                              'coordinates': ((1.0, 3.6), (1.0, 0.0))})

    def test_get_leggerprofiel(self):
        """test generate theoretical profile points"""
        
        self.maxDiff = None
        line_col = MemCollection(geometry_type='MultiLinestring')

        line_col.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (0.0, 10.0)),
                                          ((0.0, 12.0), (12.0, 12.0))]},
             'properties': {'line_id': 1,
                            'name': 'test name 1',
                            'peiljaar': '2010',
                            'waterpeil': -1.0,
                            'waterdiepte': 2.0,
                            'breedte_wa': 9.0,
                            'bodemhoogte': None,
                            'bodembreedte': None,
                            'talud_l': 1.0,
                            'talud_r': 1.0}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(10.0, 0.0), (10.0, 3.6)]},
             'properties': {'line_id': 2, 
                            'name': 'line 2',
                            'peiljaar': '2010',
                            'waterpeil': -1.0,
                            'waterdiepte': None,
                            'breedte_wa': None,
                            'bodemhoogte': -2.0,
                            'bodembreedte': 14.0,
                            'talud_l': 3.0,
                            'talud_r': 3.0}}
        ])
        
        legger_point_col = get_leggerprofiel(line_col)
        
        self.assertEqual(len(legger_point_col), 8)
        
        self.assertDictEqual(legger_point_col[0]['properties'],
                             {'line_id': 1, 'name': 'test name 1',
                              'L22': (1.0, 16.5), 'L22_peil': -1.0,
                              'knik_l': (1.0, 14.5), 'knik_l_dpt': -3.0,
                              'knik_r': (1.0, 9.5), 'knik_r_dpt': -3.0,
                              'R22': (1.0, 7.5), 'R22_peil': -1.0,
                              'ti_talulbr': 2.0,
                              'ti_knkbodr': 7.0,
                              'ti_waterbr': 9.0,
                              'peiljaar': '2010',
                              'puntcode': 22,
                              'volgnr': 1,
                              'afstand': 0.0,
                              'z_waarde': -1.0 })
        
        self.assertDictEqual(legger_point_col[2]['properties'],
                     {'line_id': 1, 'name': 'test name 1',
                      'L22': (1.0, 16.5), 'L22_peil': -1.0,
                      'knik_l': (1.0, 14.5), 'knik_l_dpt': -3.0,
                      'knik_r': (1.0, 9.5), 'knik_r_dpt': -3.0,
                      'R22': (1.0, 7.5), 'R22_peil': -1.0,
                      'ti_talulbr': 2.0,
                      'ti_knkbodr': 7.0,
                      'ti_waterbr': 9.0,
                      'peiljaar': '2010',
                      'puntcode': 99,
                      'volgnr': 3,
                      'afstand': 7.0,
                      'z_waarde': -3.0 })
        
        self.assertDictEqual(legger_point_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': [(1.0, 16.5)]})
        self.assertDictEqual(legger_point_col[1]['geometry'],
                             {'type': 'Point',
                              'coordinates': [(1.0, 14.5)]})
        self.assertDictEqual(legger_point_col[2]['geometry'],
                             {'type': 'Point',
                              'coordinates': [(1.0, 9.5)]})
        self.assertDictEqual(legger_point_col[3]['geometry'],
                             {'type': 'Point',
                              'coordinates': [(1.0, 7.5)]})
        
        self.assertDictEqual(legger_point_col[4]['properties'],
                             {'line_id': 2, 'name': 'line 2',
                              'L22': (0.0, 1.8), 'L22_peil': -1.0,
                              'knik_l': (3.0, 1.8), 'knik_l_dpt': -2.0,
                              'knik_r': ((17.0, 1.8)), 'knik_r_dpt': -2.0,
                              'R22': ((20.0, 1.8)), 'R22_peil': -1.0,
                              'ti_talulbr': 3.0,
                              'ti_knkbodr': 17.0,
                              'ti_waterbr': 20.0,
                              'peiljaar': '2010',
                              'puntcode': 22,
                              'volgnr': 1,
                              'afstand': 0.0,
                              'z_waarde': -1.0 })
        
        self.assertDictEqual(legger_point_col[6]['properties'],
                             {'line_id': 2, 'name': 'line 2',
                              'L22': (0.0, 1.8), 'L22_peil': -1.0,
                              'knik_l': (3.0, 1.8), 'knik_l_dpt': -2.0,
                              'knik_r': ((17.0, 1.8)), 'knik_r_dpt': -2.0,
                              'R22': ((20.0, 1.8)), 'R22_peil': -1.0,
                              'ti_talulbr': 3.0,
                              'ti_knkbodr': 17.0,
                              'ti_waterbr': 20.0,
                              'peiljaar': '2010',
                              'puntcode': 99,
                              'volgnr': 3,
                              'afstand': 17.0,
                              'z_waarde': -2.0 })
        
        self.assertDictEqual(legger_point_col[4]['geometry'],
                             {'type': 'Point',
                              'coordinates': [(0.0, 1.8)]})
        self.assertDictEqual(legger_point_col[5]['geometry'],
                             {'type': 'Point',
                              'coordinates': [(3.0, 1.8)]})
        self.assertDictEqual(legger_point_col[6]['geometry'],
                             {'type': 'Point',
                              'coordinates': [(17.0, 1.8)]})
        self.assertDictEqual(legger_point_col[7]['geometry'],
                             {'type': 'Point',
                              'coordinates': [(20.0, 1.8)]})

    def test_get_line_angles(self):
        """test calculate angles of lines"""   
             
        collection = MemCollection(geometry_type='MultiLinestring')

        collection.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (1.0, 1.0)),
                                              ((2.0, 2.0), (3.0, 3.0))]},
             'properties': {'id': 1L, 'name': 'line 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (103.553, 250.0)]},
             'properties': {'id': 2L, 'name': 'line 2'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (250.0, 103.553)]},
             'properties': {'id': 3L, 'name': 'line 3'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (250.0, 0.0)]},
             'properties': {'id': 4L, 'name': 'line 4'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (250.0, -250.0)]},
             'properties': {'id': 5L, 'name': 'line 5'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (-250.0, -250.0)]},
             'properties': {'id': 6L, 'name': 'line 6'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (-250.0, 250.0)]},
             'properties': {'id': 7L, 'name': 'line 7'}}
        ])
        
        angle_col = get_angles(collection)
        
        self.assertDictEqual(angle_col[0]['properties'],
                             {'id': 1L, 'name': 'line 1',
                                             'feature_angle': 45.0 })
        self.assertDictEqual(angle_col[1]['properties'],
                             {'id': 2L, 'name': 'line 2',
                                             'feature_angle': 22.5})
        self.assertDictEqual(angle_col[2]['properties'],
                             {'id': 3L, 'name': 'line 3',
                                             'feature_angle': 67.5 })
        self.assertDictEqual(angle_col[3]['properties'],
                             {'id': 4L, 'name': 'line 4',
                                             'feature_angle': 90.0})
        self.assertDictEqual(angle_col[4]['properties'],
                             {'id': 5L, 'name': 'line 5',
                                             'feature_angle': 135.0 })
        self.assertDictEqual(angle_col[5]['properties'],
                             {'id': 6L, 'name': 'line 6',
                                             'feature_angle': 225.0})
        self.assertDictEqual(angle_col[6]['properties'],
                             {'id': 7L, 'name': 'line 7',
                                             'feature_angle': 315.0})
    
    def test_get_global_intersect_angles(self):
        """test calculate angles of intersection of lines"""   
              
        collection1 = MemCollection(geometry_type='MultiLinestring')
        collection2 = MemCollection(geometry_type='MultiLinestring')
 
        collection1.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (1.0, 1.0)),
                                              ((2.0, 2.0), (3.0, 3.0))]},
             'properties': {'id': 1L, 'name': 'line 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (103.553, 250.0)]},
             'properties': {'id': 2L, 'name': 'line 2'}}
        ])
         
        collection2.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.5, 0.0), (0.5, 100.0)]},
             'properties': {'id': 1L, 'name': 'line 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.5), (500.0, 0.5)]},
             'properties': {'id': 2L, 'name': 'line 2'}}
        ])
         
        angle_col = get_global_intersect_angles(collection1, collection2)
         
        self.assertDictEqual(angle_col[0]['properties'],
                             {'crossangle': 45.0 })
        self.assertDictEqual(angle_col[1]['properties'],
                             {'crossangle': 45.0 })
        self.assertDictEqual(angle_col[2]['properties'],
                             {'crossangle': 22.5 })
        self.assertDictEqual(angle_col[3]['properties'],
                             {'crossangle': 67.5 })

    def test_get_vertices_with_index(self):
        """test get vertex index number """

        collection = MemCollection(geometry_type='MultiLinestring')

        collection.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (1.0, 1.0)),
                                              ((2.0, 2.0), (5.0, 5.0))]},
             'properties': {'id': 1L, 'name': 'line 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (0.0, 10.0), (0.0, 20.0)]},
             'properties': {'id': 2L, 'name': 'line 2'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 20.0), (30.0, 30.0)]},
             'properties': {'id': 3L, 'name': 'line 3'}}
        ])
                                 
        vertex_col = get_vertices_with_index(collection, 'id')
        
        p = vertex_col[0]
        
        self.assertEqual(p['geometry']['coordinates'][0], 0.0)
        
        self.assertDictEqual(vertex_col[0]['properties'],
                             {'line_id': 1L, 'vertex_nr': 1})
        self.assertDictEqual(vertex_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 0.0)})  
        
        self.assertDictEqual(vertex_col[1]['properties'],
                             {'line_id': 1L, 'vertex_nr': 2})
        self.assertDictEqual(vertex_col[1]['geometry'],
                             {'type': 'Point',
                              'coordinates': (1.0, 1.0)}) 
                                 
        self.assertDictEqual(vertex_col[2]['properties'],
                             {'line_id': 1L, 'vertex_nr': 3})
        self.assertDictEqual(vertex_col[2]['geometry'],
                             {'type': 'Point',
                              'coordinates': (2.0, 2.0)})                                

        self.assertDictEqual(vertex_col[3]['properties'],
                             {'line_id': 1L, 'vertex_nr': 4})
        self.assertDictEqual(vertex_col[3]['geometry'],
                             {'type': 'Point',
                              'coordinates': (5.0, 5.0)})      
        
        self.assertDictEqual(vertex_col[4]['properties'],
                             {'line_id': 2L, 'vertex_nr': 1})
        self.assertDictEqual(vertex_col[4]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 0.0)})                                        
       
        self.assertDictEqual(vertex_col[5]['properties'],
                             {'line_id': 2L, 'vertex_nr': 2})
        self.assertDictEqual(vertex_col[5]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 10.0)}) 
                                 
        self.assertDictEqual(vertex_col[7]['properties'],
                             {'line_id': 3L, 'vertex_nr': 1})
        self.assertDictEqual(vertex_col[7]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 0.0)})         

        self.assertDictEqual(vertex_col[8]['properties'],
                             {'line_id': 3L, 'vertex_nr': 2})
        self.assertDictEqual(vertex_col[8]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 10.0)})  
                        
        self.assertDictEqual(vertex_col[9]['properties'],
                             {'line_id': 3L, 'vertex_nr': 3})
        self.assertDictEqual(vertex_col[9]['geometry'],
                             {'type': 'Point',
                              'coordinates': (10.0, 10.0)})   

        self.assertDictEqual(vertex_col[10]['properties'],
                             {'line_id': 3L, 'vertex_nr': 4})
        self.assertDictEqual(vertex_col[10]['geometry'],
                             {'type': 'Point',
                              'coordinates': (10.0, 20.0)})       
        
        
    def test_get_index_number_from_points(self):
        """test append vertex index number to lines """

        line_col = MemCollection(geometry_type='MultiLinestring')

        line_col.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (1.0, 1.0)),
                                              ((2.0, 2.0), (5.0, 5.0))]},
             'properties': {'id': 1L, 'name': 'line 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (0.0, 10.0), (0.0, 20.0)]},
             'properties': {'id': 2L, 'name': 'line 2'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (0.0, 10.0), (10.0, 20.0), (30.0, 30.0)]},
             'properties': {'id': 3L, 'name': 'line 3'}}
        ])    
        
        point_col = MemCollection(geometry_type='MultiPoint')
                
        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': (0.5, 0.5)},
             'properties': {'line_id': 1L, 'vertex_nr': 1}},                               
            {'geometry': {'type': 'Point',
                          'coordinates': (0.0, 15.0)},
             'properties': {'line_id': 1L, 'vertex_nr': 2}},
            {'geometry': {'type': 'Point',
                          'coordinates': (5.0, 15.0)},
             'properties': {'line_id': 1L, 'vertex_nr': 3}}                                
        ])
        
        
        index_line_col = get_index_number_from_points(line_col, point_col, 'vertex_nr')     
        
        self.assertDictEqual(index_line_col[0]['properties'],
                             {'line_id': 1L, 'volgnr': 1 })
        self.assertDictEqual(index_line_col[1]['properties'],
                             {'line_id': 1L, 'volgnr': 2 })
        self.assertDictEqual(index_line_col[2]['properties'],
                             {'line_id': 1L, 'volgnr': 3 })
        