import json
from collection import MemCollection, OrderedDict
from gistools.utils.conversion_tools import get_float
from gistools.utils.iso8601 import parse_date

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


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
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

    for project_id, project in json_dict.items():
        # check of project ook inhoud heeft
        if len(project['measured_profiles']) == 0:
            continue

            # profielen in project nalopen
        for pro_pk, profile_ids in enumerate(project['measured_profiles']):

            ############################# profile #################################

            profile = project['measured_profiles'][profile_ids]
            prof = OrderedDict()

            prof['pk'] = pro_pk
            prof['ids'] = profile.get('ids', '')
            prof['project_id'] = project_id
            prof['opm'] = profile.get('remarks').replace('\n', '')

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

            for p in profile.get('profile_points'):
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
            prof['aantal_h'] = count_manual

            alt_accuracy_list = [a for a in alt_accuracy_list if a is not None]
            date_list = [a for a in date_list if a is not None]
            pole_list = [a for a in pole_list if a is not None]
            l1_list = [a for a in l1_list if a is not None]

            coordinates = [[0, 0], [0, 1]]

            #             if ttl is not None and ttr is not None:
            if ttl.get('rd_coordinates', None) is not None and ttr.get('rd_coordinates', None) is not None:
                # todo: verkorten of verlengen op basis van lengte
                coordinates = ([ttl['rd_coordinates'][0],
                                ttl['rd_coordinates'][1]],
                               [ttr['rd_coordinates'][0],
                                ttr['rd_coordinates'][1]])
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

            if len(pole_list) > 0:
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
            # todo: sort profile points
            for i, point in enumerate(profile['profile_points']):

                ############################# 22L en 22R #################################
                records_ttlr = []

                if point.get('code') in ['22L', '22R']:
                    tt = {}

                    tt['prof_pk'] = pro_pk
                    tt['ids'] = profile.get('ids', '')
                    tt['project_id'] = project_id

                    tt['code'] = point.get('code')
                    tt['afstand'] = get_float(point.get('distance'))
                    # tt['gps_width'] = ''
                    # tt['h_width'] = ''
                    tt['wpeil'] = prof['wpeil']
                    tt['wpeil_bron'] = prof['wpeil_bron']
                    tt['datum'] = prof['datum']

                    tt['z'] = point['rd_coordinates'][2]
                    tt['x_coord'] = point['rd_coordinates'][0]
                    tt['y_coord'] = point['rd_coordinates'][1]

                    records_ttlr.append({
                        'geometry': {'type': 'Point',
                                     'coordinates': (point['rd_coordinates'][0], point['rd_coordinates'][1])},
                        'properties': tt})

                ttlr_col.writerecords(records_ttlr)

                ############################# points #################################
                p = OrderedDict()

                p['project_id'] = project_id
                p['prof_pk'] = prof['pk']
                p['volgnr'] = i
                p['prof_ids'] = prof['ids']
                p['prof_wpeil'] = prof['wpeil']
                p['prof_opm'] = prof['opm']
                p['prof_hpeil'] = prof['hpeil']
                p['prof_lpeil'] = prof['lpeil']
                p['prof_rpeil'] = prof['rpeil']

                p['code'] = point.get('code')
                p['afstand'] = get_float(point.get('distance'))  # todo: herberekenen?
                p['afst_afw'] = get_float(point.get('distance_accuracy'))  # todo: herberekenen?
                p['afst_bron'] = point.get('distance_source')

                p['bk'] = get_float(point.get('upper_level'))
                p['bk_eenheid'] = point.get('upper_level_unit')
                p['bk_afw'] = get_float(point.get('upper_level_accuracy'))
                p['bk_bron'] = point.get('upper_level_source')

                p['ok'] = get_float(point.get('lower_level'))
                p['ok_eenheid'] = point.get('lower_level_unit')
                p['ok_afw'] = get_float(point.get('lower_level_accuracy'))
                p['ok_bron'] = point.get('lower_level_source')

                p['opm'] = point.get('remarks', '')

                # afgeleiden

                if p['bk_bron'] == 'gps':
                    p['_bk_nap'] = p['bk']
                    if prof['wpeil'] is not None and p['bk'] is not None:
                        p['_bk_tov_wp'] = int(round((prof['wpeil'] - p['bk']) * 100))
                    else:
                        p['_bk_tov_wp'] = None
                elif p['bk_bron'] == 'manual' and p['bk_eenheid'] == 'cm tov WP':
                    p['_bk_tov_wp'] = p['bk']
                    if prof['wpeil'] is not None and p['bk'] is not None:
                        p['_bk_nap'] = prof['wpeil'] - (p['bk'] / 100)
                    else:
                        p['_bk_nap'] = None
                else:
                    p['_bk_tov_wp'] = None
                    p['_bk_nap'] = None

                if p['ok_bron'] == 'gps':
                    p['_ok_nap'] = p['ok']
                    if prof['wpeil'] is not None and p['ok'] is not None:
                        p['_ok_tov_wp'] = int(round((prof['wpeil'] - p['ok']) * 100))
                    else:
                        p['_ok_tov_wp'] = None
                elif p['ok_bron'] == 'manual' and p['ok_eenheid'] == 'cm tov WP':
                    p['_ok_tov_wp'] = p['ok']
                    if prof['wpeil'] is not None and p['ok'] is not None:
                        p['_ok_nap'] = prof['wpeil'] - (p['ok'] / 100)
                    else:
                        p['_ok_nap'] = None
                elif p['ok_bron'] == '' and p['_bk_tov_wp'] is not None:
                    p['_ok_tov_wp'] = p['_bk_tov_wp']
                    p['_ok_nap'] = p['_bk_nap']
                else:
                    p['_ok_tov_wp'] = None
                    p['_ok_nap'] = None

                # Metadata

                p['datumtijd'] = point.get('datetime', '')
                p['method'] = point.get('method', '')

                p['stok_len'] = get_float(point.get('pole_length'))
                p['l1_len'] = get_float(point.get('l_one_length'))

                if type(point['rd_coordinates']) == list:
                    p['gps_rd_x'] = get_float(point['rd_coordinates'][0])
                    p['gps_rd_y'] = get_float(point['rd_coordinates'][1])
                    p['gps_rd_z'] = get_float(point['rd_coordinates'][2])
                    coordinates = (point['rd_coordinates'][0], point['rd_coordinates'][1])
                else:
                    p['gps_rd_x'] = None
                    p['gps_rd_y'] = None
                    p['gps_rd_z'] = None
                    coordinates = (0, 0)

                if type(point['wgs_coordinates']) == list:

                    p['gps_wgs_x'] = get_float(point['wgs_coordinates'][0])
                    p['gps_wgs_y'] = get_float(point['wgs_coordinates'][1])
                    p['gps_wgs_z'] = get_float(point['wgs_coordinates'][2])
                else:
                    p['gps_wgs_x'] = None
                    p['gps_wgs_y'] = None
                    p['gps_wgs_z'] = None

                p['gps_h_afw'] = get_float(point['accuracy'])
                p['gps_h_afw'] = get_float(point['altitude_accuracy'])

                point_col.writerecords([
                    {'geometry': {'type': 'Point',
                                  'coordinates': coordinates},
                     'properties': p}])

                log.warning('records toegevoegd %i', i + 1)

    # lever de collection met meetpunten en de dicts voor WDB terug
    return point_col, prof_col, ttlr_col
