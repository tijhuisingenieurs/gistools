import numpy

from shapely.geometry import MultiLineString, LineString
from shapely.ops import split

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine, TMultiLineString


def representative_length(line_col, profile_col, id_field):
    """ creates a MemCollection with a line geometry, attributes copied from the input profile file,
        and three added fields for the representative length: pre length, post length and total
        representative length.

        receives two line input files:
        - line shape representing the waterways
        - line shape representing the profiles
        - id-field representing unique profile codes

        returns MemCollection profile_col with the representative length data added, and a MemCollection rep_lines_col
        with the lines based on the representative lengths
        """

    # Initalize new line collection for the split lines
    rep_lines_col = MemCollection(geometry_type='LineString')

    # Loop through each line and select the profiles that intersect the line
    for feature in line_col:
        # Check if line is LineString or MultiLineString and create the appropriate line object
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        # Initialize the list that collects the points that intersect with the line
        points = []

        # Loop through the profiles within the bounding box of the line
        for profile in profile_col.filter(bbox=line.bounds, precision=10**-6):
            if type(profile['geometry']['coordinates'][0][0]) != tuple:
                prof = LineString(profile['geometry']['coordinates'])
            else:
                prof = MultiLineString(profile['geometry']['coordinates'])

            # Making an intersection of the profile with the line creates a point
            x = line.intersection(prof)

            # If the profile has an intersect with the line, and thus a point is created,
            # distance from the beginning of the line to the point is calculated, and it is added to
            # the points collection. Also, references to the original profile and line are added.
            if x:
                points.append({
                    'coords': x.coords[0],
                    'distance': line.project(x),
                    'profile': profile,
                    'line': line
                })

        # After all profiles on a line are defined, sort them by distance so that they are in the correct order
        sorted_points = sorted(points, key=lambda x: x['distance'])

        # Initialize list of points on which the lines will be split
        list_points = []

        # Loops again through the points to calculate the representative length variables. Four different situations
        # are treated: only one point on the line, the first point on the line, the last point on the line, and
        # points in between other points. At the same time split points are being calculated and added to the list.
        for i, point in enumerate(sorted_points):
            distance = point['distance']
            if len(sorted_points) == 1:
                point['na_lengte'] = line.length - distance
                point['voor_lengte'] = distance
            elif i != len(sorted_points) - 1:
                point['na_lengte'] = (sorted_points[i + 1]['distance'] - distance) / 2
                if i == 0:
                    point['voor_lengte'] = distance
                else:
                    point['voor_lengte'] = (distance - sorted_points[i - 1]['distance']) / 2
                    split_distance = distance - ((distance - sorted_points[i - 1]['distance']) / 2)
                    split_point = line.interpolate(split_distance)
                    list_points.append(split_point)
            else:
                point['voor_lengte'] = (distance - sorted_points[i - 1]['distance']) / 2
                split_distance = distance - ((distance - sorted_points[i - 1]['distance']) / 2)
                split_point = line.interpolate(split_distance)
                list_points.append(split_point)
                point['na_lengte'] = line.length - distance

        # If split points are present, lines will be split. Otherwise the whole line will be added to the rep_lines_col
        if list_points:

            # Define the line used for splitting
            current_line = line

            # Loop through the split points and define perpendicular lines to ensure splitting
            for j, point in enumerate(list_points):
                haaks = LineString(line.get_haakselijn_point(point, 0.001))
                split_line = split(current_line, haaks)

                # Initialize line parts (used to store the part of the line that belongs to the profile); also
                # initialize current parts, a list used to store the remaining parts of the line (that potentially need
                # to be split further. Also define the representative length per profile (distance_point). The total
                # distance of the line parts should correspond to this length.
                line_parts = []
                current_parts = []
                total_distance = 0
                distance_point = sorted_points[j]['voor_lengte'] + sorted_points[j]['na_lengte']

                # Loop through the line parts: in case of multilinestrings the split function causes all parts of the
                # line to be converted into linestrings, also when they were not split. These need to be grouped back
                # and converted back into a multilinestring. To see which lines belong together, the total
                # representative length per profile is used.
                for k, part in enumerate(split_line):
                    total_distance += part.length
                    if total_distance < distance_point:
                        line_parts.append(part)
                    elif numpy.isclose(total_distance, distance_point, 0.0000005):
                        line_parts.append(part)
                    elif total_distance > distance_point:
                        current_parts.append(part)

                # Convert line parts to multilinestring, and redefine the current line
                segment = MultiLineString(line_parts)
                current_line = MultiLineString(current_parts)

                # Copy properties to avoid aliasing and set the profile id to which this line part belongs.
                # Also add total length and write this part to the rep_lines_col
                props = feature['properties'].copy()
                props[id_field] = sorted_points[j]['profile']['properties'][id_field]
                props['tot_leng'] = segment.length

                rep_lines_col.writerecords([
                    {'geometry': {'type': 'MultiLineString',
                                  'coordinates': [[p for p in reversed(l.coords)] for l in segment]},
                     'properties': props}])

                # If the split point was the last to be treated, also add the remaining part of the line to the
                # last profile.
                if j == (len(list_points) - 1):
                    props = feature['properties'].copy()
                    props[id_field] = sorted_points[j + 1]['profile']['properties'][id_field]
                    props['tot_leng'] = current_line.length

                    rep_lines_col.writerecords([
                        {'geometry': {'type': 'MultiLineString',
                                      'coordinates': [[p for p in reversed(l.coords)] for l in current_line]},
                         'properties': props}])

        else:
            props = feature['properties'].copy()
            props[id_field] = sorted_points[0]['profile']['properties'][id_field]
            props['tot_leng'] = line.length
            rep_lines_col.writerecords([
                    {'geometry': {'type': 'MultiLineString',
                                  'coordinates': [[p for p in reversed(l.coords)] for l in line]},
                     'properties': props}])

        # The representative length data is written in the properties of the
        # profile collection, after which this updated profile collection and the rep_lines_collection with the split
        # lines is returned.
        for point in sorted_points:
            profile = point['profile']
            profile['properties']['voor_leng'] = point['voor_lengte']
            profile['properties']['na_leng'] = point['na_lengte']
            profile['properties']['tot_leng'] = point['voor_lengte'] + point['na_lengte']

    return profile_col, rep_lines_col
