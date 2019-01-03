
import os

import arcpy
import numpy as np
from shapely.geometry import LineString, Point

from gistools.utils.collection import MemCollection

# Deze functies straks verplaatsen naar ARCGIS gedeelte -----------------------
def from_shape_to_memcollection_points(input_shape):
    """Deze functie zet de shape met informatie om naar een punten collectie
    input: shapefile met meetpunten erin (het kan elke puntenshape zijn. De kolominfo wordt overgezet
    naar de properties en de coordinaten naar coordinates)
    output: memcollection met deze punten erin"""

    # ---------- Omzetten van shapefile input naar memcollection----------------
    # --- Initialize point collection
    point_col = MemCollection(geometry_type='MultiPoint')
    records_in = []
    rows_in = arcpy.SearchCursor(input_shape)
    fields_in = arcpy.ListFields(input_shape)
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
        # Voeg per punt de coordinaten en properties toe
        records_in.append({'geometry': {'type': 'Point',
                                        'coordinates': (geom.firstPoint.X, geom.firstPoint.Y)},
                           'properties': properties})
    # Schrijf de gegegevens naar de collection
    point_col.writerecords(records_in)
    return point_col

def from_list_to_shapefile_points(points_list, output_folder, output_name, output_number):
    '''functie om de lijst met punten naar arcgis te halen'''

    # Initializatie van het path en naam output en shapefile
    output_dir = os.path.dirname(output_folder)
    output_file = arcpy.CreateFeatureclass_management(output_dir, output_number + '_' + output_name, 'POINT', spatial_reference=28992)
    arcpy.AddMessage('Outputname: ' + output_name)

    # Toevoegen van Fields aan output shape
    arcpy.AddField_management(output_file, 'prof_ids', "TEXT")
    arcpy.AddField_management(output_file, 'code', "TEXT")
    arcpy.AddField_management(output_file, '_bk_nap', "DOUBLE")
    arcpy.AddField_management(output_file, 'x_coord', "DOUBLE")
    arcpy.AddField_management(output_file, 'y_coord', "DOUBLE")
    arcpy.AddField_management(output_file, 'afstand', "DOUBLE")
    arcpy.AddField_management(output_file, 'aantal', "DOUBLE")
    # arcpy.AddField_management(output_file, 'datum', "TEXT")
    dataset = arcpy.InsertCursor(output_file)

    # De punten en de gegevens van de punten overbrengen naar de shapefile
    for p in points_list:
        row = dataset.newRow()
        point = arcpy.Point(p['geometry']['coordinates'][0],p['geometry']['coordinates'][1])
        row.Shape = point

        # Voeg de properties toe aan de attribuuttable
        row.setValue('_bk_nap', p['properties']['z'])
        row.setValue('x_coord', p['geometry']['coordinates'][0])
        row.setValue('y_coord', p['geometry']['coordinates'][1])
        row.setValue('afstand', p['properties']['afstand'])
        row.setValue('aantal', p['properties']['aantal'])
        row.setValue('prof_ids', p['properties']['prof_ids'])
        row.setValue('code', p['properties']['code'])
        # row.setValue('datum')

        dataset.insertRow(row)

# def from_memcol_to_shapefile_points(point_col, output_file, output_name, output_number):
#     '''functie om de puntencollectie naar arcgis te halen'''
#     output_dir = os.path.dirname(output_file)
#     output_file = arcpy.CreateFeatureclass_management(output_dir, output_number + '_' + output_name, 'POINT', spatial_reference=28992)
#     arcpy.AddMessage('Outputname: ' + output_name)
#
#     arcpy.AddField_management(output_file, 'prof_ids', "TEXT")
#     arcpy.AddField_management(output_file, '_bk_nap', "DOUBLE")
#     arcpy.AddField_management(output_file, 'x_coord', "DOUBLE")
#     arcpy.AddField_management(output_file, 'y_coord', "DOUBLE")
#     arcpy.AddField_management(output_file, 'afstand', "DOUBLE")
#     arcpy.AddField_management(output_file, 'aantal', "DOUBLE")
#     # arcpy.AddField_management(output_file, 'datum', "TEXT")
#
#     dataset = arcpy.InsertCursor(output_file)
#
#     for p in point_col.filter():
#         row = dataset.newRow()
#         point = arcpy.Point(p['geometry']['coordinates'][0],p['geometry']['coordinates'][1])
#
#         # Voeg de properties toe aan de attribuuttable
#         row.Shape = point
#         row.setValue('prof_ids', output_name)
#         row.setValue('_bk_nap', p['properties']['z'])
#         row.setValue('x_coord', p['geometry']['coordinates'][0])
#         row.setValue('y_coord', p['geometry']['coordinates'][1])
#         row.setValue('afstand', p['properties']['afstand'])
#         row.setValue('aantal', p['properties']['aantal'])
#         # row.setValue('datum')
#
#         dataset.insertRow(row)
# EINDE functies naar ARCGIS -----------------------------------

def elec_punt_to_profiel(lijn, points_col, naam, zoekafstand):
    '''Deze functie zoekt punten bij een lijn en zorgt ervoor dat er op de lijn een punt terugkomt
    input: shapely linestring, memcollection met punten erin, waarde voor radius buffer
    returns: een list met daarin [shapely linestring, buffer van shapely linestring, list met point colletcion]'''

    # Initialisatie
    lijn_punten_list = []
    plek_punten_list = []
    afstanden_punt_dict = {}
    max_afstand = 0
    min_afstand = 999

    # Maak memcollectie aan om de electronische punten in op te slaan
    lijn_punten_col = MemCollection(geometry_type='Point')

    # Maak een buffer om de lijn. Binnen deze buffer zoek je de punten
    lijn_buffer = lijn.buffer(zoekafstand)

    # Zoek welke meetpunten binnen de buffer vallen en maak er een selectie van de er per afstand 1 punt komt
    for p in points_col.filter(bbox=lijn_buffer.bounds):  # hier wordt spatial indexing van memcollection gebruikt
        punt = Point(p['geometry']['coordinates'])
        if punt.within(lijn_buffer):
            # Maak van het punt een projectie die op de lijn ligt en sla dit punt op in list
            dist_on_line = lijn.project(punt)
            snapped_point = lijn.interpolate(dist_on_line)
            lijn_punten_list.append(
                {'geometry': {'type': 'Point',
                              'coordinates': (snapped_point.coords[0][0], snapped_point.coords[0][1])},
                 'properties': p['properties']}
            )
            # Om zometeen makkelijk te kunnen middelen, sla per afstand 1 punt op om straks mee te zoeken
            afstand = round(dist_on_line,1) # Op 1 decimaal is dus 10 cm uit elkaar
            if str(afstand) not in afstanden_punt_dict.keys():
                afstanden_punt_dict[str(afstand)] = [afstand, snapped_point]

    # Sla de gegevens van de electronische punten binnen de buffer vallend weer in een memollection
    lijn_punten_col.writerecords(lijn_punten_list)

    # Zoek de punten die op ongeveer dezelfde plek het profiel raken en bereken het gemiddelde
    # Per plek wil je maar 1 punt opnemen in het uiteindelijke profiel
    for plek in afstanden_punt_dict.keys():
        plek_punt = afstanden_punt_dict[plek][1]
        plek_afstand = afstanden_punt_dict[plek][0]
        # Maak buffer met welke punten je wilt middelen
        plek_punt_buffer = plek_punt.buffer(0.1)
        som_z = 0
        aantal_p = 0
        # Zoek de punten bij elkaar die in de boundingbox vallen
        for p in lijn_punten_col.filter(bbox=plek_punt_buffer.bounds):
            punt = Point(p['geometry']['coordinates'])
            # Test of het punt inderdaad binnen de buffer valt
            if punt.within(plek_punt_buffer):
                aantal_p += 1
                som_z += p['properties']['z']
        # Wanneer alle punten bekeken zijn, bereken gemiddelde z waarde
        if aantal_p > 0 and som_z != 0:
            z_gemiddeld = som_z/aantal_p
            # Voeg de gegevens toe aan het plekpunt
            plek_punten_list.append(
                {'geometry': dict(type='Point', coordinates=(plek_punt.coords[0][0], plek_punt.coords[0][1])),
                 'properties': dict(z=z_gemiddeld, afstand=plek_afstand, aantal=aantal_p, code='99', prof_ids=naam)}
            )
        if plek_afstand > max_afstand:
            max_afstand = plek_afstand
            z_max_afstand = z_gemiddeld
        if plek_afstand < min_afstand:
            min_afstand = plek_afstand
            z_min_afstand = z_gemiddeld

    ## Hier wil je ook nog ergens 22 punten toevoegen!!!
    # Toevoegen van 22 punten. Neem voor nu het begin en eindpunt als 22 punt
    # Zorg ervoor dat het waterpeil (de z waarde) gelijk is, kies het hoogste waarde
    z_22 = max(z_max_afstand, z_min_afstand) + 0.05
    # Het eerste 22 punt is aan het eind van de lijn op een afstand -0.1m (NOG IMPLEMENTEREN!)
    plek_punten_list.append(
        {'geometry': dict(type='Point', coordinates=(lijn.coords.xy[0][0],lijn.coords.xy[1][0])),
         'properties': dict(z=z_22, afstand=0, aantal=-1, code='22', prof_ids=naam)}
    )

    # Het tweede 22 punt is aan het eind van de lijn op een afstand +0.1m (NOG IMPLEMENTEREN)
    plek_punten_list.append(
        {'geometry': dict(type='Point', coordinates=(lijn.coords.xy[0][1],lijn.coords.xy[1][1])),
         'properties': dict(z=z_22, afstand=lijn.length, aantal=-1, code='22', prof_ids=naam)}
    )
    # Geef terug de plek van het gemiddelde punt
    return plek_punten_list

# Tool 2: het maken van een puntenprofiel ahv lijn door electronische datawolk
input_lijnen = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\profiellijn_2.shp'
input_punten = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\Meetpunten_elektronisch_test.shp'
output_file =  'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata'
output_number = str(np.random.random_integers(1,100))
print('output nummer: ',output_number)

# Zet de elektronische meetpunten om naar een memcollection
elek_punten_col = from_shape_to_memcollection_points(input_punten)

# Lees de profiellijnen in en zet de arcpy om in shapely line
lijn_list = []
rows_in = arcpy.SearchCursor(input_lijnen)
fields_in = arcpy.ListFields(input_lijnen)
# Ga de input af en sla de geom op in dict, maak meteen een buffer en zoek de punten die daarbinnen vallen
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
            # sla de prof_ids en de geom op in list
            if key == 'prof_ids':
                lijn_shapely = LineString([(geom.firstPoint.X,geom.firstPoint.Y), (geom.lastPoint.X, geom.lastPoint.Y)])
                lijn_list.append([value, lijn_shapely])

# Ga elke lijn af en vind de meetpunten uit de electronische gegevens. En zet die als punten op de lijn.
gemiddeld_punt_all = []
for gegevens in lijn_list:
    lijn = gegevens[1]
    prof_ids = gegevens[0]
    lijn_buffer = lijn.buffer(0.1)
    # Zoek welke elektronische meetpunten binnen de zoekafstand vallen,
    # Cluster deze punten en neem de gemiddelde z waarde. Ze komen terug in memcollection op 1 gezamelijk punt
    gemiddeld_punt_deel = elec_punt_to_profiel(lijn, elek_punten_col, prof_ids, zoekafstand=0.5)
    # Voeg alle punten toe aan 1 list
    gemiddeld_punt_all += gemiddeld_punt_deel

# Zet de list met gemiddelde punten om naar een shapefile
from_list_to_shapefile_points(gemiddeld_punt_all, output_file, 'test_alles', output_number)
print('k')

# Voeg 22 punten toe aan uiteinde van de lijn, en daarbij de waarde van z +0.2 ofzo. (testen)

# Sla de punten op als shapefile met devolgende kolommen:
# prof_ids, datum, code, afstand, x_coord, y_coord, _bk_nap

# Dan kun je deze profielen gebruiken in de slibaanwas tool.