from gistools.utils.geometry import tshape
from shapely.geometry import Point


def number_points_on_line(lines,
                          points,
                          line_number_field='nr',
                          line_direction_field=None,
                          point_number_field='nr'):

    sorted_lines = [l for l in lines]
    sorted_lines.sort(key=lambda li: li['properties'][line_number_field])

    i = 0

    for point in points:
        point['properties'][point_number_field] = None

    for line in sorted_lines:

        line_shape = tshape(line['geometry'])
        pnts_on_line = []

        for point in points.filter(bbox=line_shape.bounds):
            pnt = Point(point['geometry']['coordinates'])

            if line_shape.intersects(pnt):
                point['dist'] = line_shape.project(pnt)
                pnts_on_line.append(point)

        pnts_on_line.sort(key=lambda li: li['dist'])

        if (line_direction_field is not None and
                line['properties'][line_direction_field] < 0):
            pnts_on_line.reverse()

        for point in pnts_on_line:
            point['properties'][point_number_field] = i
            i += 1

    return points
