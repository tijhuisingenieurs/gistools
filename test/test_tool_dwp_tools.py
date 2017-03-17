import unittest
import os.path

from gistools.utils.collection import MemCollection
from gistools.tools.dwp_tools import get_haakselijnen_on_points_on_line, flip_lines, get_leggerprofiel


test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# TODO: uitzoeken hoe OrderedDict goed af te dwingen in genereren van dict en in AssertDictEqual


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
        
        line_col = MemCollection(geometry_type='MultiLinestring')

        line_col.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (0.0, 10.0)),
                                          ((0.0, 12.0), (12.0, 12.0))]},
             'properties': {'id': 1,
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
             'properties': {'id': 2, 
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
