from gistools.utils.geometry import tshape
from shapely.geometry import Point


def number_points_on_line(lines,
                          points,
                          line_number_field='nr',
                          line_direction_field=None,
                          point_number_field='nr',
                          start_number=1):
    """ Renumber the points on a set of numbered lines

    lines (collection of LineString of MultiLineString): lines with a number
    points (collection of Point): points which will be renumbered
    line_number_field (string): property name of line with order number. The order is ascending and the 0 will be
            ignored. preferably use a integer property/ field
    line_direction_field (string): optional - property/ field indicate of the points must be numbered in
            the direction of the shape (for values >= 0) or in opposite direction (for values < 0)
    point_number_field (string): output property/ field of the new (renumbered) index
    start_number (int): first number in index range
    :return:
    """

    sorted_lines = [l for l in lines if l['properties'][line_number_field] not in (0, 0.0, '', None)]
    sorted_lines.sort(key=lambda li: li['properties'][line_number_field])

    i = start_number

    for point in points:
        point['properties'][point_number_field] = None

    for line in sorted_lines:

        line_shape = tshape(line['geometry'])
        pnts_on_line = []

        for point in points.filter(bbox=line_shape.bounds):
            pnt = Point(point['geometry']['coordinates'])

            if line_shape.almost_intersect_with_point(pnt):
                point['dist'] = line_shape.project(pnt)
                pnts_on_line.append(point)

        pnts_on_line.sort(key=lambda li: li['dist'])

        if (line_direction_field is not None and
                line['properties'][line_direction_field] < 0):
            pnts_on_line.reverse()

        for point in pnts_on_line:
            # check if number already set in cae point is om multiple lines
            if point['properties'][point_number_field] is None:
                point['properties'][point_number_field] = i
                i += 1

    return points
