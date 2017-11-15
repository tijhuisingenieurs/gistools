import unittest

from gistools.utils.collection import MemCollection
from gistools.tools.snap_points_to_line import snap_points_to_line


class TestSnapPointToLine(unittest.TestCase):

    def setUp(self):
        self.lines = MemCollection()

        self.lines.writerecords([{
            'geometry': {'type': 'LineString', 'coordinates': [(0, 0), (0, 10)]},
            'properties': {'lid': 1, 'name': 'line 3', 'nr': 2, 'direction': 1}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(0, 10), (10, 0)]},
            'properties': {'lid': 2, 'name': 'line 4', 'nr': 1, 'direction': -1}
        }])

        self.points = MemCollection()

        self.points.writerecords([{
            'geometry': {'type': 'Point', 'coordinates': (0, 1)},
            'properties': {'pid': 1}
        }, {
            'geometry': {'type': 'Point', 'coordinates': (-1, 2)},
            'properties': {'pid': 2}
        }, {
            'geometry': {'type': 'Point', 'coordinates': (-2, 3)},
            'properties': {'pid': 3}
        }, {
            'geometry': {'type': 'Point', 'coordinates': (6, 0)},
            'properties': {'pid': 4}
        }, {
            'geometry': {'type': 'Point', 'coordinates': (0.5, 9)},
            'properties': {'pid': 5}
        }])

    def test_snapa(self):
        tolerance = 1
        keep_unsnapped_points = False

        snapped_points = snap_points_to_line(self.lines, self.points, tolerance, keep_unsnapped_points)
        point_dict = {point['properties']['pid']: point for point in snapped_points}

        self.assertTupleEqual(point_dict[1]['geometry']['coordinates'], (0, 1))
        self.assertTupleEqual(point_dict[2]['geometry']['coordinates'], (0, 2))
        self.assertTupleEqual(point_dict[5]['geometry']['coordinates'], (0.75, 9.25))

        self.assertEqual(len(point_dict.items()), 3)

    def test_snapb(self):
        tolerance = 1
        keep_unsnapped_points = True

        snapped_points = snap_points_to_line(self.lines, self.points, tolerance, keep_unsnapped_points)
        point_dict = {point['properties']['pid']: point for point in snapped_points}

        self.assertTupleEqual(point_dict[1]['geometry']['coordinates'], (0, 1))
        self.assertTupleEqual(point_dict[2]['geometry']['coordinates'], (0, 2))
        self.assertTupleEqual(point_dict[3]['geometry']['coordinates'], (-2, 3))
        self.assertTupleEqual(point_dict[4]['geometry']['coordinates'], (6, 0))
        self.assertTupleEqual(point_dict[5]['geometry']['coordinates'], (0.75, 9.25))

        self.assertEqual(len(point_dict.items()), 5)

    def test_snapc(self):
        tolerance = 4
        keep_unsnapped_points = False

        snapped_points = snap_points_to_line(self.lines, self.points, tolerance, keep_unsnapped_points)
        point_dict = {point['properties']['pid']: point for point in snapped_points}

        self.assertTupleEqual(point_dict[1]['geometry']['coordinates'], (0, 1))
        self.assertTupleEqual(point_dict[2]['geometry']['coordinates'], (0, 2))
        self.assertTupleEqual(point_dict[3]['geometry']['coordinates'], (0, 3))
        self.assertTupleEqual(point_dict[4]['geometry']['coordinates'], (8, 2))
        self.assertTupleEqual(point_dict[5]['geometry']['coordinates'], (0.75, 9.25))

        self.assertEqual(len(point_dict.items()), 5)

    def test_snapd(self):
        tolerance = 2
        keep_unsnapped_points = False

        snapped_points = snap_points_to_line(self.lines, self.points, tolerance, keep_unsnapped_points)
        point_dict = {point['properties']['pid']: point for point in snapped_points}

        self.assertTupleEqual(point_dict[1]['geometry']['coordinates'], (0, 1))
        self.assertTupleEqual(point_dict[2]['geometry']['coordinates'], (0, 2))
        self.assertTupleEqual(point_dict[3]['geometry']['coordinates'], (0, 3))
        self.assertTupleEqual(point_dict[5]['geometry']['coordinates'], (0.75, 9.25))

        self.assertEqual(len(point_dict.items()), 4)
