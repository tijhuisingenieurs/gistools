from shapely.geometry import Point, LineString
from math import sqrt
from sympy.physics.units import length

class TLine(LineString):

    def __init__(self, *args, **kwargs):
        self._length_array = None
        super(TLine, self).__init__(*args, **kwargs)

    def get_line_part(self, point):
        """ get vertex before and after point on line

        point (shapely.Point): point to find on or near line
        return: tuple with:
                vertex before as tuple with: (nr of vertex on line, vertex 
                    coordinates, distance on line)
                vertex after as tuple with: (nr of vertex on line, vertex 
                    coordinates, distance on line)
                distance of point on line
        """
        if self._length_array is None:
            self._length_array = [(i, p, self.project(Point(p))) 
                                  for i, p in enumerate(self.coords)]

        dist = self.project(point)

        for p in self._length_array:
            if dist <= p[2]:
                vertex_before = self._length_array[p[0] - 1]
                vertex_after = p
                break

        return (vertex_before, vertex_after, dist)

    def get_segment_richting(self, point):
        """ get vertex before and after point on line
        and get direction of line segment

        point (shapely.point): point to find on or near line
        return: direction of segment as tuple [dx,dy]
        """
        
        segment = self.get_line_part(point)
        
        vertex_before = segment[0][1]
        vertex_after = segment[1][1]
        
        delta_x = vertex_after[0]-vertex_before[0]
        delta_y = vertex_after[1]-vertex_before[1]
        richting = [delta_x,delta_y]
        
        return (richting)
        
    
    def get_haakselijn(self, point, length):
        """ create line trough point on line perpendicular to direction of 
        coordinate set uses get_lin_part

        point (shapely.point): point at which to create perpendicular
        length: length of perpendicular to create
        return: Tline with 3 vertices (point left, point on line, point right)
        """

        richting = self.get_segment_richting(point)
        
#         richting segment = (delta x,delta y)
#         haakse richting = -delta x / delta y

        if richting[0] <> 0 and richting[1] <> 0 :
            haakse_richting = -richting[0]/richting[1]
            if richting[1] > 0:
                delta_x_links = -0.5 * length / (sqrt(1+(richting[0]/richting[1])**2))
            else:
                delta_x_links = -0.5 * length / (sqrt(1+(richting[0]/richting[1])**2))
            
            if richting[0] > 0:
                delta_y_links = abs(haakse_richting)*abs(delta_x_links)
            else:
                delta_y_links = -abs(haakse_richting)*abs(delta_x_links)
        
        if richting[1] == 0 and richting[0] <> 0:
            delta_x_links = 0
            if richting[0] > 0:
                delta_y_links = 0.5 * length
            else:
                delta_y_links = -0.5 * length
        
        if richting[0] == 0 and richting[1] <> 0:
            delta_y_links = 0
            if richting[1] > 0:
                delta_x_links = -0.5 * length
            else:
                delta_x_links = 0.5 * length         
        
#         ToDo: wat als er twee punten op elkaar liggen... devision by zero??
#               kan dit in de praktijk voorkomen? En welk tuple krijg je dan
#               voor het segment bij een punt op deze punten
#               Exception inbouwen voor richting[0] == 0 and richting[1] == 0
        
        delta_x_rechts = - delta_x_links
        delta_y_rechts = -delta_y_links
        
        x_start = point.x + delta_x_links
        y_start = point.y + delta_y_links
        x_eind = point.x + delta_x_rechts
        y_eind = point.y + delta_y_rechts
        
        haakselijn = ((x_start,y_start), (point.x,point.y), (x_eind,y_eind))
        
        return haakselijn
