from gistools.utils.geometry import tshape
from shapely.geometry import Point
from gistools.utils.collection import MemCollection

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
    id_list = []

    for line in sorted_lines:

        line_shape = tshape(line['geometry'])
        pnts_on_line = []

        for point in points.filter(bbox=line_shape.bounds, precision=10**-6):
            pnt = Point(point['geometry']['coordinates'])

            if line_shape.almost_intersect_with_point(pnt, decimals=2):
                point['dist'] = line_shape.project(pnt)
                pnts_on_line.append(point)

        pnts_on_line.sort(key=lambda li: li['dist'])

        if (line_direction_field is not None and
                (line['properties'][line_direction_field] < 0)):
            pnts_on_line.reverse()

        for point in pnts_on_line:
            # check if point has already been processed (in case point is om multiple lines)
            if point['id'] not in id_list:
            # Check if selected
                if point['selected']:
                    point_id = point['id']
                    id_list.append(point_id)
                    point['properties'][point_number_field] = i
                    i += 1

    return points

def number_points_on_line_boorpunten(lines,
                          points,
                          line_number_field='nr',
                          point_number_field='nr',
                          start_number=1):
    """ Renumber the points on a set of numbered lines. Adjusted for boorpunten. No direction needed and the selected
    part is removed and an extra memcollection in generated.

    lines (collection of LineString of MultiLineString): lines with a number
    points (collection of Point): points which will be renumbered
    line_number_field (string): property name of line with order number. The order is ascending and the 0 will be
            ignored. preferably use a integer property/ field
    line_direction_field (string): optional - property/ field indicate of the points must be numbered in
            the direction of the shape (for values >= 0) or in opposite direction (for values < 0)
    point_number_field (string): output property/ field of the new (renumbered) index
    start_number (int): first number in index range
    :return: memcollection from hernummered points
    """

    sorted_lines = [l for l in lines if l['properties'][line_number_field] not in (0, 0.0, '', None)]
    sorted_lines.sort(key=lambda li: li['properties'][line_number_field])

    i = start_number
    id_list = []
    pnts_on_line_total = []

    for line in sorted_lines:

        line_shape = tshape(line['geometry'])
        pnts_on_line = []

        for point in points.filter(bbox=line_shape.bounds, precision=10**-6):
            pnt = Point(point['geometry']['coordinates'])

            if line_shape.almost_intersect_with_point(pnt, decimals=2):
                point['dist'] = line_shape.project(pnt)
                pnts_on_line.append(point)

        pnts_on_line.sort(key=lambda li: li['dist'])

        for point in pnts_on_line:
            # check if point has already been processed (in case point is om multiple lines)
            if point['id'] not in id_list:
                point_id = point['id']
                id_list.append(point_id)
                point['properties'][point_number_field] = i
                i += 1
                pnts_on_line_total.append(point)
     #Op een of andere manier zouden deze point_number_fields al aan de point_col moeten zijn toegevoged,
     #  maar dat gebeurt niet. Daarom een extra list (pnts_on_line_total) en een nieuwe memcollection.
    hernummered_points = MemCollection(geometry_type='MultiPoint')
    hernummered_points.writerecords(pnts_on_line_total)
    return hernummered_points