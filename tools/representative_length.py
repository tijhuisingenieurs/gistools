from shapely.geometry import MultiLineString, LineString, MultiPoint, Point
from shapely.ops import split
from gistools.utils.collection import MemCollection


def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    # This is taken from shapely manual
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]


def split_line_with_distances(line, distance_list):
    """Splits a line string in several segments considering a list of distances.
    The distances are assumed to be in the order of appearance they have in the line string.
    """
    segments = []
    current_line = line
    for dist in distance_list:
        seg, current_line = cut(current_line, dist)
        segments.append(seg)
    segments.append(current_line)
    return segments


def representative_length(line_col, profile_col):
    """ creates a MemCollection with a line geometry, attributes copied from the input profile file,
        and three added fields for the representative length: pre length, post length and total
        representative length.

        receives two line input files:
        - line shape representing the waterways
        - line shape representing the profiles

        returns MemCollection profile_col with the representative length data added
        """

    # Initalize new line collection
    rep_lines_col = MemCollection(geometry_type='MultiLineString')

    # Loop through each line and select the profiles that intersect the line
    for feature in line_col:
        # Check if line is LineString or MultiLineString and create the appropiate line object
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = LineString(feature['geometry']['coordinates'])
        else:
            line = MultiLineString(feature['geometry']['coordinates'])

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

        # TODO: have line split between first two points, save first part in new collection,
        # replace old complete line with second part, repeat process.

        list_points = []
        list_distances = []

        # Loops again through the points to calculate the representative length variables. Four different situations
        # are treated: only one point on the line, the first point on the line, the last point on the line, and
        # points in between other points
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
                    list_distances.append(split_distance)
                    split_point = line.interpolate(split_distance)
                    list_points.append(split_point)
            else:
                point['voor_lengte'] = (distance - sorted_points[i - 1]['distance']) / 2
                split_distance = distance - ((distance - sorted_points[i - 1]['distance']) / 2)
                list_distances.append(split_distance)
                split_point = line.interpolate(split_distance)
                list_points.append(split_point)
                point['na_lengte'] = line.length - distance

        if list_points:
            # multi_points = MultiPoint(list_points)
            # split_line = split(line, multi_points)

            if line.geom_type == 'LineString':
                segments = split_line_with_distances(line, list_distances)
            else:
                segments = []


            for i, l in enumerate(segments):
                rep_lines_col.writerecords([
                    {'geometry': {'type': 'LineString',
                                  'coordinates': [p for p in reversed(l.coords)]},
                     'properties': feature['properties']}])
        else:
            rep_lines_col.writerecords([
                    {'geometry': {'type': 'LineString',
                                  'coordinates': [p for p in reversed(line.coords)]},
                     'properties': feature['properties']}])

        # The representative length data is written in the properties of the
        # profile collection, after which this updated profile collection is returned.
        for point in sorted_points:
            profile = point['profile']
            profile['properties']['voor_leng'] = point['voor_lengte']
            profile['properties']['na_leng'] = point['na_lengte']
            profile['properties']['tot_leng'] = point['voor_lengte'] + point['na_lengte']

    return profile_col, rep_lines_col
