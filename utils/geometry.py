from math import sqrt, degrees, atan2
from shapely.geometry import (Point, MultiPoint, LineString, MultiLineString,
                              Polygon, MultiPolygon)

import logging
log = logging.getLogger(__name__)

def tshape(geometry):

    geom_type = geometry['type'].lower()
    coordinates = geometry['coordinates']

    if geom_type == 'linestring':
        return TLine(coordinates)
    elif geom_type == 'multilinestring':
        return TMultiLineString(coordinates)
    elif geom_type == 'point':
        return Point(coordinates)
    elif geom_type == 'multipoint':
        return MultiPoint(coordinates)
    elif geom_type == 'polygon':
        return Polygon(coordinates)
    elif geom_type == 'multipolygon':
        return MultiPolygon(coordinates)
    else:
        raise ValueError("geometry type '{0}' not supported".format(geom_type))


class TLine(LineString):

    def __init__(self, *args, **kwargs):
        self._length_array = None
        super(TLine, self).__init__(*args, **kwargs)

    def add_vertex_at_point(self, point):
        """ add vertex at point on the line

        point (Point): Shapely point on a position on the line which will be added
        returns: new TLine with vertex
        """

        vertex_before, vertex_after, dist = self.get_line_part_point(point)

        coords = self.coords[:]
        coords.insert(vertex_after[0], point.coords[0])
        return TLine(coords)

    def split_at_vertex(self, vertex_nr):
        """ split line at vertex nr

        vertex_nr: vertex nr where line will be split
        returns (tuple of TLines): the to splitted line parts

        note: if line is plit at first or last point of the line, an geometry is returned containing
        a geometry with the same start and endpoint (is that the required behavoir, or better raise an exception?)
        """

        coords = self.coords[:]
        if vertex_nr == 0:
            first_line = (coords[0], coords[0])
            second_line = coords
            log.warning('line split on first point of line, create line with same start and end point')
        elif vertex_nr == len(coords)-1:
            first_line = coords
            second_line = (coords[-1], coords[-1])
            log.warning('line split on last point of line, create line with same start and end point')
        else:
            first_line = coords[:vertex_nr+1]
            second_line = coords[vertex_nr:]

        return TLine(first_line), TLine(second_line)

    @property
    def coordinates(self):
        """representation in the format of ((x, y),(x, y))"""
        return tuple([pnt for pnt in self.coords])

    def almost_intersect_with_point(self, other, decimals=6):
        """Test intersection taking an small possible error in account

        other (shapely geometry): other geometry to test intersection
        decimals (int): decimals in precision to take into account
        return (bool): if other geometry intersects
        """

        log.warning(self.distance(other))
        if self.intersects(other):
            return True
        elif self.distance(other) < 10**-decimals:
            return True
        else:
            return False

    @property
    def vertexes(self):
        """returns list with vertexes, without link information
        (same for multi geoemtries as single geometries"""
        return [p for p in self.coords]

    def get_line_part_dist(self, afstand):
        """ get vertex before and after distance on line

        afstand: distance to find on line
        return: tuple with:
                vertex before as tuple with: (nr of vertex on line, vertex 
                    coordinates, distance on line)
                vertex after as tuple with: (nr of vertex on line, vertex 
                    coordinates, distance on line)
                distance used to find segment
        """
        # todo: make sure function is correct when point is on start vertex

        if self._length_array is None:
            if hasattr(self, 'geoms'):
                coords = []
                for p in self.geoms:
                    coords.extend(p.coords)
                self._length_array = [(i, p, self.project(Point(p)))
                                      for i, p in enumerate(coords)]
            else:
                self._length_array = [(i, p, self.project(Point(p)))
                                  for i, p in enumerate(self.coords)]

        dist = afstand

        vertex_before = None 
        vertex_after = None

        for p in self._length_array:
            if dist <= p[2]:
                vertex_before = self._length_array[p[0] - 1]
                vertex_after = p
                break
        
        if vertex_before is None:
            log.warning("No vertex found at distance {0} for line {1}".format(dist, str(self)))
        
        line_part = (vertex_before, vertex_after, dist)

        return line_part

    def get_line_part_point(self, point):
        """ get vertex before and after point on line

        point (shapely.Point): point to find on or near line
        return: tuple with:
                vertex before as tuple with: (nr of vertex on line, vertex
                    coordinates, distance on line)
                vertex after as tuple with: (nr of vertex on line, vertex
                    coordinates, distance on line)
                distance used to find segment
        """
        afstand = self.project(point)
        line_part = self.get_line_part_dist(afstand)

        return line_part

    def get_line_part_perc(self, perc):
        """ get vertex before and after percentage of line

        perc: percentage of total line length.
                    decimal values between 0 and 1
        return: tuple with:
                vertex before as tuple with: (nr of vertex on line, vertex
                    coordinates, distance on line)
                vertex after as tuple with: (nr of vertex on line, vertex
                    coordinates, distance on line)
                distance used to find segment
        """
        afstand = self.length * perc
        line_part = self.get_line_part_dist(afstand)

        return line_part

    def get_segment_richting_dist(self, afstand):
        """ get vertex before and after distance on line
        and get direction of line segment

        point (shapely.point): point to find on or near line
        return: direction of segment as tuple [dx,dy]
        """

        segment = self.get_line_part_dist(afstand)

        vertex_before = segment[0][1]
        vertex_after = segment[1][1]

        delta_x = vertex_after[0] - vertex_before[0]
        delta_y = vertex_after[1] - vertex_before[1]
        richting = (delta_x, delta_y)

        return richting

    def get_segment_richting_point(self, point):
        """ get vertex before and after distance on line
        and get direction of line segment

        point (shapely.point): point to find on or near line
        return: direction of segment as tuple [dx,dy]
        """

        afstand = self.project(point)
        richting = self.get_segment_richting_dist(afstand)

        return richting

    def get_haakselijn_point(self, point, length):
        """ create line at distance on line perpendicular to direction of
        coordinate set
        uses get_line_part

        point (shapely.point): point at which to create perpendicular
        length: length of perpendicular to create
        return: Tline with 3 vertices (point left, point on line, point right)
        """

        richting = self.get_segment_richting_point(point)

#         richting segment = (delta x,delta y)
#         haakse richting = -delta x / delta y

        if richting[0] != 0.0 and richting[1] != 0.0:
            haakse_richting = -richting[0] / richting[1]
            if richting[1] > 0.0:
                delta_x_links = -0.5 * length / (sqrt(1 + (richting[0] / richting[1])**2))
            else:
                delta_x_links = 0.5 * length / (sqrt(1 + (richting[0] / richting[1])**2))

            if richting[0] > 0.0:
                delta_y_links = abs(haakse_richting) * abs(delta_x_links)
            else:
                delta_y_links = -abs(haakse_richting) * abs(delta_x_links)

        elif richting[1] == 0.0 and richting[0] != 0.0:
            delta_x_links = 0.0
            if richting[0] > 0.0:
                delta_y_links = 0.5 * length
            else:
                delta_y_links = -0.5 * length

        elif richting[0] == 0.0 and richting[1] != 0.0:
            delta_y_links = 0.0
            if richting[1] > 0.0:
                delta_x_links = -0.5 * length
            else:
                delta_x_links = 0.5 * length
        else:
            log.warning('Haakselijn on segment of length 0.0 is not possible!')
            delta_x_links = 0
            delta_y_links = 0

#         ToDo: wat als er twee punten op elkaar liggen... devision by zero??
#               kan dit in de praktijk voorkomen? En welk tuple krijg je dan
#               voor het segment bij een punt op deze punten
#               Exception inbouwen voor richting[0] == 0 and richting[1] == 0

        delta_x_rechts = -delta_x_links
        delta_y_rechts = -delta_y_links

        x_start = point.x + delta_x_links
        y_start = point.y + delta_y_links
        x_eind = point.x + delta_x_rechts
        y_eind = point.y + delta_y_rechts

        haakselijn = ((x_start, y_start), (point.x, point.y), (x_eind, y_eind))

        return haakselijn

    def get_point_at_distance(self, afstand):
        """ create a point on a line at a given distance from the line origin

        afstand: distance from line origin to create point at
        return: point (shapely.point)
        """

        return self.interpolate(afstand).coords[0]
        # segment = self.get_line_part_dist(afstand)
        # vertex_before = segment[0][1]
        # vertex_after = segment[1][1]
        #
        # delta_x_segment = vertex_after[0] - vertex_before[0]
        # delta_y_segment = vertex_after[1] - vertex_before[1]
        #
        # lengte_segment = segment[1][2] - segment[0][2]
        #
        # # bereken verschil in coordinaten voor elke meter langs segment:
        # delta_x_m = delta_x_segment / lengte_segment
        # delta_y_m = delta_y_segment / lengte_segment
        #
        # # bereken restlengte in segment
        # afstand_segment = afstand - segment[0][2]
        #
        # # bepaal coordinaten van het nieuwe punt
        # point_x = vertex_before[0] + (afstand_segment * delta_x_m)
        # point_y = vertex_before[1] + (afstand_segment * delta_y_m)
        #
        # # point = (delta_x_m, delta_y_m)
        # point = (point_x, point_y)
        #
        # return point

    def get_point_at_percentage(self, perc):
        """ create a point on a line at a given percentage of total line length
        from the line origin

        perc: percentage from line length to create point at
        return: point (shapely.point)
        """

        afstand = self.length * perc
        point = self.get_point_at_distance(afstand)

        return point
    
    def get_projected_point_at_distance(self, afstand):
        """ create a point on a line at a given distance of total line length
        from the line origin, including (negative) distances outside line geom

        perc: percentage from line length to create point at
        return: point (shapely.point)
        """
        dist = afstand
        
        if afstand < 0:
            richting = self.get_segment_richting_dist(0.001)                  
            x = self.coordinates[0][0]
            y = self.coordinates[0][1]                                    
            
            # richting is dx en dy -> omrekenen naar dx en dy per 1 eenheid lengte
            
            if richting[0] == 0:
                new_x = x
                new_y = y + afstand
            elif richting[1] == 0:
                new_y = y
                new_x = x + afstand
            else:   
                length_richting = sqrt((richting[0]*richting[0]) + 
                                       (richting[1]*richting[1]))
                
                delta_x_per_eenheid = richting[0] / length_richting
                delta_y_per_eenheid = richting[1] / length_richting
                         
                new_x = x + (afstand * delta_x_per_eenheid)
                new_y = y + (afstand * delta_y_per_eenheid)
            
            point = (new_x, new_y)
            
        elif afstand > self.length:
            richting = self.get_segment_richting_dist(self.length)
            x = self.coordinates[-1][0]
            y = self.coordinates[-1][1]
            
            extensie = afstand - self.length  
                                
            # richting is dx en dy -> omrekenen naar dx en dy per 1 eenheid lengte
            
            if richting[0] == 0:
                new_x = x
                new_y = y + extensie
            elif richting[1] == 0:
                new_y = y
                new_x = x + extensie
            else:   
                length_richting = sqrt((richting[0]*richting[0]) + 
                                       (richting[1]*richting[1]))
                
                delta_x_per_eenheid = richting[0] / length_richting
                delta_y_per_eenheid = richting[1] / length_richting
                
                          
                new_x = x + (extensie * delta_x_per_eenheid)
                new_y = y + (extensie * delta_y_per_eenheid)
            
            point = (new_x, new_y)
        
        else:
            point = self.get_point_at_distance(afstand)

        return point

    def get_flipped_line(self):
        """ flip geometry of line

        return: Tline in flipped direction
        """

        flipped_line = []      
        
        if hasattr(self, 'geoms'):            
            for geom in reversed(self.geoms):
                flipped_line.append(tuple([p for p in reversed(geom.coords)]))                                                
        else:
            flipped_line = tuple([p for p in reversed(self.coords)])      
        
        return flipped_line
    
    def get_line_angle(self):
        """ get angle of line in degrees, between start and endpoint of line
        North = 0 degrees, East = 90 degrees
        
        return: value of angel
        """

        coords = []
        if hasattr(self, 'geoms'):
            for p in self.geoms:
                coords.extend(p.coords)
        else:
            coords = self.coords    

        start_x = coords[0][0]
        start_y = coords[0][1]
        end_x = coords[-1][0]
        end_y = coords[-1][1]

        if start_x == end_x:
            line_angle = 0
        elif start_y == end_y:
            line_angle = 90
        else:
            line_angle = round(degrees(atan2((end_x - start_x),(end_y - start_y))),1)
            if line_angle < 0:
                line_angle = 180 + line_angle
                           
        return line_angle

    def get_line_with_length(self, target_length, scale_point_perc=0):
        """ get line with given line, with same direction and scalled
        around the scale point
        
        target_length (float): length in shape units
        scale_point_perc  (float): percentage (0-1)of point on line to relatively scale around
            0=begin of line, 1=end of line, 0.5 = halfway 
        return: TLine with new line geometry
        """

        scale_point = self.get_point_at_percentage(float(scale_point_perc))
        orig_length = self.length

        if orig_length <= 0:
            log.error('length of shape is 0 or lower. returned orginal without scaling')
            return TLine(self.coordinates)

        scale_factor = float(target_length) / orig_length

        output_coordinates = []

        for vertex in self.coordinates[0]:
            x = scale_point[0] + (vertex[0] - scale_point[0]) * scale_factor
            y = scale_point[1] + (vertex[1] - scale_point[1]) * scale_factor
            output_coordinates.append((x, y))

        return TLine(output_coordinates)


class TMultiLineString(MultiLineString, TLine):

    def __init__(self, *args, **kwargs):
        self._length_array = None
        super(TMultiLineString, self).__init__(*args, **kwargs)

    def add_vertex_at_point(self, point):
        """ add vertex at point """

        vertex_before, vertex_after, dist = self.get_line_part_point(point)
        nr = 0

        new_line = []

        for line in self.geoms:
            coords = line.coords[:]
            if vertex_after[0] > nr and vertex_after[0] <= nr + len(coords):
                coords.insert(vertex_after[0]-nr, point.coords[0])
            nr += len(coords)
            new_line.append(coords)
        return TMultiLineString(new_line)

    def split_at_vertex(self, vertex_nr):
        """ split line at vertex nr

        vertex_nr: vertex nr where line will be split
        returns (tuple of TLines): the to splitted line parts
        add_multipart_point

        note: if line is plit at first or last point of the line of line part, a geometry is returned containing
        a geometry with the same start and endpoint (is that the required behavoir, or better raise an exception?)
        """

        nr = 0

        first_line = []
        second_line = []

        new_line = first_line

        for line in self.geoms:
            coords = line.coords[:]
            if vertex_nr >= nr and vertex_nr < nr + len(coords):
                # for now, make extra linepart with 2 the same vertexes
                if vertex_nr == nr:
                    new_line.append((coords[0], coords[0]))
                    new_line = second_line
                    new_line.append(coords)
                elif vertex_nr == nr + len(coords)-1:
                    new_line.append(coords)
                    new_line = second_line
                    new_line.append((coords[-1], coords[-1]))
                else:
                    new_line.append(coords[:vertex_nr-nr+1])
                    new_line = second_line
                    new_line.append(coords[vertex_nr-nr:])
            else:
                new_line.append(coords)
            nr += len(coords)
        return TMultiLineString(first_line), TMultiLineString(second_line)

    @property
    def coordinates(self):
        """representation in the format of ((x, y),(x, y))"""
        output = []
        for line in self.geoms:
            output.append(tuple([pnt for pnt in line.coords]))

        return tuple(output)

    @property
    def vertexes(self):
        """returns list with vertexes, without link information
        (same for multi geometries as single geometries"""
        if not hasattr(self, '_vertexes'):
            self._vertexes = []
            for l in self.geoms:
                for p in l.coords:
                    self._vertexes.append(p)
        return self._vertexes
