import logging
from shapely.geometry import Point

from gistools.utils.collection import MemCollection, OrderedDict
from gistools.utils.geometry import TLine, TMultiLineString, tshape
from gistools.utils.wit import vul_leggerwaarden, create_leggerpunten, update_leggerpunten_diepten

log = logging.getLogger(__file__)

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

        for p in point_col.filter(bbox=line.bounds, precision=10**-6):
            log.warning('filter')
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
        
    return line_col




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
                    records.append({'geometry': {'type': 'Point',
                                         'coordinates': (intersect_point.x, intersect_point.y) },
        
                           'properties': props})
            
    point_col.writerecords(records)

    return point_col 

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
    retun = line MemCollection with extra attribute"""
    
    records = []
    
    for feature in line_col:
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])   
              
        for p in point_col.filter(bbox=line.bounds, precision=10**-6):
            pnt = Point(p['geometry']['coordinates'])
    
            if line.almost_intersect_with_point(pnt):
                props = OrderedDict()
                props['line_id'] = p['properties'].get('line_id')
                props['volgnr'] = p['properties'].get('vertex_nr')
                 
                records.append({'geometry': {'type': line.type,
                                     'coordinates': line.coordinates},
                       'properties': props})
                
     
    indexed_line_col = MemCollection(geometry_type=line.type) 
    indexed_line_col.writerecords(records)
    
    return indexed_line_col
   