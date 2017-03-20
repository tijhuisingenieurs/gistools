from shapely.geometry import Point

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine, TMultiLineString
from gistools.utils.wit import vul_leggerwaarden, create_leggerpunten, update_leggerpunten_diepten


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
