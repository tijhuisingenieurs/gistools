from shapely.geometry import Point, MultiLineString, LineString
from gistools.utils.collection import MemCollection, OrderedDict


def representative_length(line_col, profile_col):
    prof_pk = 0

    for feature in line_col:
        points_col = MemCollection(geometry_type='Point')

        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = LineString(feature['geometry']['coordinates'])
        else:
            line = MultiLineString(feature['geometry']['coordinates'])

        for profile in profile_col.filter(bbox=line.bounds, precision=10**-6):
            if type(profile['geometry']['coordinates'][0][0]) != tuple:
                prof = LineString(profile['geometry']['coordinates'])
            else:
                prof = MultiLineString(profile['geometry']['coordinates'])

            x = line.intersection(prof)

            if x:
                profile['properties']['prof_pk'] = prof_pk
                prof_pk += 1
                props = profile['properties'].copy()
                props['distance'] = line.project(x)
                points_col.writerecords([
                    {'geometry': {'type': 'Point',
                                  'coordinates': x.coords[0]},
                     'properties': props}]
                )

        for i in range(len(points_col)):
            distance = points_col[i]['properties']['distance']
            if len(points_col) == 1:
                post_length = line.length - distance
                points_col[i]['properties']['voor_lengte'] = distance
                points_col[i]['properties']['na_lengte'] = post_length
            elif i != len(points_col)-1:
                post_length = (points_col[i+1]['properties']['distance'] - distance)/2
                if i == 0:
                    points_col[i]['properties']['voor_lengte'] = distance
                else:
                    pre_length = (distance - points_col[i - 1]['properties']['distance']) / 2
                    points_col[i]['properties']['voor_lengte'] = pre_length
                points_col[i]['properties']['na_lengte'] = post_length
            else:
                pre_length = (distance - points_col[i - 1]['properties']['distance']) / 2
                post_length = line.length - distance
                points_col[i]['properties']['voor_lengte'] = pre_length
                points_col[i]['properties']['na_lengte'] = post_length

        for profile in profile_col.filter(bbox=line.bounds, precision=10 ** -6):
            for point in points_col.filter(bbox=line.bounds, precision=10 ** -6):
                if profile['properties'].get('prof_pk') == point['properties']['prof_pk']:
                    total_length = point['properties']['voor_lengte'] + point['properties']['na_lengte']
                    profile['properties']['voor_leng'] = point['properties']['voor_lengte']
                    profile['properties']['na_leng'] = point['properties']['na_lengte']
                    profile['properties']['tot_leng'] = total_length

    return profile_col
