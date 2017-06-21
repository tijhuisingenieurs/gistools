import json
import csv
from shapely.geometry import (Point, MultiPoint, LineString, MultiLineString,
                              Polygon, MultiPolygon)
from collection import MemCollection, OrderedDict
from conversion_tool import get_float

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

def fielddata_to_memcollection(filename):
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
    
    json_data_col = MemCollection(geometry_type='MultiPoint')
    records = []
        
    # dicts voor genereren WDB tabellen
    project_dict = {}
    profile_dict = {}
    

    for project_id, project in enumerate(json_dict):
        # check of project ook inhoud heeft
        if len(json_dict[project]['measured_profiles']) > 0:
            project_dict[project_id] = project
            
            # profielen in project nalopen            
            for pro_id, profile in enumerate(json_dict[project]['measured_profiles']):
                profile_name = json_dict[project]['measured_profiles'][profile]['ids']

                profile_dict[pro_id] = {}
                profile_dict[pro_id]['profiel'] = profile_name
                profile_dict[pro_id]['project'] = project
                
                # meetpunten in profiele nalopen
                for i,p in enumerate(json_dict[project]['measured_profiles'][profile]['profile_points']):
                    
            
#                     test = json_dict[project]['measured_profiles'][profile]['profile_points'][i]['method']
                    if json_dict[project]['measured_profiles'][profile]['profile_points'][i]['method'] != 'handmatig':
                                              
                        # ken alle beschikbare attributen toe als properties
                        properties = {}
                        properties['pro_id'] = pro_id
                        properties['profiel'] = profile_name
                        properties['volgnr'] = i
                        properties['project'] = project
                        properties['z'] = p['rd_coordinates'][2]
                        properties['afstand'] = get_float(p['distance'])
                        keys = p.keys()
                        for key in keys:
                            properties[key] = p[key]
                    
                        # maak record aan voor punt
                        records.append({'geometry': {'type': 'Point',
                                        'coordinates': (p['rd_coordinates'][0], p['rd_coordinates'][1])},
                                        'properties': properties})
                        log.warning('records toegevoegd ' + str(i+1))
        
    json_data_col.writerecords(records)
    
    # lever de collection met meetpunten en de dicts voor WDB terug
    return json_data_col, project_dict, profile_dict, json_dict
    