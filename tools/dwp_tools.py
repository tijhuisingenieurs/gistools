import logging
from shapely.geometry import Point

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine, TMultiLineString
from gistools.utils.wit import vul_leggerwaarden, create_leggerpunten, update_leggerpunten_diepten

log = logging.getLogger(__file__)


def get_haakselijnen_on_points_on_line(line_col, point_col, copy_fields=list(),
                                       default_length=15.0, length_field=None, source="points"):
    """ returns MemCollection with perpendicular lines at given points on line
    with specific logic"""

    haakselijn_col = MemCollection(geometry_type='LineString')

    for feature in line_col:
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        if source == "lines":
            length = feature['properties'].get(length_field, default_length)

        for p in point_col.filter(bbox=line.bounds, precision=10**-6):
            log.warning('point within bbox line')
            if line.almost_intersect_with_point(Point(p['geometry']['coordinates'])):
                log.warning('found intersection')
                if source == "points":
                    length = p['properties'].get(length_field, default_length)
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
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])     
        
        flipped_line = line.get_flipped_line()

        feature['geometry']['coordinates'] = flipped_line
            
    return collection


def get_leggerprofiel(line_col):
    """ returns MemCollections with points for profile """
    
    records = [] 
    
    for feature in line_col:
        line_id = feature['properties'].get('line_id', None)
        name = feature['properties'].get('name', None)
        
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])     
    
        legger_col = {
            'waterpeil': feature['properties'].get('waterpeil', 0),
            'waterdiepte': feature['properties'].get('waterdiepte', 0),
            'breedte_wa': feature['properties'].get('breedte_wa', 0),
            'bodemhoogte': feature['properties'].get('bodemhoogte', 0),
            'bodembreedte': feature['properties'].get('bodembreedte', 0),
            'talud_l': feature['properties'].get('talud_l', 0),
            'talud_r': feature['properties'].get('talud_r', 0),
            'peiljaar': feature['properties'].get('peiljaar', 0)
        }

        # Berekenen leggerwaarden
        ti_velden_col = vul_leggerwaarden(legger_col)
    
        # Berekenen locatie leggerpunten
        profiel_dict = create_leggerpunten(line, line_id, name, ti_velden_col['ti_waterbr'],
                                           ti_velden_col['ti_talulbr'], ti_velden_col['ti_knkbodr'])
    
        # Berekenen waarden leggerpunten
        legger_point_dict = update_leggerpunten_diepten(profiel_dict, ti_velden_col)
        legger_point_dict['peiljaar'] = legger_col['peiljaar']
        
        legger_point_dict_22L = legger_point_dict.copy()
        legger_point_dict_22L['puntcode'] = 22
        legger_point_dict_22L['volgnr'] = 1
        legger_point_dict_22L['afstand'] = 0.0
        legger_point_dict_22L['z_waarde'] = legger_point_dict_22L['L22_peil']
        
        legger_point_dict_99L = legger_point_dict.copy()
        legger_point_dict_99L['puntcode'] = 99
        legger_point_dict_99L['volgnr'] = 2
        legger_point_dict_99L['afstand'] = legger_point_dict_99L['ti_talulbr']
        legger_point_dict_99L['z_waarde'] = legger_point_dict_99L['knik_l_dpt']
                
        legger_point_dict_99R = legger_point_dict.copy()
        legger_point_dict_99R['puntcode'] = 99
        legger_point_dict_99R['volgnr'] = 3
        legger_point_dict_99R['afstand'] = legger_point_dict_99R['ti_knkbodr']        
        legger_point_dict_99R['z_waarde'] = legger_point_dict_99R['knik_r_dpt']
                
        legger_point_dict_22R = legger_point_dict.copy()
        legger_point_dict_22R['puntcode'] = 22
        legger_point_dict_22R['volgnr'] = 4
        legger_point_dict_22R['afstand'] = legger_point_dict_22R['ti_waterbr']        
        legger_point_dict_22R['z_waarde'] = legger_point_dict_22R['R22_peil']
            
        # Vullen point collection voor deze lijn

        records.append({'geometry': {'type': 'Point',
                                     'coordinates': [(legger_point_dict['L22'][0], legger_point_dict['L22'][1])]},
                       'properties': legger_point_dict_22L})
        
        records.append({'geometry': {'type': 'Point',
                                     'coordinates': [(legger_point_dict['knik_l'][0], legger_point_dict['knik_l'][1])]},
                       'properties': legger_point_dict_99L})
        
        records.append({'geometry': {'type': 'Point',
                                     'coordinates': [(legger_point_dict['knik_r'][0], legger_point_dict['knik_r'][1])]},
                       'properties': legger_point_dict_99R})
        
        records.append({'geometry': {'type': 'Point',
                                     'coordinates': [(legger_point_dict['R22'][0], legger_point_dict['R22'][1])]},
                       'properties': legger_point_dict_22R})
    
    legger_point_col = MemCollection(geometry_type='Point') 
    legger_point_col.writerecords(records)
    
    return legger_point_col


# def get_angles(line_col):
#     """ get angle of line in degrees, between start and endpoint of line
#     North = 0 degrees, East = 90 degrees
#     
#     return; linecollection with extra property 'feature_angle'
#     """
#     
#     for feature in line_col:
#         if type(feature['geometry']['coordinates'][0][0]) != tuple:
#             line = TLine(feature['geometry']['coordinates'])
#         else:
#             line = TMultiLineString(feature['geometry']['coordinates'])   
# 
#         feature['properties']['feature_angle'] = line.get_line_angle()
#         test = feature['properties'].get('feature_angle')
#         
#     return line_col
# 
# 
# def get_intersecting_segments(line_col1, line_col2):
#     """ get line segments of line collection 1 at intersection with line collection 2
#     line_col1 = collection 1, of which segments are selected
#     line_col2 = collection 2, which determines which segments from collection 1 
#     are selected by using intersection
#     
#     return line collection with segments from collection 1"""
#     
#     line_parts_col = MemCollection(geometry_type='Linestring')
#     records = []
#     i = 0
# 
#     for line2 in line_col2:        
#         if type(line2['geometry']['coordinates'][0][0]) != tuple:
#             line2_shape = TLine(line2['geometry']['coordinates'])
#         else:
#             line2_shape = TMultiLineString(line2['geometry']['coordinates']) 
#          
#         bbox_test = line2_shape.bounds
#         
#         for line1 in line_col1: 
#           
#             if type(line1['geometry']['coordinates'][0][0]) != tuple:
#                 line1_shape = TLine(line1['geometry']['coordinates'])
#             else:
#                 line1_shape = TMultiLineString(line1['geometry']['coordinates']) 
#              
#             if line2_shape.intersects(line1_shape):
#                                   
#                 intersect_point = line2_shape.intersection(line1_shape)
#                 
#                 if intersect_point.geom_type != 'Point':
#                     message = 'Intersectie op meerdere plekken, boundingbox = ' + str(intersect_point.bounds)
#                     log.warning(message)
#                     message = 'Voor lijn 1 ' + str(line1['geometry']['coordinates']) + ' en lijn 2 '+
#                               str(line2['geometry']['coordinates'])
#                     log.warning(message)
#                 
#                 else:
#                     i = i + 1 
#                     l1_part = line1_shape.get_line_part_point(intersect_point)
#                     l1_props = {} 
#                     l1_props['name'] = line1['properties'].get('name')
#                     l1_props['line_oid'] = line1['properties'].get('id')
# #                     l1_props ['id'] = i     
#                                                           
#                     records.append({'geometry': {'type': 'linestring',
#                                          'coordinates': (l1_part[0][1], l1_part[1][1])},
#                            'properties': l1_props})                        
#                     
#     line_parts_col.writerecords(records)
#     
#     return line_parts_col 
# 
# 
# def get_global_intersect_angles(line_col1, line_col2):
#     """ get angle of intersection in degrees, between two lines
#     direction of lines from start to end point, not segment direction
#     North = 0 degrees, East = 90 degrees
#      
#     return collection of intersection points, with a property containing
#     the angle between the intersecting lines in the direction of the lines
#     """
#      
#     point_col = MemCollection(geometry_type='Point')
# 
#     records = []
#         
#     line_col1_angles = get_angles(line_col1)
#     line_col2_angles = get_angles(line_col2)
#      
#     for line1 in line_col1_angles:
#         if type(line1['geometry']['coordinates'][0][0]) != tuple:
#             line1_shape = TLine(line1['geometry']['coordinates'])
#         else:
#             line1_shape = TMultiLineString(line1['geometry']['coordinates']) 
#          
#         for line2 in line_col2_angles.filter(bbox=line1_shape.bounds, precision=10**-6):
#             if type(line2['geometry']['coordinates'][0][0]) != tuple:
#                 line2_shape = TLine(line2['geometry']['coordinates'])
#             else:
#                 line2_shape = TMultiLineString(line2['geometry']['coordinates']) 
#              
#             if line1_shape.intersects(line2_shape):
#                  
#                 max_angle = max(line1['properties'].get('feature_angle'), 
#                                 line2['properties'].get('feature_angle'))
#                 min_angle = min(line1['properties'].get('feature_angle'), 
#                                 line2['properties'].get('feature_angle'))
#                 crossangle = max_angle - min_angle
#                  
#                 intersect_point = line1_shape.intersection(line2_shape)
#                 
#                 if intersect_point.geom_type != 'Point':
#                     message = 'Intersectie op meerdere plekken, boundingbox = ' + str(intersect_point.bounds)
#                     log.warning(message)
#                     message = 'Voor lijn ' + str(line1['geometry']['coordinates']) + ' en lijn '+
#                                str(line2['geometry']['coordinates'])
#                     log.warning(message)
#                 else:
#                     props = {}        
#                     props['crossangle'] = crossangle
#                     
#                     # todo: get id's from lines (as with clean tools)
#                     log.info('..intersection ok..')
#                     records.append({'geometry': {'type': 'Point',
#                                          'coordinates': (intersect_point.x, intersect_point.y) },
#         
#                            'properties': props})
#             
#     point_col.writerecords(records)
# 
#     return point_col 
# 
# 
# def get_local_intersect_angles(line_col1, line_col2):
#     """ get angle of intersection in degrees, between two lines
#     direction of lines from start to end point, not segment direction
#     North = 0 degrees, East = 90 degrees
#      
#     return collection of intersection points, with a property containing
#     the angle between the intersecting lines in the direction of the lines
#     """
#      
#     point_col = MemCollection(geometry_type='Point')
#     records = []
# 
#     line1_parts_col= get_intersecting_segments(line_col1,line_col2 )
#     line2_parts_col= get_intersecting_segments(line_col2,line_col1 )
# 
#     
#     point_col = get_global_intersect_angles(line1_parts_col,line2_parts_col)
#     
#     return point_col

def get_vertices_with_index(line_col, id_field):
    """ get Point at each vertex on line, and assign index number
    
    input = line MemCollection
    return collection of points with line id and index number"""
    
    records = []
    
    for feature in line_col:
        coords = []
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            coords = feature['geometry']['coordinates']
        else:
            for part in feature['geometry']['coordinates']:
                for l in part:
                    coords.append(l)

        i = 0
        
        for p in coords:
            i = i + 1
            props = {}
            props['line_id'] = feature['properties'].get(id_field, None)
            props['vertex_nr'] = i          
            
            records.append({'geometry': {'type': 'Point',
                                         'coordinates': p},
                            'properties': props})
            
    point_col = MemCollection(geometry_type='Point') 
    point_col.writerecords(records)
    
    return point_col


def get_index_number_from_points(line_col, point_col, index_field):
    """ append index number from point as attribute to line
    
    input = line MemCollection to append index to
            point MemCollection with attribute with index number (index_field)
    return = line MemCollection with extra attribute"""
    
    records = []
    log.warning('Tool started')

    for feature in line_col:
        log.warning('feature found')
        message1 = 'feature: ' + str(feature['properties'].get('FID'))
        log.warning(message1)
        
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])   
              
        for p in point_col.filter(bbox=line.bounds, precision=10**-6):
            log.warning('point found in bbox')
            message2 = 'point: ' + str(p['properties'].get('vertex_nr'))
            log.warning(message2)
            
            pnt = Point(p['geometry']['coordinates'])
    
            if line.almost_intersect_with_point(pnt, decimals=2):
                log.warning('intersection found')
                message3 = 'feature ' + str(feature['properties'].get('FID')) + ' with vertex ' + \
                           str(p['properties'].get('vertex_nr'))
                log.warning(message3)  
                                                                                                  
                props = {}
                props['bronlijn'] = feature['properties'].get('FID', 999999)
                props['line_id'] = p['properties'].get('line_id')
                props['volgnr'] = p['properties'].get('vertex_nr')
                 
                records.append({'geometry': {'type': line.type,
                                             'coordinates': line.coordinates},
                                'properties': props})

    indexed_line_col = MemCollection(geometry_type=line.type) 
    indexed_line_col.writerecords(records)
    
    return indexed_line_col


def get_scaled_line(line_col, target_length_field, scale_point_perc=0):
    """get line with given line, with same direction and scalled
    around the scale point
        
    target_length_field: field with new length in shape units (float)
    scale_point_perc  (float): percentage (0-1) of point on line to relatively scale around
            0=begin of line, 1=end of line, 0.5 = halfway
    
    return = line MemCollection with new scaled lengths"""

    for feature in line_col:  
        
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])  
            
        target_length = feature['properties'].get(target_length_field, 0.0)
        if target_length == 0.0:
            scaled_line = line
        else:
            scaled_line = line.get_scaled_line_with_length(target_length, scale_point_perc)
        
        coordinates = []
        for p in scaled_line.coordinates:
            coordinates.append(p) 

        feature['geometry']['coordinates'] = coordinates
                
    return line_col


def get_extended_line(line_col, target_length_field, extend_point='end'):
    """get line with given line, with same direction and extended
    at extendpoint with given length
        
    target_length_field: field with new length in shape units (float)
    extend_point (text): point of line to extend
        values: 'begin', 'end', 'both'
    
    return = line MemCollection with new extended lengths"""

    for feature in line_col:  
        
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])  
            
        target_length = feature['properties'].get(target_length_field, 0.0)
        
        if target_length == 0.0:
            extended_line = line            
        else:
            extended_line = line.get_extended_line_with_length(target_length, extend_point)
        
        coordinates = []
        for p in extended_line.coordinates:
            coordinates.append(p) 

        feature['geometry']['coordinates'] = coordinates
                
    return line_col
