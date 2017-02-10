import unittest
import os.path

import fiona

from utils.collection import MemCollection
from tools.connect_start_end_points import get_start_endpoints, get_midpoints


test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestTools(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_start_endpoints_shapefile(self):
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

    def test_get_midpoints_mem_collection(self):
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
