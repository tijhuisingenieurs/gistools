import logging
import random
from math import floor

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine, TMultiLineString
from shapely.geometry import shape

# from utils.arcgis_logging import setup_logging
# TODO: Change name of the file? I think it does not correctly represent the functions inside it.

log = logging.getLogger(__file__)


def get_start_endpoints(line_col, copy_fields=list()):
    """ returns MemCollection with start and end points of line"""

    point_col = MemCollection(geometry_type='Point')

    for feature in line_col.filter():
        line = shape(feature['geometry'])
        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        point_col.writerecords([
            {'geometry': {'type': 'Point', 'coordinates': line.coords[0]},
             'properties': props},
            {'geometry': {'type': 'Point', 'coordinates': line.coords[-1]},
             'properties': props}])

    return point_col


def get_midpoints(line_col, copy_fields=list()):
    """ returns MemCollection with midpoints"""

    point_col = MemCollection(geometry_type='Point')

    for feature in line_col.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': line.get_point_at_percentage(0.5)},
             'properties': props}])

    return point_col


def get_points_on_line(line_col, copy_fields=list(),
                       fixed_distance=100.0,
                       distance_field=None,
                       max_repr_length=150,
                       rep_field=None,
                       all_lines=False):
    """ returns MemCollection with points on line with special logic"""

    point_col = MemCollection(geometry_type='Point')

    for feature in line_col.filter():
        rep_length = float(feature['properties'].get(rep_field, max_repr_length))

        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        # Calculate distance
        distance = float(feature['properties'].get(distance_field, fixed_distance))
        # round distance down to 2 decimals to get correct nr of points later on
        distance = floor(distance * 100) / 100

        # Calculate number of needed profiles
        nr = line.length // distance
        rest_length = line.length % distance

        # Max representative length cannot be exceeded, otherwise extra point is needed.
        if (rep_length < rest_length + distance) and line.length > distance:
            nr = nr + 1

        if line.length < distance and all_lines:
            dist = 0.5 * line.length

            point_col.writerecords([
                {'geometry': {'type': 'Point',
                              'coordinates': line.get_point_at_distance(dist)},
                 'properties': props}])

        for i in range(0, int(nr)):
            # if line length is smaller than the required distance: only one point
            if line.length < distance and all_lines:
                dist = 0.5 * line.length
            else:
                # doortellen met veelvoud van afstand vanaf 0.5 * afstand
                dist = (0.5 + i) * distance

            point_col.writerecords([
                {'geometry': {'type': 'Point',
                              'coordinates': line.get_point_at_distance(dist)},
                 'properties': props}])

    return point_col


def get_points_on_perc(line_col, copy_fields=list(), default_perc=10.0, perc_field=None):
    """ returns MemCollection with points on line at specified percentage"""
    
    point_col = MemCollection(geometry_type='Point')
    
    for feature in line_col.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        # afstand
        percentage = (float(feature['properties'].get(perc_field, default_perc))/100)
        # round percentage down to 2 decimals to get correct nr of points later on
        percentage = floor(percentage * 100) / 100
        
        if percentage > 0.0:
            # aantal benodigde profielen bepalen
            nr = int(1 / percentage)
        
            for i in range(0, int(nr)):
                perc = (i+1) * percentage

                point_col.writerecords([
                    {'geometry': {'type': 'Point',
                                  'coordinates': line.get_point_at_percentage(perc)},
                     'properties': props}])
        else:
            log.warning('Geen geldig percentage voor feature: %i', percentage)
    
    return point_col


def get_points_on_line_amount(line_col, copy_fields=list(), default_amount=10.0, amount_field=None):
    """ returns MemCollection with specified amount of points on line at equal distance"""
    
    point_col = MemCollection(geometry_type='Point')
        
    for feature in line_col.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        # afstand
        aantal = int(feature['properties'].get(amount_field, default_amount))
        if aantal > 0:
            distance = line.length / aantal
            # round distance down to 2 decimals to get correct nr of points later on
            distance = floor(distance * 100.0) / 100.0
    
            for i in range(0, int(aantal)):
                dist = (0.5 + i) * distance

                point_col.writerecords([
                    {'geometry': {'type': 'Point',
                                  'coordinates': line.get_point_at_distance(dist)},
                     'properties': props}])
        else:
            log.warning('Geen geldig aantal voor feature: ' + str(aantal))
            
    return point_col


def get_points_on_line_random(line_col, copy_fields=list(), default_offset=0.75, offset_field=None):
    """ returns MemCollection with specified amount of points on line at equal distance"""
    
    point_col = MemCollection(geometry_type='Point')
    
    for feature in line_col.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)
    
        # afstand bepalen
        offset = feature['properties'].get(offset_field, default_offset)
        if offset > line.length:
            offset = 0.25 * line.length
            
        random_afstand = random.uniform(offset, line.length - offset)

        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': line.get_point_at_distance(random_afstand)},
             'properties': props}])

    return point_col
