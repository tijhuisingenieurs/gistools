from collections import OrderedDict


def get_nearest_point(points, target_afstand, skip_codes=[], min_afstand=None, max_afstand=None):
    shortest_afstand = 99999.0
    nearest_point = None

    for point in points:
        if point['properties']['code'] in skip_codes:
            continue

        if min_afstand is not None and min_afstand >= point['properties']['afstand']:
            continue

        if max_afstand is not None and max_afstand <= point['properties']['afstand']:
            continue

        if abs(point['properties']['afstand'] - target_afstand) < shortest_afstand:
            shortest_afstand = abs(point['properties']['afstand'] - target_afstand)
            nearest_point = point

    return nearest_point


def update_profile_point_type(point_col, method):
    profiles = OrderedDict()

    # get unique profiles and all points
    for point in point_col:

        if point['properties']['prof_ids'] not in profiles:
            profiles[point['properties']['prof_ids']] = []

        profiles[point['properties']['prof_ids']].append(point)

    # analyse profiles
    for prof_ids, points in profiles.items():
        ttl = None
        ttr = None

        points = sorted(points, key=lambda x: x['properties']['afstand'])
        first_point = points[0]
        last_point = points[-1]

        for point in points:
            if point['properties']['code'] == '22L':
                ttl = point

            if point['properties']['code'] == '22R':
                ttr = point

        if ttl is None or ttr is None:
            continue

        width = ttr['properties']['afstand'] - ttl['properties']['afstand']

        mid_point = get_nearest_point(
            points,
            (ttl['properties']['afstand'] + ttr['properties']['afstand']) / 2,
            ['22L', '22R', '22'],
            ttl['properties']['afstand'],
            ttr['properties']['afstand'])

        if method == 'Fryslan':

            left_shore_nod_point = get_nearest_point(
                points,
                ttl['properties']['afstand'] - 0.5,
                ['22L', '22R', '22'],
                None,
                ttl['properties']['afstand'])

            right_shore_nod_point = get_nearest_point(
                points,
                ttr['properties']['afstand'] + 0.5,
                ['22L', '22R', '22'],
                ttr['properties']['afstand'])

            dist_from_tt = min(
                0.5,
                0.1 * width
            )

            left_wet_profile_nod_point = get_nearest_point(
                points,
                ttl['properties']['afstand'] + dist_from_tt,
                ['22L', '22R', '22'],
                ttl['properties']['afstand'],
                ttr['properties']['afstand'])

            right_wet_profile_nod_point = get_nearest_point(
                points,
                ttr['properties']['afstand'] - dist_from_tt,
                ['22L', '22R', '22'],
                ttl['properties']['afstand'],
                ttr['properties']['afstand'])

            for point in points:
                point['properties']['code_oud'] = point['properties']['code']

                if point['properties']['code'] not in ['22L', '22R', '22']:
                    point['properties']['code'] = '99'

            if mid_point is not None:
                mid_point['properties']['code'] = '7'

            if left_shore_nod_point is not None:
                left_shore_nod_point['properties']['code'] = '1'

            if right_shore_nod_point is not None:
                right_shore_nod_point['properties']['code'] = '2'

            if left_wet_profile_nod_point is not None:
                left_wet_profile_nod_point['properties']['code'] = '5'

            if right_wet_profile_nod_point is not None:
                right_wet_profile_nod_point['properties']['code'] = '6'

        elif method == 'Waternet':

            for point in points:
                point['properties']['code_oud'] = point['properties']['code']

                if point['properties']['code'] not in ['22L', '22R', '22']:

                    if point['properties']['afstand'] < ttl['properties']['afstand']:
                        point['properties']['code'] = '99'
                    elif (ttl['properties']['afstand'] <= point['properties']['afstand'] <=
                          mid_point['properties']['afstand']):
                        point['properties']['code'] = '5'
                    elif (mid_point['properties']['afstand'] < point['properties']['afstand'] <=
                          ttr['properties']['afstand']):
                        point['properties']['code'] = '6'
                    else:  # point['properties']['afstand'] >= ttr['properties']['afstand'])
                        point['properties']['code'] = '99'

            if first_point['properties']['code'] not in ['22L', '22R', '22']:
                first_point['properties']['code'] = '1'

            if mid_point['properties']['code'] not in ['22L', '22R', '22']:
                mid_point['properties']['code'] = '7'

            if last_point['properties']['code'] not in ['22L', '22R', '22']:
                last_point['properties']['code'] = '2'

    return point_col
