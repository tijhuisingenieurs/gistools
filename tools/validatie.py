import logging
from shapely.geometry import Point, Polygon

from gistools.utils.collection import MemCollection, OrderedDict
from gistools.utils.geometry import TLine, TMultiLineString, tshape


log = logging.getLogger(__file__)


def get_angles(line_col):
    """ get angle of line in degrees, between start and endpoint of line
    North = 0 degrees, East = 90 degrees
    
    return; linecollection with extra property 'feature_angle'
    """
    
    for feature in line_col:
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])   

        feature['properties']['feature_angle'] = line.get_line_angle()
        test = feature['properties'].get('feature_angle')
        
    return line_col

def get_intersecting_segments(line_col1, line_col2):
    """ get line segments of line collection 1 at intersection with line collection 2
    line_col1 = collection 1, of which segments are selected
    line_col2 = collection 2, which determines which segments from collection 1 
    are selected by using intersection
    
    return line collection with segments from collection 1"""
    
    line_parts_col = MemCollection(geometry_type='Linestring')
    records = []
    i = 0

    for line2 in line_col2:        
        if type(line2['geometry']['coordinates'][0][0]) != tuple:
            line2_shape = TLine(line2['geometry']['coordinates'])
        else:
            line2_shape = TMultiLineString(line2['geometry']['coordinates']) 
         
        bbox_test = line2_shape.bounds
        
        for line1 in line_col1: 
          
            if type(line1['geometry']['coordinates'][0][0]) != tuple:
                line1_shape = TLine(line1['geometry']['coordinates'])
            else:
                line1_shape = TMultiLineString(line1['geometry']['coordinates']) 
             
            if line2_shape.intersects(line1_shape):
                                  
                intersect_point = line2_shape.intersection(line1_shape)
                
                if intersect_point.geom_type != 'Point':
                    message = 'Intersectie op meerdere plekken, boundingbox = ' + str(intersect_point.bounds)
                    log.warning(message)
                    message = 'Voor lijn 1 ' + str(line1['geometry']['coordinates']) + ' en lijn 2 '+ str(line2['geometry']['coordinates'])
                    log.warning(message)
                
                else:
                    i = i + 1 
                    l1_part = line1_shape.get_line_part_point(intersect_point)
                    l1_props = {} 
                    l1_props['name'] = line1['properties'].get('name')
                    l1_props['line_oid'] = line1['properties'].get('id')   
                                                          
                    records.append({'geometry': {'type': 'linestring',
                                         'coordinates': (l1_part[0][1], l1_part[1][1])},
                           'properties': l1_props})                        
                    
    line_parts_col.writerecords(records)
    
    return line_parts_col 


def get_global_intersect_angles(line_col1, line_col2):
    """ get angle of intersection in degrees, between two lines
    direction of lines from start to end point, not segment direction
    North = 0 degrees, East = 90 degrees
     
    return collection of intersection points, with a property containing
    the angle between the intersecting lines in the direction of the lines
    """
     
    point_col = MemCollection(geometry_type='Point')

    records = []
        
    line_col1_angles = get_angles(line_col1)
    line_col2_angles = get_angles(line_col2)
     
    for line1 in line_col1_angles:
        if type(line1['geometry']['coordinates'][0][0]) != tuple:
            line1_shape = TLine(line1['geometry']['coordinates'])
        else:
            line1_shape = TMultiLineString(line1['geometry']['coordinates']) 
         
        for line2 in line_col2_angles.filter(bbox=line1_shape.bounds, precision=10**-6):
            if type(line2['geometry']['coordinates'][0][0]) != tuple:
                line2_shape = TLine(line2['geometry']['coordinates'])
            else:
                line2_shape = TMultiLineString(line2['geometry']['coordinates']) 
             
            if line1_shape.intersects(line2_shape):
                 
                max_angle = max(line1['properties'].get('feature_angle'), 
                                line2['properties'].get('feature_angle'))
                min_angle = min(line1['properties'].get('feature_angle'), 
                                line2['properties'].get('feature_angle'))
                crossangle = max_angle - min_angle
                 
                intersect_point = line1_shape.intersection(line2_shape)
                
                if intersect_point.geom_type != 'Point':
                    message = 'Intersectie op meerdere plekken, boundingbox = ' + str(intersect_point.bounds)
                    log.warning(message)
                    message = 'Voor lijn ' + str(line1['geometry']['coordinates']) + ' en lijn '+ str(line2['geometry']['coordinates'])
                    log.warning(message)
                else:
                    props = {}        
                    props['crossangle'] = crossangle
                    
                    # todo: get id's from lines (as with clean tools)
                    log.info('..intersection ok..')
                    records.append({'geometry': {'type': 'Point',
                                         'coordinates': (intersect_point.x, intersect_point.y) },
        
                           'properties': props})
            
    point_col.writerecords(records)

    return point_col 


def get_local_intersect_angles(line_col1, line_col2):
    """ get angle of intersection in degrees, between two lines
    direction of lines from start to end point, not segment direction
    North = 0 degrees, East = 90 degrees
     
    return collection of intersection points, with a property containing
    the angle between the intersecting lines in the direction of the lines
    """
     
    point_col = MemCollection(geometry_type='Point')
    records = []

    line1_parts_col= get_intersecting_segments(line_col1,line_col2 )
    line2_parts_col= get_intersecting_segments(line_col2,line_col1 )

    
    point_col = get_global_intersect_angles(line1_parts_col,line2_parts_col)
    
    return point_col


def get_distance_point_to_contour(poly_col, point_col, poly_id_field):
    """ get distance of points to contour of polygons
    
    return pointcollection with distances. positive is inside polygon, 
    negative is outside polygon
    """
     
    records = []
              
    for feature in poly_col:
        if type(feature['geometry']['coordinates'][0][0]) != tuple: 
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TLine(feature['geometry']['coordinates'][0])
        
        contour_buffer = line.buffer(2.0)
        
        for p in point_col.filter(bbox=contour_buffer.bounds, precision=10**-6):
        
            if p in point_col.filter(bbox=line.bounds, precision=10**-6):
                log.info('Punt in polygon boundingbox')
                pnt = Point(p['geometry']['coordinates'])
                
                pnt_prj = line.project(pnt)
                pnt_on_contour = Point(line.get_point_at_distance(pnt_prj))
                
                afstand = pnt.distance(pnt_on_contour)
                afstand = round(afstand, 2)
                
                props = {}
                props['poly_id'] = feature['properties'].get(poly_id_field, None)
                props['afstand'] = afstand
                     
                records.append({'geometry': {'type': pnt.type,
                                             'coordinates': pnt.coords[0]},
                                             'properties': props})
        
            
            else:
                log.info('Punt buiten polygon boundingbox, binnen 2 meter buffer')
                pnt = Point(p['geometry']['coordinates'])
                
                pnt_prj = line.project(pnt)
                pnt_on_contour = Point(line.get_point_at_distance(pnt_prj))
                
                afstand = -pnt.distance(pnt_on_contour)
                afstand = round(afstand, 2)
                
                props = {}
                props['poly_id'] = feature['properties'].get(poly_id_field, None)
                props['afstand'] = afstand
                     
                records.append({'geometry': {'type': pnt.type,
                                             'coordinates': pnt.coords[0]},
                                             'properties': props})
            
            
    point_dist_col = MemCollection(geometry_type=pnt.type) 
    point_dist_col.writerecords(records)
            
    return point_dist_col
    
    