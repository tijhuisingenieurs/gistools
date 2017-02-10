from argparse import ArgumentError
import exceptions
from shapely.geometry import shape
from utils.collection import MemCollection
from utils.geometry import TLine, TMultiLineString


def get_start_endpoints(line_col, copy_fields=[]):
    """ returns MemCollection with start and end points of line"""

    point_col = MemCollection(geometry_type='Point')

    for feature in line_col.filter():
        line = shape(feature['geometry'])
        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        point_col.writerecords([
            {'geometry': {'type': 'Point', 'coordinates': line.coords[0]},
             'properties': props},
            {'geometry': {'type': 'Point', 'coordinates': line.coords[-1]},
             'properties': props}])

    return point_col


def get_midpoints(line_col, copy_fields=[]):
    """ returns MemCollection with midpoints"""

    point_col = MemCollection(geometry_type='Point')

    for feature in line_col.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': line.get_point_at_percentage(0.5)},
             'properties': props}])

    return point_col

def get_points_on_line(line_col, copy_fields=[],
                       default_distance=100.0, min_default_offset_start=0.0, min_default_offset_end=0.0,
                       distance_field=None, min_offset_start_field=None,
                       min_offset_end_field=None):
    """ returns MemCollection with points on line with special logic"""

    point_col = MemCollection(geometry_type='Point')

    for feature in line_col.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        offset_start = feature['properties'].get('min_offset_start_field', min_default_offset_start)
        offset_end = feature['properties'].get('min_offset_end_field', min_default_offset_end)
        distance = feature['properties'].get('distance_field', default_distance)

        nr_full = line.length // distance
        rest_lengte = line.length % distance

        if rest_lengte >= 0.5 * distance:
            nr = nr_full + 1
        else:
            nr = nr_full
        offset_max_length = line.length - offset_end

        for i in range(0, int(nr)):
            if i == int(nr_full):
                dist = line.length - 0.5 * rest_lengte
            else:
                dist = (0.5 + i) * distance

            dist = max(dist, offset_start)
            dist = min(dist, offset_max_length)

            point_col.writerecords([
                {'geometry': {'type': 'Point',
                              'coordinates': line.get_point_at_distance(dist)},
                 'properties': props}])

    return point_col