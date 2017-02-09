from shapely.geometry import Point, LineString, MultiLineString

import logging
logger = logging.getLogger(__name__)


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
        # todo: make sure function is correct when point is on start vertex

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

    def get_haakselijn(self, point, length):
        """

        :param point:
        :param length:
        :return:
        """

        pass


class TMultiLineString(MultiLineString, TLine):

    def __init__(self, coords):
        self._length_array = None
        self.line_parts = []

        if len(coords) == 0 or len(coords[0]) == 0:
            logger.warning('line with no or incorrect elements')
        elif type(coords[0][0]) in [float, int]:
            # single line
            self.line_parts.append(TLine(coords))
        else:
            # multipart
            for part in coords:
                self.line_parts.append(TLine(part))

    def is_multipart(self):
        return len(self.line_parts) > 1
