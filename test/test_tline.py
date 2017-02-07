import unittest
from shapely.geometry import Point, LineString
from utils.geometry import TLine
from math import sqrt


class TestTLine(unittest.TestCase):

    def setUp(self):
        pass

    def test_point_on_line(self):
        """test line on point"""
        point = Point(2, 1)
        line = TLine([(0,0), (0,1), (3,1), (3,3)])
        line_part = line.get_line_part(point)

        self.assertTupleEqual(line_part[0], (1, (0,1), 1.0))
        self.assertTupleEqual(line_part[1], (2, (3, 1), 4.0))
        self.assertEqual(line_part[2], 3.0)

    def test_point_on_line_on_vertex(self):
        """test line on point exact on a vertex"""

        point = Point(3, 1)
        line = TLine([(0,0), (0,1), (3,1), (3,3)])
        line_part = line.get_line_part(point)

        self.assertTupleEqual(line_part[0], (1, (0,1), 1.0))
        self.assertTupleEqual(line_part[1], (2, (3, 1), 4.0))
        self.assertEqual(line_part[2], 4.0)

    def test_haakselijn_op_horizontaal(self):
        """"test haakselijn on point on line"""

        point = Point(2, 1)
        line = TLine([(0, 0), (0, 1), (3, 1), (3, 3)])
        haakselijn = line.get_haakselijn(point, 2.0)

        self.assertTupleEqual(haakselijn, ((2.0, 2.0), (2.0, 0.0)))

    def test_haakselijn_op_diagonaal(self):
        """"test haakselijn on point on line"""

        point = Point(2, 2)
        line = TLine([(0, 0), (3, 3), (2, 5)])
        haakselijn = line.get_haakselijn(point, sqrt(8.0))

        self.assertTupleEqual(haakselijn, ((1.0, 3.0), (3.0, 1.0)))
