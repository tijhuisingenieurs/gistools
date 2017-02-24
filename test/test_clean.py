import unittest

from gistools.utils.collection import MemCollection
from gistools.tools.clean import get_end_points, connect_lines
from gistools.utils.geometry import tshape


class TestEndPoints(unittest.TestCase):

    def setUp(self):

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

class TestConnectLines(unittest.TestCase):

    def setUp(self):

        self.lines = [{
            'geometry': {'type': 'LineString', 'coordinates': [(-10, 0), (10, 0)]},
            'properties': {'lid': 1, 'name': 'refline'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(1, 0), (1, 5)]},
            'properties': {'lid': 2, ' name': 'touches'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(4, -1), (4, 4)]},
            'properties': {'lid': 3, 'name': 'crosses'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(2, 9), (5, 9)]},
            'properties': {'lid': 4, 'name': 'extend touches'}
        }]

        self.col = MemCollection()
        self.col.writerecords(self.lines)

    def test_function(self):

        one = tshape(self.lines[0]['geometry'])
        touch_line = tshape(self.lines[1]['geometry'])
        cross_line = tshape(self.lines[2]['geometry'])
        extend_line = tshape(self.lines[3]['geometry'])

        self.assertTrue(one.touches(touch_line))
        self.assertFalse(cross_line.touches(touch_line))
        self.assertFalse(one.touches(cross_line))

        self.assertTrue(one.crosses(cross_line))
        self.assertFalse(cross_line.crosses(touch_line))
        self.assertFalse(one.crosses(touch_line))

    def test_add_vertex_at_connection(self):

        col = MemCollection()
        col.writerecords(self.lines[:2])

        lines = connect_lines(col,
                            line_id_field='lid')

        self.assertEqual(len(lines), 2)
        self.assertEqual(len(lines[0]['geometry']['coordinates']), 3)
        self.assertListEqual(lines[1]['properties']['linked_start'], [0])

    def test_split_at_connection(self):

        col = MemCollection()
        col.writerecords(self.lines[:2])

        lines = connect_lines(col,
                              line_id_field='lid',
                              split_line_at_connection=True)


        parts = [f['properties']['part'] for f in lines]
        self.assertEqual(len(lines), 3)
        self.assertListEqual(parts, [0, 1, None])
