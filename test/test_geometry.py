import unittest
from shapely.geometry import Point
from utils.geometry import TLine, TMultiLineString
from math import sqrt
# from generatepointsfromlines import percentage


class TestTLine(unittest.TestCase):

    def setUp(self):
        pass

    def test_point_on_line(self):
        """test line on point"""
        point = Point(2, 1)
        line = TLine([(0, 0), (0, 1), (3, 1), (3, 3)])
        line_part = line.get_line_part_point(point)

        self.assertTupleEqual(line_part[0], (1, (0, 1), 1.0))
        self.assertTupleEqual(line_part[1], (2, (3, 1), 4.0))
        self.assertEqual(line_part[2], 3.0)

    def test_point_on_line_on_vertex(self):
        """test line on point exact on a vertex"""

        point = Point(3, 1)
        line = TLine([(0, 0), (0, 1), (3, 1), (3, 3)])
        line_part = line.get_line_part_point(point)

        self.assertTupleEqual(line_part[0], (1, (0, 1), 1.0))
        self.assertTupleEqual(line_part[1], (2, (3, 1), 4.0))
        self.assertEqual(line_part[2], 4.0)

    def test_haakselijn_op_horizontaal(self):
        """test haakselijn on point on horizontal line"""

        point = Point(2, 1)
        line = TLine([(0, 0), (0, 1), (3, 1), (3, 3)])
        haakselijn = line.get_haakselijn_point(point, 2.0)

        self.assertTupleEqual(haakselijn, ((2.0, 2.0), (2.0, 1.0), (2.0, 0.0)))

    def test_haakselijn_op_vertikaal(self):
        """test haakselijn on point on vertical line"""

        point = Point(3, 2)
        line = TLine([(0, 0), (0, 1), (3, 1), (3, 3)])
        haakselijn = line.get_haakselijn_point(point, 2.0)

        self.assertTupleEqual(haakselijn, ((2.0, 2.0), (3.0, 2.0), (4.0, 2.0)))

    def test_haakselijn_op_diagonaal(self):
        """test haakselijn on point on diagonal line"""

        point = Point(2, 2)
        line = TLine([(0, 0), (3, 3), (2, 5)])
        haakselijn = line.get_haakselijn_point(point, sqrt(8.0))

        self.assertTupleEqual(haakselijn, ((1.0, 3.0), (2.0, 2.0), (3.0, 1.0)))

    def test_segment_richting(self):
        """test segment direction on point on line"""

        point = Point(2, 2)
        line = TLine([(0, 0), (3, 3), (2, 5)])
        richting = line.get_segment_richting_point(point)

        self.assertTupleEqual(richting, (3.0, 3.0))

    def test_get_point_at_distance(self):
        """test create point on line at given distance"""
        
        line = TLine([(0, 0), (0, 2), (2, 2), (2, 4)])
        afstand = 5
        point = line.get_point_at_distance(afstand)
        segment = line.get_line_part_dist(afstand)
        
        self.assertTupleEqual(segment[0], (2, (2, 2), 4.0))
        self.assertTupleEqual(segment[1], (3, (2, 4), 6.0))
        self.assertEqual(segment[2], 5.0)
        
        self.assertEqual(list(point.coords), [(2.0, 3.0)])

    def test_get_point_at_percentage(self):
        """test create point on line at given % of total line length"""
        
        line = TLine([(0, 0), (0, 2), (2, 2), (2, 8)])
        perc = 0.5
        point = line.get_point_at_percentage(perc)
        segment = line.get_line_part_perc(perc)
        
        self.assertTupleEqual(segment[0], (2, (2, 2), 4.0))
        self.assertTupleEqual(segment[1], (3, (2, 8), 10.0))
        self.assertEqual(segment[2], 5.0)
        
        self.assertEqual(list(point.coords), [(2.0, 3.0)])
    

class TestTMultiLine(unittest.TestCase):

    def test_init_single_line(self):
        """ test creation of single LineString and function 'is_multipart' """
        multi_line = TMultiLineString([(0, 0), (0, 2)])
        self.assertFalse(multi_line.is_multipart())

    def test_init_multi_line(self):
        """ test creation of multi LineString and function 'is_multipart' """
        multi_line = TMultiLineString([[(0, 0), (0, 2)], [(1, 0), (1, 2)]])
        self.assertTrue(multi_line.is_multipart())
