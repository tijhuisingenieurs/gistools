from shapely.geometry import shape, Point, LineString, MultiLineString

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine, TMultiLineString


def get_haakselijnen_on_points_on_line(line_col, point_col, copy_fields=list(),
                                       default_length=15.0, length_field=None):
    """ returns MemCollection with perpendicular lines at given points on line
    with specific logic"""

    haakselijn_col = MemCollection(geometry_type='LineString')

    for feature in line_col:
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])        

        length = feature['properties'].get(length_field, default_length)

        for p in point_col.filter(bbox=line.bounds):
                
            if line.almost_intersect_with_point(Point(p['geometry']['coordinates'])):
                props = {}
                for field in copy_fields:
                    props[field] = p['properties'].get(field, None)
                
                haakselijn_col.writerecords([
                    {'geometry': {'type': 'LineString', 
                                  'coordinates': line.get_haakselijn_point(Point(p['geometry']['coordinates']),
                                                                           length)},
                     'properties': props}])

    return haakselijn_col


def flip_lines(collection):
    """ returns MemCollection with flipped lines"""    
    
    for feature in collection:
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
            check = 'Tline'
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])     
            check = 'TMultiLineString'
        
        flipped_line = line.get_flipped_line()

        feature['geometry']['coordinates'] = flipped_line
            
    return collection
