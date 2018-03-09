from shapely.geometry import MultiLineString, LineString
from gistools.utils.collection import MemCollection


def representative_length(line_col, profile_col):
    """ creates a MemCollection with a line geometry, attributes copied from the input profile file,
        and three added fields for the representative length: pre length, post length and total
        representative length.

        receives two line input files:
        - line shape representing the waterways
        - line shape representing the profiles

        returns MemCollection profile_col with the representative length data added
        """

    # Initialising prof_pk; a unique identifier for each profile
    prof_pk = 0

    # Loop through each line and select the profiles that intersect the line
    for feature in line_col:
        # Initialize the collections
        points_col = MemCollection(geometry_type='Point')
        sorted_col = MemCollection(geometry_type='Point')

        # Check if line is LineString or MultiLineString and create the appropiate line object
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = LineString(feature['geometry']['coordinates'])
        else:
            line = MultiLineString(feature['geometry']['coordinates'])

        # Loop through the profiles within the bounding box of the line
        for profile in profile_col.filter(bbox=line.bounds, precision=10**-6):
            if type(profile['geometry']['coordinates'][0][0]) != tuple:
                prof = LineString(profile['geometry']['coordinates'])
            else:
                prof = MultiLineString(profile['geometry']['coordinates'])

            # Making an intersection of the profile with the line creates a point
            x = line.intersection(prof)

            # If the profile has an intersect with the line, and thus a point is created, a unique prof_pk is assigned
            # to the profile, distance from the beginning of the line to the point is calculated, and it is added to
            # the points collection.
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

        # After all profiles on a line are defined, sort them by distance so that they are in order
        sorted_list = sorted(points_col.keys(), key=lambda x: (points_col[x]['properties']['distance']))

        # Write the sorted points to another collection (sorted_col)
        for i in sorted_list:
            p = points_col[i]
            props = p['properties']
            coords = p['geometry']['coordinates']

            sorted_col.writerecords([
                {'geometry': {'type': 'Point',
                              'coordinates': coords},
                 'properties': props}])

        # Loop again through the points to calculate the representative length variables. Four different situations
        # are treated: only one point on the line, the first point on the line, the last point on the line, and
        # points in between other points
        for i in range(len(sorted_col)):
            distance = sorted_col[i]['properties']['distance']
            if len(sorted_col) == 1:
                post_length = line.length - distance
                sorted_col[i]['properties']['voor_lengte'] = distance
                sorted_col[i]['properties']['na_lengte'] = post_length
            elif i != len(sorted_col)-1:
                post_length = (sorted_col[i + 1]['properties']['distance'] - distance) / 2
                if i == 0:
                    sorted_col[i]['properties']['voor_lengte'] = distance
                else:
                    pre_length = (distance - sorted_col[i - 1]['properties']['distance']) / 2
                    sorted_col[i]['properties']['voor_lengte'] = pre_length
                sorted_col[i]['properties']['na_lengte'] = post_length
            else:
                pre_length = (distance - sorted_col[i - 1]['properties']['distance']) / 2
                post_length = line.length - distance
                sorted_col[i]['properties']['voor_lengte'] = pre_length
                sorted_col[i]['properties']['na_lengte'] = post_length

        # Using the unique prof_pk identifier, the representative length data is written in the properties of the
        # profile collection, after which this updated collection is returned.
        for profile in profile_col.filter(bbox=line.bounds, precision=10 ** -6):
            for point in sorted_col.filter(bbox=line.bounds, precision=10 ** -6):
                if profile['properties'].get('prof_pk') == point['properties']['prof_pk']:
                    total_length = point['properties']['voor_lengte'] + point['properties']['na_lengte']
                    profile['properties']['voor_leng'] = point['properties']['voor_lengte']
                    profile['properties']['na_leng'] = point['properties']['na_lengte']
                    profile['properties']['tot_leng'] = total_length

    return profile_col
