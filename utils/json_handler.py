import json
import csv
from shapely.geometry import (Point, MultiPoint, LineString, MultiLineString,
                              Polygon, MultiPolygon)
from collection import MemCollection, OrderedDict
# from conversion_tool import get_float
from utils.conversion_tools import get_float
from utils.iso8601 import parse_date

import logging
log = logging.getLogger(__name__)


def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def json_to_dict(filename):
    """ creates a dictionary with JSON content of JSON file
    
    receives JSON file with content to process
                      
    returns dictionary json_dict with content of JSON file
    """
    
    with open(filename) as data_file:    
        json_dict = json_load_byteified(data_file)
    
    return json_dict

def fielddata_to_memcollections(filename):
    """ creates a MemCollection with geometry and attributes of json file 
    with point data, as collected with Tijhuis Field App
    
    receives JSON file with content to process:
    - file is dict of projects
    - project is dict of project definitions, 
        amongst which 'measured_profiles'
    - measured_profiles is dict of profiles names
    - each profile name is dict of profile definitions,
        amongst which 'profile_points'
    - profile_points is list of dicts with profile point definitions, 
        amongst which 'rd_coordinates' and 'method'
                      
    returns MemCollection json_data_col with content of JSON file
    """
    
    json_dict = json_to_dict(filename)
    
    point_col = MemCollection(geometry_type='Point')
    prof_col = MemCollection(geometry_type='LineString')
    ttlr_col = MemCollection(geometry_type='Point')
    records = []
        
    # dicts voor genereren WDB tabellen
    output_point = []
    output_prof = []
    output_ttlr = []

    for project_id, project in json_dict.items():
        # check of project ook inhoud heeft
        if len(project['measured_profiles']) == 0:
            continue

        proj_output_point = []
        proj_output_prof = []
        proj_output_22lr = []

        # profielen in project nalopen
        for pro_pk, profile_ids in enumerate(project['measured_profiles']):

            ############################# profile #################################

            profile = project['measured_profiles'][profile_ids]
            prof = {}

            log = ''

            prof['pk'] = pro_pk
            prof['ids'] = profile.get('ids', '')
            prof['project_id'] = project_id
            prof['opm'] = profile.get('remarks')

            ttl = {}
            ttr = {}
            count_one = 0
            count_ttl = 0
            count_nn = 0
            count_ttr = 0
            count_two = 0

            count_gps = 0
            count_manual = 0
            alt_accuracy_list = []
            method_list = []
            date_list = []
            pole_list = []
            l1_list = []

            for p in profile.get('measured_profiles'):
                code = p.get('code')
                method_list.append(p.get('method'))
                date = p.get('datetime')
                if date is not None:
                    date_list.append(parse_date(date))
                pole_list.append(p.get('pole_length'))
                l1_list.append(p.get('l_one_length'))

                if code == '1':
                    count_one += 1
                elif code == '22L':
                    count_ttl += 1
                    ttl = p
                elif code == '99':
                    count_nn += 1
                elif code == '22R':
                    count_ttr += 1
                    ttr = p
                elif code == '2':
                    count_two += 1
                if p.get('upper_source') == 'gps':
                    count_gps += 1
                    accuracy = get_float(profile.get('upper_accuracy'))
                    alt_accuracy_list += accuracy
                elif p.get('upper_source') == 'manual':
                    count_manual += 1
                if p.get('lower_source') == 'gps':
                    count_gps += 1
                    accuracy = get_float(profile.get('upper_accuracy'))
                    alt_accuracy_list += accuracy
                elif p.get('lower_source') == 'manual':
                    count_manual += 1

            prof['hpeil'] = get_float(profile.get('reference_level', None))

            prof['lpeil'] = get_float(ttl.get('upper_level'))
            prof['lpeil_afw'] = get_float(ttl.get('upper_level_accuracy'))
            prof['rpeil'] = get_float(ttr.get('upper_level'))
            prof['rpeil_afw'] = get_float(ttr.get('upper_level_accuracy'))

            prof['wpeil'] = None
            if prof['hpeil'] is not None:
                prof['wpeil'] = prof['hpeil']
                prof['wpeil_bron'] = 'manual'
            elif prof['lpeil'] is not None and prof['rpeil'] is not None:
                prof['wpeil'] = (prof['lpeil'] + prof['rpeil']) / 2
                prof['wpeil_bron'] = '22L en 22R'
            elif prof['lpeil'] is not None:
                prof['wpeil'] = prof['lpeil']
                prof['wpeil_bron'] = '22L'
            elif prof['rpeil'] is not None:
                prof['wpeil'] = prof['rpeil']
                prof['wpeil_bron'] = '22R'
            else:
                prof['wpeil_bron'] = '-'

            prof['aantal_1'] = count_one
            prof['aantal_22L'] = count_ttl
            prof['aantal_99'] = count_nn
            prof['aantal_22R'] = count_ttr
            prof['aantal_2'] = count_two

            prof['aantal_gps'] = count_gps
            prof['aantal_hand'] = count_manual

            alt_accuracy_list = [a for a in alt_accuracy_list if a is not None]
            date_list = [a for a in date_list if a is not None]
            pole_list = [a for a in pole_list if a is not None]
            l1_list = [a for a in l1_list if a is not None]

            coordinates = [[0,0],[0,1]]

            if ttl is not None and ttr is not None:
                coordinates = [[ttl['rds_coordinates'][0],
                                ttl['rds_coordinates'][1]],
                               [ttr['rds_coordinates'][0],
                                ttr['rds_coordinates'][1]]]
                prof['geom_bron'] = '22L en 22R'
            else:
                prof['geom_bron'] = 'todo: uit plan'
                # todo; haal uit plan als deze niet gemaakt kan worden op basis van 22L en 22R
                pass



            prof_col.writerecords([
                {'geometry': {'type': 'LineString',
                              'coordinates': coordinates},
                 'properties': prof}])

            if len(alt_accuracy_list) > 0:
                prof['min_z_afw'] = min(alt_accuracy_list)
                prof['gem_z_afw'] = reduce(lambda x, y: x + y, alt_accuracy_list) / len(alt_accuracy_list)
                prof['max_z_afw'] = max(alt_accuracy_list)
            else:
                prof['min_z_afw'] = None
                prof['gem_z_afw'] = None
                prof['max_z_afw'] = None

            if len(date_list) > 0:
                prof['datum'] = date_list[0].strftime('%d/%m/%Y')
                prof['min_datumt'] = min(date_list).isoformat()
                prof['max_datumt'] = max(date_list).isoformat()
            else:
                prof['datum'] = None
                prof['min_datumt'] = None
                prof['max_datumt'] = None

            if len(pole_list ) > 0:
                prof['min_stok'] = min(pole_list)
                prof['max_stok'] = max(pole_list)
            else:
                prof['min_stok'] = None
                prof['max_stok'] = None

            if len(l1_list) > 0:
                prof['min_l1_len'] = min(l1_list)
                prof['max_l1_len'] = max(l1_list)
            else:
                prof['min_l1_len'] = None
                prof['max_l1_len'] = None




                # meetpunten in profiele nalopen
            for i, point in enumerate(profile['profile_points']):

                ############################# 22L en 22R #################################
                if point.get('code') in ['22L', '22R']:
                    tt = {}

                    # todo

                    ttlr_col.writerecords([{
                        'geometry' : {

                        },
                        'props': tt
                    }])

                ############################# points #################################

#                     test = json_dict[project]['measured_profiles'][profile]['profile_points'][i]['method']
                if json_dict[project]['measured_profiles'][profile]['profile_points'][i]['method'] != 'handmatig':

                    # ken alle beschikbare attributen toe als properties
                    properties = {}
                    properties['pro_id'] = pro_id
                    properties['profiel'] = profile_name
                    properties['volgnr'] = i
                    properties['project'] = project
                    properties['z'] = p['rd_coordinates'][2]
#                         properties['afstand'] = get_float(p['distance'])
                    keys = p.keys()
                    for key in keys:
                        properties[key] = p[key]

                    # maak record aan voor punt
                    records.append({'geometry': {'type': 'Point',
                                    'coordinates': (p['rd_coordinates'][0], p['rd_coordinates'][1])},
                                    'properties': properties})
                    log.warning('records toegevoegd ' + str(i+1))
        
    # lever de collection met meetpunten en de dicts voor WDB terug
    return point_col, prof_col, ttlr_col
    