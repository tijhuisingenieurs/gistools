from gistools.utils.collection import MemCollection
from shapely.geometry import Point, MultiLineString, LineString


def snap_points_to_line(line_col, points_col, tolerance=0.01, keep_unsnapped_points=True):
    snapped_points_col = MemCollection(geometry_type='Point')
    snapped_points_list = []

    for feature in points_col.filter():
        point = feature['geometry']['coordinates']
        bbox = (
            point[0] - tolerance,
            point[1] - tolerance,
            point[0] + tolerance,
            point[1] + tolerance
        )

        lines = line_col.filter(bbox=bbox)

        point_geom = Point(point)
        distance = tolerance * 2
        nearest_line = None

        for line in lines:
            if line['geometry']['type'].lower() == 'multilinestring':
                line_geom = MultiLineString(line['geometry']['coordinates'])
            else:
                line_geom = LineString(line['geometry']['coordinates'])

            new_distance = point_geom.distance(line_geom)
            if new_distance < distance:
                distance = new_distance
                nearest_line = line_geom

        if nearest_line is not None and distance <= tolerance:
            dist_on_line = nearest_line.project(point_geom)
            snapped_point = nearest_line.interpolate(dist_on_line)
            snapped_points_list.append(
                {'geometry': {'type': 'Point',
                              'coordinates': snapped_point.coords[0]},
                 'properties': feature['properties']}
            )

        elif keep_unsnapped_points:
            snapped_points_list.append(feature)

    snapped_points_col.writerecords(snapped_points_list)

    return snapped_points_col
