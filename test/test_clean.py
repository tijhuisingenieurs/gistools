import unittest

from gistools.utils.collection import MemCollection
from gistools.tools.clean import get_end_points


class TestEndPoints(unittest.TestCase):

    def setUp(self):

        self.col = MemCollection()

        self.lines = [{
            'geometry': {'type': 'LineString', 'coordinates': [(1, 5), (5, 5)]},
            'properties': {'lid': 1, 'name': 'line 1'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(0, 0), (5, 0)]},
            'properties': {'lid': 2,' name': 'line 2'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(0, 0), (0, 5)]},
            'properties': {'lid': 3, 'name': 'line 3'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(3, -1), (3, 5)]},
            'properties': {'lid': 4, 'name': 'line 4'}
        }]

        self.col = MemCollection()
        self.col.writerecords(self.lines)

        self.col_small_disjoined = MemCollection()
        self.col_small_disjoined.writerecords(self.lines[:2])

        self.col_small_joined = MemCollection()
        self.col_small_joined.writerecords(self.lines[1:3])

        # situatie schets
        #   | -+--
        #   |  |
        #   |  |
        #   |  |
        #   |--+--
        #      |

    def test_get_end_points_two_joined_lines(self):
        """"""

        end_points = get_end_points(self.col_small_joined,
                                    'lid',
                                    max_delta=0.0)

        self.assertEqual(len(end_points), 3)

    def test_get_end_points_two_disjoined_lines(self):
        """"""

        end_points = get_end_points(self.col_small_disjoined,
                                    'lid',
                                    max_delta=0.0)

        self.assertEqual(len(end_points), 4)

    def test_get_end_points(self):

        end_points = get_end_points(self.col, 'lid', max_delta=0.0)

        self.assertEqual(len(end_points), 7)

    def test_get_end_points_with_delta(self):

        memcol = MemCollection()
        memcol.writerecords([{
            'geometry': {'type': 'LineString', 'coordinates': [(0.5, 0), (5, 5)]},
            'properties': {'lid': 1, 'name': 'line 1'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(0, 0), (5, 0)]},
            'properties': {'lid': 2,' name': 'line 2'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(-0.5, -0.5), (0, 5)]},
            'properties': {'lid': 3, 'name': 'line 3'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(-1, -1.5), (-5, -5)]},
            'properties': {'lid': 4, 'name': 'line 4'}
        }])

        end_points = get_end_points(memcol, 'lid', max_delta=0.6)

        self.assertEqual(len(end_points), 6)
        # test location combined point
        combined_point = [f for f in end_points.filter(bbox=(0, (-1.0/6.0)-0.0001, 0, (-1.0/6.0)+0.0001))]
        self.assertEqual(len(combined_point), 1)
        self.assertEqual(combined_point[0]['properties']['line_ids'], '1,2,3')

    def test_get_end_points_multiline(self):
        memcol = MemCollection()
        memcol.writerecords([{
            'geometry': {'type': 'MultiLineString', 'coordinates': [[(0, 0), (3, 0)], [(4, 0), (5, 0)]]},
            'properties': {'lid': 2, ' name': 'line 2'}
        }, {
            'geometry': {'type': 'MultiLineString', 'coordinates': [[(0, 0), (0, 5)]]},
            'properties': {'lid': 3, 'name': 'line 3'}
        }])

        end_points = get_end_points(memcol, 'lid')
        self.assertEqual(len(end_points), 3)
