import unittest
from shapely.geometry import Point
from gistools.utils.geometry import TLine, TMultiLineString
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

    def test_haakselijn_op_horizontaal_reversed(self):
        """test haakselijn on point on horizontal line"""

        point = Point(2, 1)
        line = TLine([(3, 3), (3, 1), (0, 1), (0, 0)])
        haakselijn = line.get_haakselijn_point(point, 2.0)

        self.assertTupleEqual(haakselijn, ((2.0, 0.0), (2.0, 1.0), (2.0, 2.0)))

    def test_haakselijn_op_vertikaal_reversed(self):
        """test haakselijn on point on vertical line"""

        point = Point(3, 2)
        line = TLine([(3, 3), (3, 1), (0, 1), (0, 0)])
        haakselijn = line.get_haakselijn_point(point, 2.0)

        self.assertTupleEqual(haakselijn, ((4.0, 2.0), (3.0, 2.0), (2.0, 2.0)))

    def test_haakselijn_op_diagonaal_reversed(self):
        """test haakselijn on point on diagonal line"""

        point = Point(2, 2)
        line = TLine([(2, 5), (3, 3), (0, 0)])
        haakselijn = line.get_haakselijn_point(point, sqrt(8.0))

        self.assertTupleEqual(haakselijn, ((3.0, 1.0), (2.0, 2.0), (1.0, 3.0)))
                
    def test_haakselijn_op_horizontaal_boundary(self):
        """test haakselijn on point on horizontal line"""

        point = Point(3, 3)
        line = TLine([(0, 0), (0, 1), (3, 1), (3, 3)])
        haakselijn = line.get_haakselijn_point(point, 2.0)

        self.assertTupleEqual(haakselijn, ((2.0, 3.0), (3.0, 3.0), (4.0, 3.0)))
        
    def test_haakselijn_punt_buiten_lijn(self):
        """test haakselijn on point on horizontal line"""

        point = Point(2, 0)
        line = TLine([(0, 0), (0, 1), (3, 1), (3, 3)])
        haakselijn = line.get_haakselijn_point(point, 2.0)

        self.assertTupleEqual(haakselijn, ((2.0, 1.0), (2.0, 0.0), (2.0, -1.0)))

    def test_segment_richting(self):
        """test segment direction on point on line"""

        point = Point(2, 2)
        line = TLine([(0, 0), (3, 3), (2, 5)])
        richting = line.get_segment_richting_point(point)

        self.assertTupleEqual(richting, (3.0, 3.0))
    
    def test_segment_richting_boundary(self):
        """test segment direction on point at boundary of line"""

        point = Point(3, 5)
        line = TLine([(0, 0), (3, 3), (3, 5)])
        richting = line.get_segment_richting_point(point)

        self.assertTupleEqual(richting, (0.0, 2.0))

    def test_get_point_at_distance(self):
        """test create point on line at given distance"""
        
        line = TLine([(0, 0), (0, 2), (2, 2), (2, 4)])
        afstand = 5
        point = line.get_point_at_distance(afstand)
        segment = line.get_line_part_dist(afstand)
        
        self.assertTupleEqual(segment[0], (2, (2, 2), 4.0))
        self.assertTupleEqual(segment[1], (3, (2, 4), 6.0))
        self.assertEqual(segment[2], 5.0)
        
        self.assertEqual(point, (2.0, 3.0))

    def test_get_point_at_percentage(self):
        """test create point on line at given % of total line length"""
        
        line = TLine([(0, 0), (0, 2), (2, 2), (2, 8)])
        perc = 0.5
        point = line.get_point_at_percentage(perc)
        segment = line.get_line_part_perc(perc)
        
        self.assertTupleEqual(segment[0], (2, (2, 2), 4.0))
        self.assertTupleEqual(segment[1], (3, (2, 8), 10.0))
        self.assertEqual(segment[2], 5.0)
        
        self.assertEqual(point, (2.0, 3.0))

    def test_get_flipped_line(self):
        """test flip line"""
        
        line = TLine([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (2.0, 4.0), (4.0, 4.0)])
        flipped_line = line.get_flipped_line()
        
        self.assertEqual(flipped_line, ((4.0, 4.0), (2.0, 4.0), (2.0, 2.0), (1.0, 1.0), (0.0, 0.0)))

    def test_get_vertexes(self):

        line = TLine([(-10, 0), (-4, 0), (-3, 0), (10, 0)])

        vertexes = line.vertexes

        self.assertListEqual(vertexes, [(-10, 0), (-4, 0), (-3, 0), (10, 0)])

    def test_get_coordinates(self):
        line = TLine([(-10, 0), (-4, 0), (-3, 0), (10, 0)])

        coordinates = line.coordinates

        self.assertTupleEqual(coordinates, ((-10, 0), (-4, 0), (-3, 0), (10, 0)))

    def test_add_vertex_at_point(self):
        """ test TLine.add_vertex_at_point"""

        line = TLine([(-10, 0), (10, 0)])

        new_line = line.add_vertex_at_point(Point(0, 0))
        self.assertTupleEqual(new_line.coordinates, ((-10, 0), (0, 0), (10, 0)))

    def test_split_line_at_vertex(self):
        """ test TMultiLineString.split_at_vertex"""

        line = TLine([(-10, 0), (-6, 0), (10, 0)])

        first_line, second_line = line.split_at_vertex(1)
        self.assertTupleEqual(first_line.coordinates, ((-10, 0), (-6, 0)))
        self.assertTupleEqual(second_line.coordinates, ((-6, 0), (10, 0)))

        first_line, second_line = line.split_at_vertex(0)
        self.assertTupleEqual(first_line.coordinates, ((-10, 0), (-10, 0)))
        self.assertTupleEqual(second_line.coordinates, ((-10, 0), (-6, 0), (10, 0)))

        first_line, second_line = line.split_at_vertex(2)
        self.assertTupleEqual(first_line.coordinates, ((-10, 0), (-6, 0), (10, 0)))
        self.assertTupleEqual(second_line.coordinates, ((10, 0), (10, 0)))


class TestTMultiLine(unittest.TestCase):

    def test_get_vertexes(self):

        line = TMultiLineString([((-10, 0), (-4, 0)), ((-3, 0), (10, 0))])

        vertexes = line.vertexes

        self.assertListEqual(vertexes, [(-10, 0), (-4, 0), (-3, 0), (10, 0)])

    def test_get_coordinates(self):

        line = TMultiLineString([((-10, 0), (-4, 0)), ((-3, 0), (10, 0))])

        coordinates = line.coordinates

        self.assertTupleEqual(coordinates, (((-10, 0), (-4, 0)), ((-3, 0), (10, 0))))

    def test_add_vertex_at_point(self):
        """ test TMultiLineString.add_vertex_at_point"""

        line = TMultiLineString([((-10, 0), (-4, 0)), ((-3, 0), (10, 0))])

        new_line = line.add_vertex_at_point(Point(-6, 0))
        self.assertTupleEqual(new_line.coordinates, (((-10, 0), (-6, 0), (-4, 0)), ((-3, 0), (10, 0))))

        new_line = line.add_vertex_at_point(Point(0, 0))
        self.assertTupleEqual(new_line.coordinates, (((-10, 0), (-4, 0)), ((-3, 0), (0, 0), (10, 0))))

    def test_split_line_at_vertex(self):
        """ test TMultiLineString.split_at_vertex"""

        line = TMultiLineString([((-10, 0), (-6, 0), (-4, 0)), ((-3, 0), (10, 0))])
        first_line, second_line = line.split_at_vertex(1)

        self.assertTupleEqual(first_line.coordinates, (((-10, 0), (-6, 0)), ))
        self.assertTupleEqual(second_line.coordinates, (((-6, 0), (-4, 0)), ((-3, 0), (10, 0))))

        line = TMultiLineString([((-10, 0), (-4, 0)), ((-3, 0), (0, 0), (10, 0))])

        first_line, second_line = line.split_at_vertex(3)
        self.assertTupleEqual(first_line.coordinates, (((-10, 0), (-4, 0)), ((-3, 0), (0, 0))))
        self.assertTupleEqual(second_line.coordinates, (((0, 0), (10, 0)), ))

        first_line, second_line = line.split_at_vertex(2)
        self.assertTupleEqual(first_line.coordinates, (((-10, 0), (-4, 0)), ((-3, 0), (-3, 0))))
        self.assertTupleEqual(second_line.coordinates, (((-3, 0), (0, 0), (10, 0)), ))

        first_line, second_line = line.split_at_vertex(0)
        self.assertTupleEqual(first_line.coordinates, (((-10, 0), (-10, 0)), ))
        self.assertTupleEqual(second_line.coordinates, (((-10, 0), (-4, 0)), ((-3, 0), (0, 0), (10, 0))))

        first_line, second_line = line.split_at_vertex(4)
        self.assertTupleEqual(first_line.coordinates, (((-10, 0), (-4, 0)), ((-3, 0), (0, 0), (10, 0))))
        self.assertTupleEqual(second_line.coordinates, (((10, 0), (10, 0)), ))

    def test_get_line_with_length(self):

        line = TLine([(0, 0), (10, 0)])

        output = line.get_line_with_length(20, 0)
        self.assertTupleEqual(output.coordinates, ((0, 0), (20, 0)))

        output = line.get_line_with_length(20, 1)
        self.assertTupleEqual(output.coordinates, ((-10, 0), (10, 0)))

        output = line.get_line_with_length(20, 0.5)
        self.assertTupleEqual(output.coordinates, ((-5, 0), (15, 0)))

        line = TLine([(10, 0), (0, 0)])

        output = line.get_line_with_length(20, 0)
        self.assertTupleEqual(output.coordinates, ((10, 0), (-10, 0)))

        output = line.get_line_with_length(20, 0.5)
        self.assertTupleEqual(output.coordinates, ((15, 0), (-5, 0)))

        line = TLine([(5, 5), (10, 10)])

        output = line.get_line_with_length(3*sqrt(50), 0.5)
        self.assertTupleEqual(output.coordinates, ((0, 0), (15, 15)))

        output = line.get_line_with_length(3*sqrt(50), 0)
        self.assertTupleEqual(output.coordinates, ((5, 5), (20, 20)))
