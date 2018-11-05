import os
import csv
import pandas as pd
import logging
import os.path
import sys

import arcpy

from utils.addresulttodisplay import add_result_to_display
from utils.arcgis_logging import setup_logging

from gistools.utils.collection import MemCollection



# ------------ Part1:
def GetProfielMiddelpunt(input_inpeil, input_uitpeil):
    ''' Deze functie maakt van de metingen een overzicht van de profielen in deze shape en een middelpunt.
     input: input_inpeil(shapefile), input_uitpeil(shapefile)
     return: input bestanden, list met profielnaam en de coordinaten van het middelpunt'''

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
    profiel_namen = set(p['properties']['prof_ids'] for p in point_col_in.filter())

    # Initialize point collection -> middelpunten (inpeilingen)
    point_col_mid = MemCollection(geometry_type='MultiPoint')
    records_mid = []

    # Vindt voor elk profiel het middelste meetpunt
    for profiel in profiel_namen:
        profiel_punten = list(point_col_in.filter(property={'key': 'prof_ids', 'values': [profiel]}))
        middelpunt_nr = int(round(len(profiel_punten)/2,0))
        middelpunt = profiel_punten[middelpunt_nr]
        print middelpunt
        records_mid.append(middelpunt)

    # sla deze middelpunten op in een memcollection
    point_col_mid.writerecords(records_mid)

    K = 3