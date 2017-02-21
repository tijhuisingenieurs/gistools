from gistools.utils.collection import MemCollection
from gistools.utils.geometry import tshape


def get_end_points(lines, line_id_field='id', max_delta=0.01):

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
                      'properties': {'line_id': feature['properties'][line_id_field]}})
        # end_point
        points.write({'geometry': {'type': 'Point',
                                   'coordinates': p_end},
                      'properties': {'line_id': feature['properties'][line_id_field]}})

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
            for id in cluster_ids:
                x += points[id]['geometry']['coordinates'][0]
                y += points[id]['geometry']['coordinates'][1]

            x = x / len(cluster_ids)
            y = y / len(cluster_ids)

            line_ids = [str(points[id]['properties']['line_id']) for id in cluster_ids]

            point_sum.write({
                'geometry': {'type': 'Point',
                             'coordinates': (x, y)},
                'properties': {
                    'line_count': len(cluster_ids),
                    'line_ids': ','.join(line_ids)
                }
            })

    return point_sum
