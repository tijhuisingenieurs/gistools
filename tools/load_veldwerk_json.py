import logging
from math import sqrt

from gistools.utils.collection import MemCollection, OrderedDict
from gistools.utils.conversion_tools import get_float
from gistools.utils.iso8601 import parse_date
from gistools.utils.json_handler import json_to_dict
from gistools.utils.geometry import TLine

log = logging.getLogger(__name__)


def fielddata_to_memcollections(filename, profile_plan_col=None, profile_id_field='DWPcode'):
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
        
    profile_plan_col (MemCollection): MemCollection of fieldwork plan with
        planned locations of profile measurements. In case the location of the profile,
        based on the 22L and 22R points are not complete, the predefined location
        is taken.
        
    profiel_id_field: fieldname of field with profiel identification.
        Default value: 'DWPcode'

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

            max_99_breedte = 0.0

            for p in profile.get('profile_points'):
                code = p.get('code')
                method_list.append(p.get('method'))
                date = p.get('datetime')
                if date is not None:
                    date_list.append(parse_date(date))
                pole_list.append(get_float(p.get('pole_length')))
                l1_list.append(get_float(p.get('l_one_length')))

                if code == '1':
                    count_one += 1
                elif code == '22L':
                    count_ttl += 1
                    ttl = p
                elif code == '99':
                    if p.get('distance') != '':
                        max_99_breedte = max(max_99_breedte, get_float(p.get('distance'), -99))
                    count_nn += 1
                elif code == '22R':
                    count_ttr += 1
                    ttr = p
                elif code == '2':
                    count_two += 1
                if p.get('upper_level_source') == 'gps':
                    count_gps += 1
                    accuracy = get_float(p.get('upper_level_accuracy'))
                    alt_accuracy_list.append(accuracy)
                elif p.get('upper_level_source') == 'manual':
                    count_manual += 1
                if p.get('lower_level_source') == 'gps':
                    count_gps += 1
                    accuracy = get_float(p.get('lower_level_accuracy'))
                    alt_accuracy_list.append(accuracy)
                elif p.get('lower_level_source') == 'manual':
                    count_manual += 1

            prof['methode'] = ", ".join(set(method_list))

            prof['breedte'] = None
            prof['h_breedte'] = get_float(profile.get('width'))
            if prof['h_breedte'] == '':
                prof['h_breedte'] = None

            prof['gps_breed'] = None


            if  (len(ttl) > 0 and len(ttr) > 0 and 
                ttl['rd_coordinates'] <> '' and ttr['rd_coordinates'] <> ''):

                prof['gps_breed'] = sqrt(
                    (ttl['rd_coordinates'][0] - ttr['rd_coordinates'][0]) ** 2 +
                    (ttl['rd_coordinates'][1] - ttr['rd_coordinates'][1]) ** 2)

            prof['m99_breed'] = max_99_breedte  # breedte volgens 99 pnt

            if prof['h_breedte'] is not None:
                prof['breedte'] = prof['h_breedte']
            else:
                prof['breedte'] = max(prof['gps_breed'], prof['m99_breed'])

            prof['hpeil'] = get_float(profile.get('manual_ref_level', None))

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

            if (ttl.get('rd_coordinates', None) is not None and 
                ttl.get('rd_coordinates', None) <> '' and
                ttr.get('rd_coordinates', None) is not None and
                ttr.get('rd_coordinates', None) <> '') :
                coordinates = ([ttl['rd_coordinates'][0],
                                ttl['rd_coordinates'][1]],
                               [ttr['rd_coordinates'][0],
                                ttr['rd_coordinates'][1]])
                prof['geom_bron'] = '22L en 22R'
            elif profile_plan_col is not None:
                # todo: check if id is the correct field to look for profile id
                meet_prof = [p for p in profile_plan_col if p['properties'][profile_id_field] == prof['ids']]
                
                if len(meet_prof) > 0:
                    coordinates = meet_prof[0]['geometry']['coordinates']
                    prof['geom_bron'] = 'meetplan'
                else:
                    prof['geom_bron'] = '22L en/of 22R mist en geen profiel gevonden in meetplan shape'

            else:
                prof['geom_bron'] = '22L en/of 22R mist en geen meetplan shape opgegeven'

            line = TLine(coordinates)

            if prof['breedte'] is not None:
                line = line.get_line_with_length(prof['breedte'], 0.5)
            else:
                log.warning('profiel %s heeft geen breedte, lijn wordt niet geschaald', prof['ids'])

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

            prof_col.writerecords([
                {'geometry': {'type': 'LineString',
                              'coordinates': line.coordinates},
                 'properties': prof}])

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
                    
                    tt['breedte'] = prof['breedte']
                    tt['gps_breed'] = prof['gps_breed']
                    tt['h_breedte'] = prof['h_breedte']
                    tt['m99_breed'] = prof['m99_breed']                                                            

                    tt['wpeil'] = prof['wpeil']
                    tt['wpeil_bron'] = prof['wpeil_bron']
                    tt['datum'] = prof['datum']

                    if (point.get('rd_coordinates', None) is not None and 
                        point.get('rd_coordinates', None) <> '' ) :
                        tt['x_coord'] = point['rd_coordinates'][0]
                        tt['y_coord'] = point['rd_coordinates'][1]
                        tt['z'] = point['rd_coordinates'][2]
                    
                    elif profile_plan_col is not None:
                        meet_prof = [p for p in profile_plan_col if p['properties'][profile_id_field] == tt['ids']]
                    
                        if len(meet_prof) > 0:
                            if point.get('code') == '22L': 
                                tt['x_coord'] = meet_prof[0]['geometry']['coordinates'][0][0]
                                tt['y_coord'] = meet_prof[0]['geometry']['coordinates'][0][1]
                                tt['z'] = ''
                            if point.get('code') == '22R': 
                                tt['x_coord'] = meet_prof[0]['geometry']['coordinates'][-1][0]
                                tt['y_coord'] = meet_prof[0]['geometry']['coordinates'][-1][1]
                                tt['z'] = ''                        
                        else:
                            log.warning('Bij profiel %s mist 22L en/of 22R en is geen profiel gevonden in meetplan shape', prof['ids'])
                    else:
                        log.warning('Bij profiel %s mist 22L en/of 22R en er geen meetplan shape opgegeven', prof['ids'])      

                    if 'x_coord' in tt and 'y_coord' in tt:
                        records_ttlr.append({
                            'geometry': {'type': 'Point',
                                         'coordinates': (tt['x_coord'], tt['y_coord'])},
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
                p['afstand'] = get_float(point.get('distance'))
                p['afst_afw'] = get_float(point.get('distance_accuracy'))
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
                        p['_bk_wp'] = int(round((prof['wpeil'] - p['bk']) * 100))
                    else:
                        p['_bk_wp'] = None
                elif p['bk_bron'] == 'manual' and p['bk_eenheid'] == 'cm tov WP':
                    p['_bk_wp'] = p['bk']
                    if prof['wpeil'] is not None and p['bk'] is not None:
                        p['_bk_nap'] = prof['wpeil'] - (p['bk'] / 100)
                    else:
                        p['_bk_nap'] = None
                else:
                    p['_bk_wp'] = None
                    p['_bk_nap'] = None

                if p['ok_bron'] == 'gps':
                    p['_ok_nap'] = p['ok']
                    if prof['wpeil'] is not None and p['ok'] is not None:
                        p['_ok_wp'] = int(round((prof['wpeil'] - p['ok']) * 100))
                    else:
                        p['_ok_wp'] = None
                elif p['ok_bron'] == 'manual' and p['ok_eenheid'] == 'cm tov WP':
                    p['_ok_wp'] = p['ok']
                    if prof['wpeil'] is not None and p['ok'] is not None:
                        p['_ok_nap'] = prof['wpeil'] - (p['ok'] / 100)
                    else:
                        p['_ok_nap'] = None
                elif p['ok_bron'] == '' and p['_bk_wp'] is not None:
                    p['_ok_wp'] = p['_bk_wp']
                    p['_ok_nap'] = p['_bk_nap']
                else:
                    p['_ok_wp'] = None
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
                p['gps_z_afw'] = get_float(point['altitude_accuracy'])

                point_col.writerecords([
                    {'geometry': {'type': 'Point',
                                  'coordinates': coordinates},
                     'properties': p}])

                log.warning('records toegevoegd %i', i + 1)

    # lever de collection met meetpunten en de dicts voor WDB terug
    return point_col, prof_col, ttlr_col
