from copy import copy
from shapely.geometry import Polygon

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import tshape, TLine, Point


def get_end_points(lines,
                   line_id_field='id',
                   max_delta=0.01):
    """Get endpoints of lines and the number of lines that end in the same point

    lines (collection of MultiLineString of LineString): Input
    line_id_field (string): Name of property/ field which could be used for logging of connected ids of the line
    max_delta (float): max distance between endpoints to make it one connected endpoint
    return (point collection): collection of endpoints with the properties:
        - line_count: number of connected fields
        - line_ids: comma separated list of ids of lines that are connected
        - line_starts: comma separated list of identification if it is the start point (1) or endpoint (0)
            of the connected lines
    """

    points = MemCollection()
    point_sum = MemCollection()

    # get start and endpoints
    for feature in lines:
        line = tshape(feature['geometry'])

        if hasattr(line, 'geoms'):
            # MultiLineString
            p_start = line.geoms[0].coords[0]
            p_end = line.geoms[-1].coords[-1]
        else:
            # LineString
            p_start = line.coords[0]
            p_end = line.coords[-1]

        # start_point
        points.write({'geometry': {'type': 'Point',
                                   'coordinates': p_start},
                      'properties': {
                          'line_id': feature['properties'][line_id_field],
                          'start': True
                      }})
        # end_point
        points.write({'geometry': {'type': 'Point',
                                   'coordinates': p_end},
                      'properties': {
                          'line_id': feature['properties'][line_id_field],
                          'start': False
                      }})

    # link points close to each other
    for point in points:
        if 'connected' not in point['properties']:
            point['properties']['connected'] = set()

        coords = point['geometry']['coordinates']
        bbox = (coords[0] - max_delta,
                coords[1] - max_delta,
                coords[0] + max_delta,
                coords[1] + max_delta)

        near = points.filter(bbox=bbox)

        for p in near:
            if point['id'] == p['id']:
                continue
            elif 'connected' not in p['properties']:
                p['properties']['connected'] = set()

            p['properties']['connected'].add(point['id'])
            point['properties']['connected'].add(p['id'])

    def add_points(point_collection, point_ids_set, extra_point_ids_set):
        """recursive function to link all connected points"""
        diff = extra_point_ids_set.difference(point_ids_set)

        point_ids_set = point_ids_set.union(extra_point_ids_set)
        # loop over new points
        for p_id in diff:
            if 'done' not in point_collection[p_id]['properties']:
                point_collection[p_id]['properties']['done'] = True
                point_ids_set = add_points(point_collection,
                                           point_ids_set,
                                           point_collection[p_id]['properties']['connected'])
        return point_ids_set

    # combine points close to each other
    for point in points:
        cluster_ids = set()
        if 'done' not in point['properties']:
            cluster_ids.add(point['id'])
            point['properties']['done'] = True
            cluster_ids = add_points(points,
                                     cluster_ids,
                                     point['properties']['connected'])

        if len(cluster_ids) > 0:
            x = 0
            y = 0
            for ids in cluster_ids:
                x += points[ids]['geometry']['coordinates'][0]
                y += points[ids]['geometry']['coordinates'][1]

            x /= len(cluster_ids)
            y /= len(cluster_ids)

            line_ids = [str(points[ids]['properties']['line_id']) for ids in cluster_ids]

            line_starts = [str(int(points[ids]['properties']['start'])) for ids in cluster_ids]

            point_sum.write({
                'geometry': {'type': 'Point',
                             'coordinates': (x, y)},
                'properties': {
                    'line_count': len(cluster_ids),
                    'line_ids': ','.join(line_ids),
                    'line_starts': ','.join(line_starts)
                }
            })

    return point_sum


def connect_lines(lines,
                  line_id_field='id',
                  correct_overshoot_units=None,
                  correct_with_extend_units=None,
                  extend_with_angle_degrees=None,
                  snap_to_endpoint_units=None,
                  split_line_at_connection=False
                  ):
    """ Tool which makes sure lines connect correctly.
    lines (collection of LineString or MultiLineString): Input collection
    ...
    split_line_at_connection (bool): split the lines on crosssections with other lines.


    The tool has serveral options:
    1) Tool makes sure a connected line has a vertex on the connection
    2) Tool makes sure that when there is a small 'overshoot' this overshoot is removed
       and the lines are connected as mentioned under point 1
    3) When there is a small gap till a line, the line is 'extended' to connect
       with the other line as mentioned under point 1
    4) As in point 3 but with a specfic max angle
    5) When the connection is close to the end or begin
       of a line, the connection is moved (snapped) to the end or begin point
    6) Instead of adding a vertex as mentioned in 1), the connected line is split in two
       parts at the connection

    implemented cases:
    1) add vertex when line touches other line
    6) split line on connection

    """
    for feature in lines:
        feature['properties']['link_start'] = []
        feature['properties']['link_end'] = []
        feature['properties']['link_loc'] = []


    for feature in lines:
        line = tshape(feature['geometry'])
        multi_geom = feature['geometry']['type'].lower() == 'multilinestring'

        if multi_geom:
            start_pnt = Point(line.geoms[0].coords[0])
            end_pnt = Point(line.geoms[-1].coords[-1])
        else:
            start_pnt = Point(line.coords[0])
            end_pnt = Point(line.coords[-1])

        start_line = TLine()
        end_line = TLine()

        extended_line_start = TLine()
        extended_line_end = TLine()

        extended_line_start_angle = Polygon()
        extended_line_end_angle = Polygon()

        # if extend_with_angle_degrees is None:
        #     extend_line_start = TLine()
        #     extend_line_end = TLine()
        # else:
        #     extend_line_start = Polygon()
        #     extend_line_start = Polygon()

        for candidate in lines.filter(bbox=line.bounds):
            if candidate['id'] == feature['id']:
                continue

            cand_line = tshape(candidate['geometry'])

            # check if endpoint is on other line

            if cand_line.intersects(start_pnt):
                # on line
                feature['properties']['link_start'].append(candidate['id'])
                candidate['properties']['link_loc'].append(start_pnt.coords[0])

                if start_pnt.coords not in cand_line.vertexes:
                    # add vertex to line
                    cand_line = cand_line.add_vertex_at_point(start_pnt)
                    candidate['geometry']['coordinates'] = cand_line.coordinates

            if cand_line.intersects(end_pnt):
                feature['properties']['link_end'].append(candidate['id'])
                candidate['properties']['link_loc'].append(end_pnt.coords[0])

                if end_pnt.coords not in cand_line.vertexes:
                    # add vertex to line
                    cand_line = cand_line.add_vertex_at_point(end_pnt)
                    candidate['geometry']['coordinates'] = cand_line.coordinates

    # del cand_line, candidate, start_line, start_pnt

    if split_line_at_connection:
        output_lines = MemCollection()
        for feature in lines:

            line = tshape(feature['geometry'])

            # sort split_points on distance:
            split_points = sorted(feature['properties']['link_loc'],
                                  key=lambda loc: line.project(Point(loc)))

            start_vertex = 0
            nr = None
            for i, split_point in enumerate(split_points):
                end_vertex = feature['geometry']['coordinates'].index(split_point)
                line_part = {
                    'geometry': {
                        'type': feature['geometry']['type'],
                        'coordinates': feature['geometry']['coordinates'][start_vertex:end_vertex+1]},
                    'properties': copy(feature['properties'])
                }
                line_part['properties']['part'] = i
                output_lines.write(line_part)
                start_vertex = end_vertex
                nr = i + 1

            # last part
            line_part = {
                'geometry': {
                    'type': feature['geometry']['type'],
                    'coordinates': feature['geometry']['coordinates'][start_vertex:]},
                'properties': copy(feature['properties'])
            }
            line_part['properties']['part'] = nr
            output_lines.write(line_part)

        return output_lines

    return lines

    # check if line crosses other line
    # if line.crosses(candidate):
    #     pass
    #
    # # check of line crosses or touches other line when extended, with and without angle
    # if extend_with_angle_degrees is None:
    #     if extend_line_start.crosses(cand_line):
    #         pass
    #     elif extend_line_start.touches(cand_line):
    #         pass
    #
    #     if extend_line_end.crosses(cand_line):
    #         pass
    #     elif extend_line_end.touches(cand_line):
    #         pass
