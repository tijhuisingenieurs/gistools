from shapely.geometry import Point, LineString


class TLine(LineString):

    def __init__(self, *args, **kwargs):
        self._length_array = None
        super(TLine, self).__init__(*args, **kwargs)

    def get_line_part(self, point):
        """ get vertex before and after point on line

        point (shapely.Point): point to find on or near line
        return: tuple with:
                vertex before as tuple with: (nr of vertex on line, vertex coordinates, distance on line)
                vertex after as tuple with: (nr of vertex on line, vertex coordinates, distance on line)
                distance of point on line
        """
        if self._length_array is None:
            self._length_array = [(i, p, self.project(Point(p))) for i, p in enumerate(self.coords)]

        dist = self.project(point)

        for p in self._length_array:
            if dist <= p[2]:
                vertex_before = self._length_array[p[0] - 1]
                vertex_after = p
                break

        return (vertex_before, vertex_after, dist)

    def get_haakselijn(self, point, length):
        """ create line trough point on line perpendicular to direction of coordinate set
        uses get_lin_part

        point (shapely.point): point at which to create perpendicular
        length: length of perpendicular to create
        return: Tline with 3 vertices (point left, point on line, point right)
        """
        
        

        pass
