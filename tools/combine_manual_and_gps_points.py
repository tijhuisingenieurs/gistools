"""Tool voor Iris voor het combineren van metingen uit Excel en GPS punten"""
import xlrd
from math import sqrt


def get_distance(p, q):
    return sqrt((float(p['x']) - float(q['x']))**2 + (float(p['y']) - float(q['y']))**2)


def get_projected_point(ttl, ttr, distance):
    ttl_ttr_distance = get_distance(ttl, ttr)
    if ttl_ttr_distance == 0.0:
        print('afstand is 0 tussen 22l en 22r')

    x = (float(ttr['x']) - float(ttl['x'])) * (float(distance) / ttl_ttr_distance) + float(ttl['x'])
    y = (float(ttr['y']) - float(ttl['y'])) * (float(distance) / ttl_ttr_distance) + float(ttl['y'])

    return {'x': x, 'y': y}


class CombineMeasurements(object):

    def __init__(self):
        pass

    def read_natte_profiel_punten(self, file_path):

        profile_data = []

        wb = xlrd.open_workbook(file_path)

        sheet = wb.sheets()[0]

        for record_nr in range(sheet.nrows/3):
            row = (record_nr) * 3
            if sheet.cell_type(row, 0) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                profile = {
                    'id': int(sheet.cell(row, 0).value),
                    'ref_level': round(float(sheet.cell(row, 1).value), 2),
                    'wet_points': []
                }
                for col in range(2, sheet.ncols):
                    if sheet.cell_type(row, col) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                        break
                    val = sheet.cell(row, col)
                    profile['wet_points'].append({
                        'distance': round(float(sheet.cell(row, col).value), 2),
                        'bk': int(sheet.cell(row + 1, col).value),
                        'ok': int(sheet.cell(row + 2, col).value),
                    })
                profile_data.append(profile)

        return profile_data

    def read_gps_punten(self, file_path):

        profile_data = []

        wb = xlrd.open_workbook(file_path)

        sheet = wb.sheets()[0]

        for row in range(1, sheet.nrows):

            if sheet.cell_type(row, 0) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                profile = {
                    'id': int(sheet.cell(row, 0).value),
                    'zijde': sheet.cell(row, 1).value,
                    'pnt_soort': int(sheet.cell(row, 2).value),
                    'x': round(float(sheet.cell(row, 3).value), 4),
                    'y': round(float(sheet.cell(row, 4).value), 4),
                    'z': round(float(sheet.cell(row, 5).value), 4),
                    'code': sheet.cell(row, 6).value,
                }

                profile_data.append(profile)

        return profile_data

    def combine(self, wet_profile, gps_points):
        messages = []

        points = []

        # map gps_points
        gps_dict = {}

        for gps_point in gps_points:
            if gps_point['id'] not in gps_dict:
                gps_dict[gps_point['id']] = {
                    'L': [],
                    'R': []
                }
            gps_dict[gps_point['id']][gps_point['zijde']].append(gps_point)

        for profile in wet_profile:
            output_profile = []

            # fist do left embankment
            left_points = gps_dict[profile['id']]['L']

            ttl = [point for point in left_points if point['code'] == '22L']

            if len(ttl) == 0:
                print('Missing 22L point for %i' % profile['id'])
                ttl = None
            else:
                ttl = ttl[0]
                for point in left_points:
                    if point['code'] == '22L':
                        continue

                    output_profile.append({
                        'type': point['code'],
                        'x': point['x'],
                        'y': point['y'],
                        'z': point['z'],
                        'code': 'dp',
                        'profiel': format(point['id'], '04d'),
                        'distance': -1 * get_distance(point, ttl)
                    })
                output_profile.sort(key=lambda p: p['distance'])

            right_points = gps_dict[profile['id']]['R']

            prof_width = profile['wet_points'][-1]['distance']
            ttr = [point for point in right_points if point['code'] == '22R']

            if len(ttr) == 0:
                ttr = None
            else:
                ttr = ttr[0]

            if ttl is None and ttr is not None:
                # get point with maximal distance to 22R
                for point in right_points:
                    point['distance_ttr'] = get_distance(point, ttr)
                right_points.sort(key=lambda p: p['distance_ttr'])

                ttl = get_projected_point(ttr, right_points[-1], -1 * prof_width)
            elif ttr is None and ttl is not None:
                ttr = get_projected_point(
                    output_profile[0],
                    ttl,
                    prof_width - output_profile[0]['distance'])
            elif ttr is None and ttl is None:
                msg = 'Missing 22L and 22R point for %i' % profile['id']
                messages.append(msg)
                print(msg)
                continue

            right_points_output = []
            for point in right_points:
                if point['code'] == '22R':
                    continue
                distance = prof_width + get_distance(point, ttr)
                projected_point = get_projected_point(ttl, ttr, distance)
                right_points_output.append({
                    'type': point['code'],
                    'x': projected_point['x'],
                    'y': projected_point['y'],
                    'z': point['z'],
                    'code': 'dp',
                    'profiel': format(profile['id'], '04d'),
                    'distance': prof_width + get_distance(point, ttr)
                })
                right_points_output.sort(key=lambda p: p['distance'])

            point = profile['wet_points'][0]
            projected_point = get_projected_point(ttl, ttr, point['distance'])
            output_profile.append({
                'type': 'waterlijn',
                'x': projected_point['x'],
                'y': projected_point['y'],
                'z': profile['ref_level'] - (float(point['bk']) / 100),
                'code': 'dp',
                'profiel': format(profile['id'], '04d'),
                'distance': point['distance']
            })

            point = profile['wet_points'][1]
            projected_point = get_projected_point(ttl, ttr, point['distance'])
            output_profile.append({
                'type': 'bagger_en_vastebodem',
                'x': projected_point['x'],
                'y': projected_point['y'],
                'z': profile['ref_level'] - (float(point['bk']) / 100),
                'code': 'dp',
                'profiel': format(profile['id'], '04d'),
                'distance': point['distance']
            })

            for point in profile['wet_points'][2:-2]:
                projected_point = get_projected_point(ttl, ttr, point['distance'])

                output_profile.append({
                    'type': 'bagger',
                    'x': projected_point['x'],
                    'y': projected_point['y'],
                    'z': profile['ref_level'] - (float(point['bk']) / 100),
                    'code': 'dp',
                    'profiel': format(profile['id'], '04d'),
                    'distance': point['distance']
                })

                output_profile.append({
                    'type': 'vaste_bodem',
                    'x': projected_point['x'],
                    'y': projected_point['y'],
                    'z': profile['ref_level'] - (float(point['ok']) / 100),
                    'code': 'dp',
                    'profiel': format(profile['id'], '04d'),
                    'distance': point['distance']
                })

            point = profile['wet_points'][-2]
            projected_point = get_projected_point(ttl, ttr, point['distance'])
            output_profile.append({
                'type': 'bagger_en_vastebodem',
                'x': projected_point['x'],
                'y': projected_point['y'],
                'z': profile['ref_level'] - (float(point['bk']) / 100),
                'code': 'dp',
                'profiel': format(profile['id'], '04d'),
                'distance': point['distance']
            })

            point = profile['wet_points'][-1]
            projected_point = get_projected_point(ttl, ttr, point['distance'])
            output_profile.append({
                'type': 'waterlijn',
                'x': projected_point['x'],
                'y': projected_point['y'],
                'z': profile['ref_level'] - (float(point['bk']) / 100),
                'code': 'dp',
                'profiel': format(profile['id'], '04d'),
                'distance': point['distance']
            })

            output_profile.extend(right_points_output)

            for i, prof in enumerate(output_profile):
                prof['pnt_nr'] = i + 1

            points.extend(output_profile)

        return points, messages

    def run(self, wet_points_file_path, gps_points_file_path):

        wet_points = self.read_natte_profiel_punten(wet_points_file_path)
        gps_points = self.read_gps_punten(gps_points_file_path)

        return self.combine(wet_points, gps_points)
