import logging
import random
from math import floor

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine, TMultiLineString
from shapely.geometry import shape

# from utils.arcgis_logging import setup_logging

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
                       default_distance=100.0, min_default_offset_start=0.0,
                       distance_field=None, min_offset_start_field=None, 
                       use_rest=True):
    """ returns MemCollection with points on line with special logic"""

    point_col = MemCollection(geometry_type='Point')

    for feature in line_col.filter():
        if type(feature['geometry']['coordinates'][0][0]) != tuple:
            line = TLine(feature['geometry']['coordinates'])
        else:
            line = TMultiLineString(feature['geometry']['coordinates'])

        props = {}
        for field in copy_fields:
            props[field] = feature['properties'].get(field, None)

        # afstand en offset bepalen
        distance = float(feature['properties'].get(distance_field, default_distance))
        # round distance down to 2 decimals to get correct nr of points later on
        distance = floor(distance * 100) / 100
        offset_start = float(feature['properties'].get(min_offset_start_field, min_default_offset_start))
        
        if distance > 0:
            # afspraak: offset alleen van toepassing indien kleiner dan 0.5 * distance
            if offset_start >= 0.5 * distance:
                offset_start = 0
    
            # aantal benodigde profielen bepalen
            nr_full = line.length // distance
            rest_lengte = line.length % distance
            rest_lengte_offset = (line.length - offset_start) % distance
            if rest_lengte_offset == rest_lengte:
                rest_lengte_offset = 0
            
            nr = nr_full
            
            # indien extra punt nodig is op de restlengte
            if use_rest is True:
                
                # Maximaal 10% overschrijding van vereiste onderlinge afstand, anders
                # een extra punt nodig
                if rest_lengte >= 0.1 * distance:
                    nr = nr + 1
        
                # Bij gebruik offset nog een extra p indien nodig
                if offset_start > 0 and rest_lengte_offset > 0.5 * distance:
                    nr = nr + 1                   
                         
            # slechts 1 punt indien lijn korter dan vereiste onderlinge afstand      
            if line.length < distance:
                nr = 1
                    
            for i in range(0, int(nr)):
                if i == int(nr_full):           
                    # todo: hoe om te gaan met het laatste punt
                    if rest_lengte == 0 and rest_lengte_offset == 0:
                        # als het precies past
                        if offset_start > 0:
                            dist = offset_start + (i * distance)
                        else:
                            dist = (0.5 + i) * distance
                    elif rest_lengte < 0.1 * distance and rest_lengte_offset > 0:
                        # als de offset ervoor zorgt dat de 10% norm mogelijk 
                        # alsnog wordt overschreden (meer niet gegarandeerd)
                        # TODO: kijken of dit nog netter uitgewerkt kan worden
                        dist = line.length - 0.5 * rest_lengte_offset     
                    elif rest_lengte_offset > 0 and line.length > distance:
                        # als de restlengte meer dan 10% overschrijding van de 
                        # afstand bedraagt en extra wordt beinvloed door de offset
                        dist = line.length - 0.5 * (rest_lengte + distance - offset_start)
                    else:
                        # als er maar 1 punt te genereren is, of de restlengte
                        # meer dan 10% overschrijding van de afstand bedraagt
                        dist = line.length - 0.5 * rest_lengte    
                        
                else:
                    if offset_start > 0:
                        # doortellen met veelvoud van afstand vanaf offset
                        dist = offset_start + (i * distance) 
                    else:
                        # doortellen met veelvoud van afstand vanaf 0.5 * afstand
                        dist = (0.5 + i) * distance 
    
                point_col.writerecords([
                    {'geometry': {'type': 'Point',
                                  'coordinates': line.get_point_at_distance(dist)},
                     'properties': props}])
        else:
            log.warning('Geen geldig afstand voor feature: ' + distance)
            
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
            log.warning('Geen geldig percentage voor feature: ' + percentage)
    
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
            log.warning('Geen geldig aantal voor feature: ' + aantal)
            
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
