import logging


from gistools.utils.collection import MemCollection, OrderedDict
from gistools.utils.conversion_tools import get_float
from gistools.utils.iso8601 import parse_date
from gistools.utils.json_handler import json_to_dict
from gistools.utils.geometry import TLine


log = logging.getLogger(__name__)


def create_fieldwork_output_shapes(line_col, point_col):
    """
    
    line_col (MemCollection): profile line collection 
    point_col (MemCollection): profile point collection
    return: tuple with:
    - corrected profile line collection, with points as vertexes
    - corrected profile point collection based on calculated point locations
    """

    #
    output_line_col = MemCollection(geometry_type='LineString')
    output_point_col = MemCollection(geometry_type='Point')

    for line in line_col:

        line_props = line['properties']
        
        l = {
            'pk': line_props['pk'],
            'ids': line_props['ids'],
            'project_id': line_props['project_id'],
            'proj_name': line_props.get('proj_name', ''),           
            'opm': line_props.get('opm', ''),
            'wpeil': round(get_float(line_props['wpeil']), 2),
            'datum': line_props.get('datum', ''),
            'breedte': round(get_float(line_props['breedte']), 2)
        }
        
        # replace default value -9999 for None
        if l['wpeil'] == -9999:
            l['wpeil'] = None


        if type(line['geometry']['coordinates'][0][0]) != tuple:
            line = TLine([line['geometry']['coordinates'][0], line['geometry']['coordinates'][-1]])
        else:
            line = TLine([line['geometry']['coordinates'][0][0],line['geometry']['coordinates'][-1][-1]])
        
        line = line.get_scaled_line_with_length(l['breedte'], 0.5)

        for point in point_col:
            if point['properties']['prof_ids'] == l['ids']:
    
                point_props = point['properties']
                afstand = round(get_float(point_props['afstand']),2)
    
                xy = line.get_projected_point_at_distance(afstand) # todo: check if values before and after are supported
               
                p = {
                    'prof_ids': point_props['prof_ids'],
                    'datum': l['datum'],
                    'code': point_props['code'],
                    'tekencode': point_props.get('tekencode', 999),                
                    'afstand': round(get_float(point_props['afstand']),2),
                    'x_coord': xy[0],
                    'y_coord': xy[1]                    
                }                             
                
                # indien alle hoogtes bekend, vul waarden in
                if point_props['_bk_wp'] == -9999:
                    point_props['_bk_wp'] = ''
                if point_props['_ok_wp'] == -9999:
                    point_props['_ok_wp'] = ''                

                if l['wpeil'] is not None:
                    if point_props['_bk_wp'] <> '' and point_props['_ok_wp'] <> '':
                        p['_bk_wp'] = round(get_float(point_props['_bk_wp']),2)
                        p['_bk_nap'] = round(get_float(l['wpeil']) - (get_float(point_props['_bk_wp']) / 100),2)
                        p['_ok_wp'] = round(get_float(point_props['_ok_wp']),2)
                        p['_ok_nap'] = round(get_float(l['wpeil']) - (get_float(point_props['_ok_wp']) / 100),2)               
                    
                    # indien _ok_wp onbekend, maar _bk_wp bekend, neem _bk_wp over en vul waarden in      
                    elif point_props['_ok_wp'] == '' and point_props['_bk_wp'] <> '':
                        p['_bk_wp'] = round(get_float(point_props['_bk_wp']),2)
                        p['_bk_nap'] = round(get_float(l['wpeil']) - (get_float(point_props['_bk_wp']) / 100),2)
                        p['_ok_wp'] = round(get_float(point_props['_bk_wp']), 2)
                        p['_ok_nap'] = round(get_float(l['wpeil']) - (p['_ok_wp'] / 100), 2)
                    
                    # indien _bk_wp onbekend, maar _ok_wp bekend, vul ok waarden in en probeer _bk_wp te vullen vanuit _bk_nap     
                    elif point_props['_bk_wp'] == '' and  point_props['_ok_wp'] <> '':
                        p['_ok_wp'] = round(get_float(point_props['_ok_wp']),2)
                        p['_ok_nap'] = round(get_float(l['wpeil']) - (get_float(point_props['_ok_wp']) / 100),2)
                        
                        if '_bk_nap' in point_props and (point_props['_bk_nap'] <> '-9999' 
                                                         and point_props['_bk_nap'] <> '' 
                                                         and point_props['_bk_nap'] is not None):
                            p['_bk_wp'] = round(get_float(l['wpeil']) - get_float(point_props['_bk_nap']), 2)
                            p['_bk_nap'] = round(get_float(l['wpeil']) - (p['_bk_wp'] / 100), 2)
                        elif 'bk' in point_props and point_props['bk'] <> '' and point_props['bk'] is not None:
                            if point_props['bk_bron'] == 'manual':
                                p['_bk_wp'] = get_float(point_props['bk'])
                                p['_bk_nap'] = round(get_float(l['wpeil']) - (get_float(p['_bk_wp']) / 100),2)
                            elif point_props['bk_bron'] == 'gps':
                                p['_bk_nap'] = get_float(point_props['bk'])
                                p['_bk_wp'] = round((get_float(l['wpeil']) - (get_float(p['_bk_nap'])) * 100),2)
                                
                        else:
                            log.warning('Geen geldige waarde voor _bk_wp te bepalen. _bk_wp = ' 
                                        + str(point_props['_bk_wp']) + ' en bk en bk_nap niet aanwezig')
                            p['_bk_wp'] = point_props['_bk_wp']
                            p['_bk_nap'] = ''
                            
                    else:
                        log.warning('Geen geldige waarde voor ok_wp te bepalen. ok_wp = ' 
                                    + point_props['_ok_wp'] + ' en _bk_wp = ' + 
                                    point_props['_bk_wp'])
                        p['_bk_wp'] = point_props['_bk_wp']
                        p['_bk_nap'] = ''
                        p['_ok_wp'] = point_props['_ok_wp']
                        p['_ok_nap'] = ''                        
                
                else:
                    log.warning('Geen geldig waterpeil om dieptes mee te berekenen')
                    p['_bk_wp'] = point_props.get('_bk_wp', None)
                    p['_bk_nap'] = point_props.get('_bk_nap', None)
                    p['_ok_wp'] = point_props.get('_ok_wp', None)
                    p['_ok_nap'] = point_props.get('_ok_nap', None) 
                        
                output_point_col.writerecords([{
                    'geometry': {
                        'type': 'Point',
                        'coordinates': xy
                    },
                    'properties': p
                }])

        l['xb_prof'] = line.coords[0][0]
        l['yb_prof'] = line.coords[0][1]

        l['xe_prof'] = line.coords[-1][0]
        l['ye_prof'] = line.coords[-1][1]

        output_line_col.writerecords([{
            'geometry': {
                'type': 'LineString',
                'coordinates': line.coordinates
            },
            'properties': l
        }])

    return output_line_col, output_point_col






