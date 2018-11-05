import os
import csv
import pandas as pd
import logging
import os.path
import sys
from shapely.geometry import Point, MultiLineString, LineString
import matplotlib.pyplot as plt
import arcpy

from utils.addresulttodisplay import add_result_to_display
from utils.arcgis_logging import setup_logging

from gistools.utils.collection import MemCollection

def GetProfielMiddelpunt(input_inpeil, input_uitpeil):
    ''' Deze functie maakt van de metingen een overzicht van de profielen in deze shape en een middelpunt.
     input: input_inpeil(shapefile), input_uitpeil(shapefile)
     return:
     pointcollection input inpeilingen, pointcollection input uitpeilingen,
     pointcollection middelpunten van de inpeilingen, pointcollection middelpunten van de uitpeilingen,
     list van de profielnamen van de inpeilingen, list van de profielnamen van de uitpeilingen'''

    # ---------- Omzetten van shapefile input naar memcollection----------------
    # Initialize point collection -> inpeilingen
    point_col_in = MemCollection(geometry_type='MultiPoint')
    records_in = []
    rows_in = arcpy.SearchCursor(input_inpeil)
    fields_in = arcpy.ListFields(input_inpeil)
    point_in = arcpy.Point()

    oid_fieldname = fields_in[0].name

    # Fill the point collection
    for row in rows_in:
        geom = row.getValue('SHAPE')
        properties = {}
        for field in fields_in:
            if field.name.lower() != 'shape':
                if isinstance(field.name, unicode):
                    key = field.name.encode('utf-8')
                else:
                    key = field.name
                if isinstance(row.getValue(field.name), unicode):
                    value = row.getValue(field.name).encode('utf-8')
                else:
                    value = row.getValue(field.name)
                properties[key] = value

        records_in.append({'geometry': {'type': 'Point',
                                      'coordinates': (geom.firstPoint.X, geom.firstPoint.Y)},
                         'properties': properties})

    point_col_in.writerecords(records_in)

    # Initialize point collection -> uipeilingen
    point_col_uit = MemCollection(geometry_type='MultiPoint')
    records_uit = []
    rows_uit = arcpy.SearchCursor(input_uitpeil)
    fields_uit = arcpy.ListFields(input_uitpeil)
    point_uit = arcpy.Point()

    oid_fieldname = fields_uit[0].name

    # Fill the point collection
    for row in rows_uit:
        geom = row.getValue('SHAPE')
        properties = {}
        for field in fields_uit:
            if field.name.lower() != 'shape':
                if isinstance(field.name, unicode):
                    key = field.name.encode('utf-8')
                else:
                    key = field.name
                if isinstance(row.getValue(field.name), unicode):
                    value = row.getValue(field.name).encode('utf-8')
                else:
                    value = row.getValue(field.name)
                properties[key] = value

        records_uit.append({'geometry': {'type': 'Point',
                                     'coordinates': (geom.firstPoint.X, geom.firstPoint.Y)},
                        'properties': properties})

    point_col_uit.writerecords(records_uit)

    # ---------- Get unieke waardes van profielnamen en hun middelpunt----------------
    # Van de inpeilingen
    profiel_namen_in = set(p['properties']['prof_ids'] for p in point_col_in.filter())

    # Initialize point collection -> middelpunten (inpeilingen)
    point_col_mid_in = MemCollection(geometry_type='MultiPoint')
    records_mid_in = []

    # Vindt voor elk profiel het middelste meetpunt
    for profiel in profiel_namen_in:
        profiel_punten = list(point_col_in.filter(property={'key': 'prof_ids', 'values': [profiel]}))
        middelpunt_nr = int(round(len(profiel_punten)/2,0))
        middelpunt = profiel_punten[middelpunt_nr]
        records_mid_in.append(middelpunt)

    # sla deze middelpunten op in een memcollection
    point_col_mid_in.writerecords(records_mid_in)

    # van de uitpeilingen
    profiel_namen_uit = set(p['properties']['prof_ids'] for p in point_col_uit.filter())

    # Initialize point collection -> middelpunten (inpeilingen)
    point_col_mid_uit = MemCollection(geometry_type='MultiPoint')
    records_mid_uit = []

    # Vindt voor elk profiel het middelste meetpunt
    for profiel in profiel_namen_uit:
        profiel_punten = list(point_col_in.filter(property={'key': 'prof_ids', 'values': [profiel]}))
        middelpunt_nr = int(round(len(profiel_punten) / 2, 0))
        middelpunt = profiel_punten[middelpunt_nr]
        records_mid_uit.append(middelpunt)

    # sla deze middelpunten op in een memcollection
    point_col_mid_uit.writerecords(records_mid_uit)

    return point_col_in, point_col_uit, point_col_mid_in, point_col_mid_uit, profiel_namen_in, profiel_namen_uit

def Createbuffer(point_col, radius=5):
    ''' Maakt van elk punt een polgon, door middel van een buffer met de ingegeven radius (default=5).
    input: pointcollection
    result: list met profielnaam en de shapelypolygon'''
    records = []

    # Fill the point collection
    for meetpunt in point_col.filter():
        profielnaam = meetpunt['properties']['prof_ids']
        punt = Point(meetpunt['geometry']['coordinates'])
        buffered = punt.buffer(radius)
        records.append([profielnaam,buffered])

    return records

def CalcSlibaanwas(point_list_in,point_list_uit, meter_factor=1):
    '''Deze functie berekent de slibaanwas tussen 2 profielen.
    input: list van 1 profiel inpeiling, list van 1 profiel uitpeiling, meter_factor(aantal meters vanaf
    de eerste meting)
    return: waarde van de hoeveelheid slibaanwas'''
    afstand_in = []
    afstand_uit = []
    bk_in = []
    bk_uit = []

    # Get de meetpuntgegevens van de inpeiling: de meetafstand en de bovenkant slip in NAP
    for meetpunt in point_list_in:
        afstand_in.append(meetpunt['properties']['afstand'])
        bk_in.append(meetpunt['properties']['_bk_nap'])

    # Get de meetpuntgegevens van de uitpeiling: de meetafstand en de bovenkant slip in NAP
    for meetpunt in point_list_uit:
        afstand_uit.append(meetpunt['properties']['afstand'])
        bk_uit.append(meetpunt['properties']['_bk_nap'])

    print afstand_in
    print bk_in
    plt.figure()
    plt.plot(afstand_in,bk_in)
    print 'test'

def GetSlibaanwas(point_col_in,point_col_uit, point_col_mid_uit,buffer_list, meter_factor=1):
    '''Deze funtie zoekt bij elke inpeiling een uitpeiling en berekent dan het verschil in slib (de slibaanwas)
    input:
    memcollection van de inpeiling
    memcollection van de uitpeiling
    memcollection van de middenpunten van de uitpeiling
    list met bufferpolygons en profielnamen inpeiling
    meter_factor

    result: memcollection lines met bij elke lijn een slibaanwas en de meter_factor vermeld.'''

    in_uit_combi = []

    # Vind bij elk profiel van de inpeilingen de uitpeiling die binnen de buffer valt
    for profiel_naam, buffer_p in buffer_list:
        for p in point_col_mid_uit.filter():
            punt_uit = Point(p['geometry']['coordinates'])
            if punt_uit.within(buffer_p):
                in_uit_combi.append([profiel_naam,p['properties']['prof_ids']])
    print in_uit_combi

    # Ga elk profiel af en bereken de slibaanwas
    for prof_in, prof_uit in in_uit_combi:
        prof_list_in = list(point_col_in.filter(property={'key': 'prof_ids', 'values': [prof_in]}))
        prof_list_uit = list(point_col_uit.filter(property={'key': 'prof_ids', 'values': [prof_uit]}))
        CalcSlibaanwas(prof_list_in, prof_list_uit)
        print test