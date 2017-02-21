from shapely.geometry import shape, Point, LineString, MultiLineString

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine, TMultiLineString


def get_haakselijnen_on_points_on_line(line_col, point_col, copy_fields=list(),
                                       default_length=15.0, length_field=None):
    """ returns MemCollection with perpendicular lines at given points on line
    with specific logic"""

    haakselijn_col = MemCollection(geometry_type='LineString')

    for feature in line_col.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])        

        length = feature['properties'].get(length_field, default_length)

        for p in point_col:
            props = {}
            for field in copy_fields:
                props[field] = p['properties'].get(field, None)
                
            if line.contains(Point(p['geometry']['coordinates'])):
                haakselijn_col.writerecords([
                    {'geometry': {'type': 'LineString', 
                                  'coordinates': line.get_haakselijn_point(Point(p['geometry']['coordinates']),
                                                                           length)},
                     'properties': props}])

    return haakselijn_col


def flip_lines(collection):
    """ returns MemCollection with flipped lines"""    
    
    for feature in collection.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])     
        
        line.get_flipped_line()
        
        line['geometry']['coordinates'] = l.coords
        
    return collection
