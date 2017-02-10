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
    """ returns MemCollection with start and end points of line"""

    point_col = MemCollection(geometry_type='Point')

    for feature in line_col.filter():
        try:
            line = TLine(feature['geometry']['coordinates'])
        except ValueError:
            line = TMultiLineString(feature['geometry'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        coord = line.get_point_at_percentage(0.5).coords[0]

        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': line.get_point_at_percentage(0.5)},
             'properties': props}])

    return point_col
