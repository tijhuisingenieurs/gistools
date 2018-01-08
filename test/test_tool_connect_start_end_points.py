import unittest
import os.path


from gistools.utils.collection import MemCollection
from gistools.tools.connect_start_end_points import (get_start_endpoints,
                                                     get_midpoints, get_points_on_line,
                                                     get_points_on_line_random,
                                                     get_points_on_perc,
                                                     get_points_on_line_amount)


test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def check_import_fiona():
    try:
        import fiona
        return True
    except ImportError, e:
        return False


class TestTools(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.skipIf(not check_import_fiona(), "could not import fiona")
    def test_get_start_endpoints_shapefile(self):
        import fiona
        collection = fiona.open(os.path.join(test_data_dir, 'rd_line.shp'))

        point_col = get_start_endpoints(collection, ['id', 'name'])

        self.assertEqual(len(point_col), 4)
        self.assertDictEqual(point_col[0]['properties'],
                             {'id': 1L, 'name': 'test name 1'})

    def test_get_start_endpoints_mem_collection(self):
        collection = MemCollection(geometry_type='Linestring')

        collection.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (4.0, 4.0)]},
             'properties': {'id': 1L, 'name': 'test name 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(2.0, 0.0), (0.0, 2.0)]},
             'properties': {'id': 2L, 'name': 'line crosses line 1'}}
        ])

        point_col = get_start_endpoints(collection, ['id', 'name'])

        self.assertEqual(len(point_col), 4)
        self.assertDictEqual(point_col[0]['properties'],
                             {'id': 1L, 'name': 'test name 1'})

    def test_get_midpoints_line(self):
        collection = MemCollection(geometry_type='Linestring')

        collection.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (4.0, 4.0)]},
             'properties': {'id': 1L, 'name': 'test name 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(2.0, 0.0), (0.0, 2.0)]},
             'properties': {'id': 2L, 'name': 'line crosses line 1'}}
        ])

        point_col = get_midpoints(collection, ['id', 'name'])

        self.assertEqual(len(point_col), 2)
        self.assertDictEqual(point_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': (2.0, 2.0)})
        self.assertDictEqual(point_col[0]['properties'],
                             {'id': 1L, 'name': 'test name 1'})

    def test_get_midpoints_multiline(self):
        collection = MemCollection(geometry_type='MultiLinestring')

        collection.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (3.0, 3.0)),
                                          ((4.0, 4.0), (5.0, 5.0))]},
             'properties': {'id': 1L, 'name': 'test name 1'}},
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((2.0, 0.0), (1.0, 1.0)),
                                          ((1.0, 1.0), (0.0, 2.0))]},
             'properties': {'id': 2L, 'name': 'line crosses line 1'}}
        ])

        point_col = get_midpoints(collection, ['id', 'name'])

        self.assertEqual(len(point_col), 2)
        self.assertDictEqual(point_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': (2.0, 2.0)})
        self.assertDictEqual(point_col[0]['properties'],
                             {'id': 1L, 'name': 'test name 1'})

    def test_get_points_on_line_false(self):
        collection = MemCollection(geometry_type='MultiLinestring')

        collection.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (0.0, 3.0)),
                                          ((0.0, 4.0), (0.0, 4.6))]},
             'properties': {'id': 1L, 'name': 'test name 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(1.0, 0.0), (1.0, 3.6)]},
             'properties': {'id': 2L, 'name': 'line 2'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(1.0, 0.0), (1.0, 0.6)]},
             'properties': {'id': 3L, 'name': 'line 3'}}
        ])

        point_col = get_points_on_line(collection, ['id', 'name'],
                                       fixed_distance=1.0, max_repr_length=1.5,
                                       all_lines=False)

        self.assertEqual(len(point_col), 8)
        self.assertDictEqual(point_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 0.5)})
        self.assertDictEqual(point_col[3]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 4.5)})
        self.assertDictEqual(point_col[7]['geometry'],
                             {'type': 'Point',
                              'coordinates': (1.0, 3.5)})

        self.assertDictEqual(point_col[0]['properties'],
                             {'id': 1L, 'name': 'test name 1'})
        self.assertDictEqual(point_col[7]['properties'],
                             {'id': 2L, 'name': 'line 2'})

    def test_get_points_on_line_true(self):
        collection = MemCollection(geometry_type='MultiLinestring')

        collection.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (0.0, 3.0)),
                                          ((0.0, 4.0), (0.0, 4.6))]},
             'properties': {'id': 1L, 'name': 'test name 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(1.0, 0.0), (1.0, 3.6)]},
             'properties': {'id': 2L, 'name': 'line 2'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(1.0, 0.0), (1.0, 0.6)]},
             'properties': {'id': 3L, 'name': 'line 3'}}
        ])

        point_col = get_points_on_line(collection, ['id', 'name'],
                                       fixed_distance=1.0, max_repr_length=1.5,
                                       all_lines=True)

        self.assertEqual(len(point_col), 9)
        self.assertDictEqual(point_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 0.5)})
        self.assertDictEqual(point_col[3]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 4.5)})
        self.assertDictEqual(point_col[7]['geometry'],
                             {'type': 'Point',
                              'coordinates': (1.0, 3.5)})

        self.assertDictEqual(point_col[0]['properties'],
                             {'id': 1L, 'name': 'test name 1'})
        self.assertDictEqual(point_col[7]['properties'],
                             {'id': 2L, 'name': 'line 2'})
        self.assertDictEqual(point_col[8]['properties'],
                             {'id': 3L, 'name': 'line 3'})
    
    def test_get_points_on_perc(self):
        collection = MemCollection(geometry_type='MultiLinestring')
        
        collection.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (0.0, 79.0)),
                                          ((0.0, 89.0), (0.0, 170.0))]},
             'properties': {'id': 1L, 'name': 'line 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (90.0, 0.0)]},
             'properties': {'id': 2L, 'name': 'line 2'}}
        ])

        point_col = get_points_on_perc(collection, ['id', 'name'],
                                       default_perc=25.0, 
                                       perc_field=None)
        
        self.assertEqual(len(point_col), 8)
        
        self.assertDictEqual(point_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 40.0)})  
        self.assertDictEqual(point_col[1]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 90.0)})
        self.assertDictEqual(point_col[2]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 130.0)})
        self.assertDictEqual(point_col[3]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 170.0)})
        self.assertDictEqual(point_col[4]['geometry'],
                             {'type': 'Point',
                              'coordinates': (22.5, 0.0)})
        self.assertDictEqual(point_col[5]['geometry'],
                             {'type': 'Point',
                              'coordinates': (45.0, 0.0)})
        self.assertDictEqual(point_col[6]['geometry'],
                             {'type': 'Point',
                              'coordinates': (67.5, 0.0)})
        self.assertDictEqual(point_col[7]['geometry'],
                             {'type': 'Point',
                              'coordinates': (90.0, 0.0)})

    def get_points_on_line_amount(self):
        collection = MemCollection(geometry_type='MultiLinestring')
        
        collection.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (0.0, 80.0)),
                                          ((0.0, 90.0), (0.0, 170.0))]},
             'properties': {'id': 1L, 'name': 'line 1'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (90.0, 0.0)]},
             'properties': {'id': 2L, 'name': 'line 2'}}
        ])

        point_col = get_points_on_line_amount(collection, ['id', 'name'],
                                              default_amount=4.0,
                                              amount_field=None)
        
        self.assertEqual(len(point_col), 8)
        
        self.assertDictEqual(point_col[0]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 40.0)})  
        self.assertDictEqual(point_col[1]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 80.0)})
        self.assertDictEqual(point_col[2]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 130.0)})
        self.assertDictEqual(point_col[3]['geometry'],
                             {'type': 'Point',
                              'coordinates': (0.0, 170.0)})
        self.assertDictEqual(point_col[4]['geometry'],
                             {'type': 'Point',
                              'coordinates': (22.5, 0.0)})
        self.assertDictEqual(point_col[5]['geometry'],
                             {'type': 'Point',
                              'coordinates': (45.0, 0.0)})
        self.assertDictEqual(point_col[6]['geometry'],
                             {'type': 'Point',
                              'coordinates': (67.5, 0.0)})
        self.assertDictEqual(point_col[7]['geometry'],
                             {'type': 'Point',
                              'coordinates': (90.0, 0.0)})
    
    def test_get_points_on_line_random(self):
        collection = MemCollection(geometry_type='MultiLinestring')

        collection.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (0.0, 10.0)),
                                          ((0.0, 20.0), (0.0, 30.0))]},
             'properties': {'id': 1L, 'name': 'line 1', 'offset': 2.0}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (20.0, 0.0)]},
             'properties': {'id': 2L, 'name': 'line 2', 'offset': 2.0}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (20.0, 20.0)]},
             'properties': {'id': 3L, 'name': 'line 3', 'offset': 2.5}}
            ])     
        
        point_col = get_points_on_line_random(collection, ['id', 'name'],
                                              default_offset=0.75,
                                              offset_field='offset')
                                 
        self.assertEqual(len(point_col), 3)

        self.assertGreaterEqual(point_col[0]['geometry']['coordinates'][1], 2.0)
        self.assertLessEqual(point_col[0]['geometry']['coordinates'][1], 28.0)
     
        self.assertGreaterEqual(point_col[1]['geometry']['coordinates'][0], 2.0)
        self.assertLessEqual(point_col[1]['geometry']['coordinates'][0], 18.0)
        
        self.assertGreaterEqual(point_col[2]['geometry']['coordinates'][0], 1.76)
        self.assertLessEqual(point_col[2]['geometry']['coordinates'][0], 18.24)
        self.assertGreaterEqual(point_col[2]['geometry']['coordinates'][1], 1.76)
        self.assertLessEqual(point_col[2]['geometry']['coordinates'][1], 18.24)