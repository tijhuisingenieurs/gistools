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
        
    def test_get_projected_point_at_distance(self):
        """test create point on line at given % of total line length"""
        
        line1 = TLine([(0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 8.0)])
        line2 = TLine([(0.0, 0.0), (2.0, 2.0), (0.0, 4.0)])

        afstand1 = -1.5   
        afstand2 = 11.5
        afstand3 = 1.0

        test = 'point1'
        point1 = line1.get_projected_point_at_distance(afstand1)
        test = 'point2'
        point2 = line1.get_projected_point_at_distance(afstand2)
        test = 'point3'
        point3 = line1.get_projected_point_at_distance(afstand3)
        
        test = 'point4'
        point4 = line2.get_projected_point_at_distance(afstand1)
        test = 'point5'        
        point5 = line2.get_projected_point_at_distance(afstand2)
        test = 'point6'
        point6 = line2.get_projected_point_at_distance(afstand3)

        self.assertEqual(point1, (0.0, -1.5))
        self.assertEqual(point2, (2.0, 9.5))
        self.assertEqual(point3, (0.0, 1.0))
        
        self.assertEqual(point4, (-sqrt((afstand1*afstand1)/2), -sqrt((afstand1*afstand1)/2)))
        self.assertEqual(round(point5[0], 3), (-4.132))
        self.assertEqual(round(point5[1], 3), (8.132))
        self.assertEqual(round(point6[0], 3), round(sqrt((afstand3*afstand3)/2),3))
        self.assertEqual(round(point6[1], 3), round(sqrt((afstand3*afstand3)/2),3))


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

#     def test_get_projected_point_at_distance(self):
#         """test create point on line at given % of total line length"""
#         afstand1 = -1.5   
#         afstand2 = 11.5
#         afstand3 = 1.0
# 
#         line3 = TMultiLineString([((0.0, 0.0), (0.0, 2.0)), ((2.0, 2.0), (2.0, 8.0))])
#                  
#         point1a = line3.get_projected_point_at_distance(afstand1)
#         point2a = line3.get_projected_point_at_distance(afstand2)
#         point3a = line3.get_projected_point_at_distance(afstand3)                
#         
#         self.assertEqual(point1a, (0.0, -1.5))
#         self.assertEqual(point2a, (2.0, 11.5))
#         self.assertEqual(point3, (0.0, 0.1))