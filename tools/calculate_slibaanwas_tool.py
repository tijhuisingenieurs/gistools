import os
import csv
import pandas as pd
import logging
import os.path
import sys
import numpy as np
from numpy.core.umath import add
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
    # --- Initialize point collection -> inpeilingen
    point_col_in = MemCollection(geometry_type='MultiPoint')
    records_in = []
    rows_in = arcpy.SearchCursor(input_inpeil)
    fields_in = arcpy.ListFields(input_inpeil)
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
    # Schrijf de gegegevens naar de collection
    point_col_in.writerecords(records_in)

    # --- Initialize point collection -> uipeilingen
    point_col_uit = MemCollection(geometry_type='MultiPoint')
    records_uit = []
    rows_uit = arcpy.SearchCursor(input_uitpeil)
    fields_uit = arcpy.ListFields(input_uitpeil)
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
    # Schrijf de gegegevens naar de collection
    point_col_uit.writerecords(records_uit)

    # ---------- Get unieke waardes van profielnamen en hun middelpunt----------------
    # --- Van de inpeilingen
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

    # --- Van de uitpeilingen
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

    # Initialize voor opslag polygonen
    records = []

    # Ga elk meetpunt langs en create een polygon. Sla de polygon op in records
    for meetpunt in point_col.filter():
        profielnaam = meetpunt['properties']['prof_ids']
        punt = Point(meetpunt['geometry']['coordinates'])
        buffered = punt.buffer(radius)
        records.append([profielnaam,buffered])

    return records

def CalcSlibaanwas(point_list_in,point_list_uit, meter_factor=1):
    '''Deze functie berekent de slibaanwas tussen 2 profielen.
    input: list van 1 profiel inpeiling, list van 1 profiel uitpeiling, meter_factor(aantal meters vanaf
    de eerste meting, welke mee wordt genomen in de slibaanwas berekening (dus meters vanaf kant))
    return: waarde van de hoeveelheid slibaanwas'''

    # parameters om de gegevens in op te slaan
    afstand_in = []
    afstand_uit = []
    bk_in = []
    bk_uit = []
    ind_22_in = []
    ind_22_uit = []

    # ------- Inlezen van de gegegens
    # Get de meetpuntgegevens van de inpeiling: de meetafstand en de bovenkant slip in NAP en de index van het 22 punt
    for ind, meetpunt in enumerate(point_list_in):
        afstand_in.append(meetpunt['properties']['afstand'])
        bk_in.append(meetpunt['properties']['_bk_nap'])
        if meetpunt['properties']['code'] == '22':
            ind_22_in.append(ind)

    # Get de meetpuntgegevens van de uitpeiling: de meetafstand en de bovenkant slip in NAP en de index van het 22 punt
    for ind, meetpunt in enumerate(point_list_uit):
        afstand_uit.append(meetpunt['properties']['afstand'])
        bk_uit.append(meetpunt['properties']['_bk_nap'])
        if meetpunt['properties']['code'] == '22':
            ind_22_uit.append(ind)

    # -------- Berekenen interpolatie
    # Reeks waarop de interpolatie plaatsvindt
    # Maak een vanaf de eerste t/m de laatste meting punten om de 10 cm
    minimale_afstand = min(min(afstand_in),min(afstand_in))
    maximale_afstand = max(max(afstand_in),max(afstand_in))
    aantal_punten = (abs(minimale_afstand) +maximale_afstand)*10

    reeks_10cm = np.linspace(minimale_afstand,maximale_afstand,aantal_punten)

    # Interpolatie van de meetpunten
    intp_bk_in = np.interp(reeks_10cm,afstand_in,bk_in)
    intp_bk_uit = np.interp(reeks_10cm, afstand_uit, bk_uit)

    # Bereken vanaf het 22 punt de bounding box met daarbij de meters vanaf de kant
    afstand_begin = afstand_in[ind_22_in[0]] + meter_factor
    afstand_eind = afstand_in[ind_22_in[1]] - meter_factor
    box_lengte = afstand_eind-afstand_begin

    # Vind hier de bijbehorende waarde van de reeks_10cm.
    for ind, value in enumerate(reeks_10cm):
        if round(value*10) == round(afstand_begin*10):
            ind_begin = ind
        if round(value*10) == round(afstand_eind*10):
            ind_eind = ind

    # ------- Bereken hoeveelheid slib binnen box van interesse
    # Hoeveelheid slib in m2 in het hele profiel
    slibaanwas_totaal = np.sum((intp_bk_in[ind_begin:ind_eind]-intp_bk_uit[ind_begin:ind_eind]))*0.1
    # Hoeveelheid slib in m per lengte-eenheid
    slibaanwas_lengte = slibaanwas_totaal/((box_lengte))

    # ------- Test figures om de dataset te bekijken
    # plt.figure()
    # plt.plot(reeks_10cm,intp_bk_uit,'ro')
    # plt.hold(True)
    # plt.plot(reeks_10cm, intp_bk_in,'.')
    # plt.hold(False)

    return slibaanwas_lengte, box_lengte, meter_factor

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
    slibaanwas_all = []
    box_lengte_all = []
    #prof_len_in = []
    #prof_len_uit = []
    meter_factor_all = []
    datum_in_all = []
    datum_uit_all = []

    # Vind bij elk profiel van de inpeilingen de uitpeiling die binnen de buffer valt
    for profiel_naam, buffer_p in buffer_list:
        for p in point_col_mid_uit.filter():
            punt_uit = Point(p['geometry']['coordinates'])
            if punt_uit.within(buffer_p):
                in_uit_combi.append([profiel_naam,p['properties']['prof_ids']])
    print in_uit_combi

    # Ga elk profiel af en bereken de slibaanwas en verzamel info voor de output
    for prof_in, prof_uit in in_uit_combi:
        prof_list_in = list(point_col_in.filter(property={'key': 'prof_ids', 'values': [prof_in]}))
        prof_list_uit = list(point_col_uit.filter(property={'key': 'prof_ids', 'values': [prof_uit]}))
        slibaanwas_profiel, , meter_factor = CalcSlibaanwas(prof_list_in, prof_list_uit)
        slibaanwas_all.append(slibaanwas_profiel)
        box_lengte_all.append(box_lengte)
        meter_factor_all.append(meter_factor)
        datum_in_all.append(prof_list_in[0]['properties']['datum'])
        datum_uit_all.append(prof_list_uit[0]['properties']['datum'])
    #plt.show()

    # Maken van de output-shape
    # Maak een shape van de middelpunten van de inpeiling, voeg daar de kolommen aan toe:
    # profielnaam_in
    # profielnaam_uit
    # lengte_in
    # lengte_uit
    # lengte_slibaanwas
    # slibaanwas
    # meter_factor
    # datum_in
    # datum_uit

    point = arcpy.Point()
    output_in_points = arcpy.CreateFeatureclass_management(output_dir, output_name_l, 'POINT',
                                                          spatial_reference=28992)

    arcpy.AddField_management(output_in_points, 'p_ids_in', "TEXT")
    arcpy.AddField_management(output_in_points, 'p_ids_uit', "TEXT")
    arcpy.AddField_management(output_in_points, 'slibaanwas', "DOUBLE")
    arcpy.AddField_management(output_in_points, 'ps_breedte', "DOUBLE")
    arcpy.AddField_management(output_in_points, 'datum_in', "TEXT")
    arcpy.AddField_management(output_in_points, 'datum_uit', "TEXT")
    arcpy.AddField_management(output_in_points, 'm_factor', "DOUBLE")

    dataset = arcpy.InsertCursor(output_in_points)
    fields_lines = next(line_col.filter())['properties'].keys()

    for l in line_col.filter():
        arcpy.AddMessage('profiel: ' + str(l['properties']['ids']))
        arcpy.AddMessage('geometrie: ' + str(l['geometry']['coordinates']))

        mline = arcpy.Array()
        array = arcpy.Array()
        for p in l['geometry']['coordinates']:
            point.X = p[0]
            point.Y = p[1]
            array.add(point)

        mline.add(array)

        row = dataset.newRow()
        row.Shape = mline

        for field in fields_lines:
            row.setValue(field, l['properties'].get(field, ''))

        dataset.insertRow(row)

    add_result_to_display(output_in_points, output_name_l)



return slibaanwas_all, box_lengte_all
