# Necessary imports
import os
import csv
import arcpy
import numpy as np

from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine
from shapely.geometry import Point, LineString

# Script to convert text file profiles of project TI18135 into geometries and combine them

## ------------------------------------------ Set input parameters ------------------------------------------------- ##
# Complete: contains both slib and vaste bodem
waterlevel = -0.54
extra_length_tt = 0.10
link_table = "K:\Projecten\\2018\TI18135 Onderhoudsplan aanlegplaatsen gemeente Heerenveen\Tekening\Conversie_tekst" \
             "_bestanden_naar_shapes\link_tabel.csv"

output_folder = "K:\Projecten\\2018\TI18135 Onderhoudsplan aanlegplaatsen gemeente Heerenveen\Tekening\Conversie_" \
                "tekst_bestanden_naar_shapes"

input_folder_complete_23 = "K:\Projecten\\2018\TI18135 Onderhoudsplan aanlegplaatsen gemeente Heerenveen\Meet" \
                           "data eerdere projecten\Provincie Fryslan J. vd Ploeg - Vaarweg 8 en 23 - 28-05-2018\Vaar" \
                           "geul 23 XYZ"
complete_23_name = "compleet_vaargeul_23"
complete_line_23_name = "compleet_line_vaargeul_23"

input_folder_complete_8 = "K:\Projecten\\2018\TI18135 Onderhoudsplan aanlegplaatsen gemeente Heerenveen\Meet" \
                           "data eerdere projecten\Provincie Fryslan J. vd Ploeg - Vaarweg 8 en 23 - 28-05-2018\Vaar" \
                           "weg 8B XYZ"
complete_8_name = "compleet_vaarweg_8"
complete_line_8_name = "compleet_line_vaarweg_8"

# Bovenkant: contains only slib data
input_folder_bovenkant_23 = "K:\Projecten\\2018\TI18135 Onderhoudsplan aanlegplaatsen gemeente Heerenveen\Meetdata " \
                            "eerdere projecten\Vaarweg_8_23_Inpeiling\Vaargeul_23"
bovenkant_23_name = "bovenkant_vaargeul_23"
bovenkant_line_23_name = "bovenkant_line_vaargeul_23"

input_folder_bovenkant_8 = "K:\Projecten\\2018\TI18135 Onderhoudsplan aanlegplaatsen gemeente Heerenveen\Meetdata " \
                           "eerdere projecten\Vaarweg_8_23_Inpeiling\Vaargeul_8"
bovenkant_8_name = "bovenkant_vaarweg_8"
bovenkant_line_8_name = "bovenkant_line_vaargeul_8"


## ------------------------ Step 1: read text files and convert to geometry collections ---------------------------- ##


# Function to read files
def read_file(file_path, prof_name, waterlevel, bodem_values=None):
    point_list = []
    tt_point_list = []

    first_point = None
    last_point = None

    with open(file_path, mode='r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        row_count = sum(1 for row in reader)
        infile.seek(0)
        for i, row in enumerate(reader):
            properties = {}
            properties['bk_nap'] = float(row[2])
            properties['prof_ids'] = prof_name
            properties['code'] = '99'
            if bodem_values:
                properties['ok_nap'] = bodem_values[i]
            point = Point(float(row[0]), float(row[1]))

            point_list.append(
                {'geometry': {'type': 'Point',
                              'coordinates': point.coords[0]},
                 'properties': properties}
            )

            if i == 0:
                first_point = point
            if i == row_count - 1:
                last_point = point

    pre_line = TLine([first_point, last_point])

    # Verleng lijn met 10 centimeter voor de 22 punten
    line = pre_line.get_extended_line_with_length((pre_line.length + extra_length_tt), 'both')

    start_point = line.coords[0]
    end_point = line.coords[-1]

    tt_point_list.append(
        {'geometry': {'type': 'Point',
                      'coordinates': start_point},
         'properties': {'prof_ids': prof_name,
                        'code': '22l',
                        'bk_nap': waterlevel,
                        'ok_nap': waterlevel}}
    )

    tt_point_list.extend(point_list)

    tt_point_list.extend(
        [{'geometry': {'type': 'Point',
                       'coordinates': end_point},
         'properties': {'prof_ids': prof_name,
                        'code': '22r',
                        'bk_nap': waterlevel,
                        'ok_nap': waterlevel}}]
    )

    # Calculate distances for each point
    for p in tt_point_list:
        distance = Point(start_point).distance(Point(p['geometry']['coordinates']))
        p['properties']['afstand'] = round(distance, 2)

    return tt_point_list, line


# Function to read the files in the folder and convert them to profiles
def read_folder(input_folder, pattern):
    point_col = MemCollection(geometry_type='Point')
    line_col = MemCollection(geometry_type='LineString')

    list_files = [f for f in os.listdir(input_folder) if pattern in f]

    point_list = []
    for f in list_files:
        file_path = os.path.join(input_folder, f)
        prof_id = os.path.splitext(f)[0]

        prof_list, prof_line = read_file(file_path, prof_id, waterlevel)

        point_list.extend(prof_list)
        line_col.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': prof_line.coords},
             'properties': {'prof_ids': prof_id,
                            'breedte': round(prof_line.length, 2)}}])

    point_col.writerecords(point_list)

    return point_col, line_col


# Function to get only values in the file, not coordinates
def get_bodem_values(file_path):
    bodem_values = []
    with open(file_path, mode='r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        for row in reader:
            bodem_values.append(float(row[2]))
    return bodem_values


# Function to combine two files in a folder to get bovenkant and onderkant slib
def combine_profiles_in_folder(input_folder, pattern):
    point_col = MemCollection(geometry_type='Point')
    line_col = MemCollection(geometry_type='LineString')

    list_files = [f for f in os.listdir(input_folder) if pattern in f]

    point_list = []
    for i in xrange(0, 28, 2):
        f_bodem = list_files[i]
        f_path_bodem = os.path.join(input_folder, f_bodem)
        f_slib = list_files[i+1]
        f_path_slib = os.path.join(input_folder, f_slib)
        prof_name = f_slib.split("_")[0]

        bodem_values = get_bodem_values(f_path_bodem)
        prof_list, prof_line = read_file(f_path_slib, prof_name, waterlevel, bodem_values)

        point_list.extend(prof_list)
        line_col.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': prof_line.coords},
             'properties': {'prof_ids': prof_name,
                            'breedte': round(prof_line.length, 2)}}])

    point_col.writerecords(point_list)

    return point_col, line_col

# Run the functions for the four folders to get to point collections
point_col_complete_8, line_col_complete_8 = combine_profiles_in_folder(input_folder_complete_8, '0_')
point_col_complete_23, line_col_complete_23 = combine_profiles_in_folder(input_folder_complete_23, '0_')
point_col_bovenkant_8, line_col_bovenkant_8 = read_folder(input_folder_bovenkant_8, 'DWP')
point_col_bovenkant_23, line_col_bovenkant_23 = read_folder(input_folder_bovenkant_23, 'DWP')

new_point_col_bovenkant_8 = MemCollection(geometry_type='Point')
new_point_col_bovenkant_23 = MemCollection(geometry_type='Point')

## -------------------------------------- Step 2: Combineer profielen ---------------------------------------------- ##


def link_table_to_dict(link_table):
    with open(link_table, mode='r') as infile:
        dialect = csv.Sniffer().sniff(infile.read(1024), delimiters=';,')
        infile.seek(0)
        reader = csv.reader(infile, dialect)
        link_dictionary = {rows[0]: rows[1] for rows in reader}
    return link_dictionary


link_dict = link_table_to_dict(link_table)

for l in line_col_bovenkant_23:
    prof_id = l['properties']['prof_ids']

    if not link_dict.get(prof_id):
        continue

    l['properties']['compleet'] = link_dict[prof_id]

    bovenkant_points = list(point_col_bovenkant_23.filter(property={'key': 'prof_ids', 'values': [prof_id]}))

    complete_line = list(line_col_complete_23.filter(property={'key': 'prof_ids',
                                                                      'values': [link_dict[prof_id]]}))
    complete_points = list(point_col_complete_23.filter(property={'key': 'prof_ids',
                                                                  'values': [link_dict[prof_id]]}))

    array_dist = np.array([point['properties']['afstand']
                           for point in complete_points if point['properties'].get('ok_nap') is not None])
    array_level = np.array([point['properties']['ok_nap']
                           for point in complete_points if point['properties'].get('ok_nap') is not None])

    bline = TLine(l['geometry']['coordinates'])
    line_complete_length = complete_line[0]['properties']['breedte']
    cline = TLine(complete_line[0]['geometry']['coordinates'])
    line_bovenkant_length = l['properties']['breedte']

    if line_bovenkant_length > line_complete_length:
        l['properties']['situation'] = 'Langer dan compleet'
    else:
        new_line = bline.get_extended_line_with_length(line_complete_length, 'both')

        ttl_point = new_line.coords[0]
        ttr_point = new_line.coords[-1]

        for p in bovenkant_points:
            distance = Point(ttl_point).distance(Point(p['geometry']['coordinates']))

            p['properties']['compleet'] = link_dict[prof_id]

            if p['properties']['code'] == '22l':
                p['geometry']['coordinates'] = ttl_point
            elif p['properties']['code'] == '22r':
                p['geometry']['coordinates'] = ttr_point
                p['properties']['afstand'] = distance
            else:
                p['properties']['afstand'] = distance
                ok_nap = round(np.interp(distance, array_dist, array_level), 3)
                if ok_nap > p['properties']['bk_nap']:
                    p['properties']['ok_nap'] = p['properties']['bk_nap']
                else:
                    p['properties']['ok_nap'] = ok_nap
        l['geometry']['coordinates'] = new_line.coords

        new_point_col_bovenkant_23.writerecords(bovenkant_points)


for l in line_col_bovenkant_8:
    prof_id = l['properties']['prof_ids']

    if not link_dict.get(prof_id):
        continue

    l['properties']['compleet'] = link_dict[prof_id]

    bovenkant_points = list(point_col_bovenkant_8.filter(property={'key': 'prof_ids', 'values': [prof_id]}))

    complete_line = list(line_col_complete_8.filter(property={'key': 'prof_ids',
                                                              'values': [link_dict[prof_id]]}))
    complete_points = list(point_col_complete_8.filter(property={'key': 'prof_ids',
                                                                 'values': [link_dict[prof_id]]}))

    array_dist = np.array([point['properties']['afstand']
                           for point in complete_points if point['properties'].get('ok_nap') is not None])
    array_level = np.array([point['properties']['ok_nap']
                           for point in complete_points if point['properties'].get('ok_nap') is not None])

    bline = TLine(l['geometry']['coordinates'])
    line_complete_length = complete_line[0]['properties']['breedte']
    cline = TLine(complete_line[0]['geometry']['coordinates'])
    line_bovenkant_length = l['properties']['breedte']

    if line_bovenkant_length > line_complete_length:
        l['properties']['situation'] = 'Langer dan compleet'
    else:
        new_line = bline.get_extended_line_with_length(line_complete_length, 'both')

        ttl_point = new_line.coords[0]
        ttr_point = new_line.coords[-1]

        for p in bovenkant_points:
            distance = Point(ttl_point).distance(Point(p['geometry']['coordinates']))

            p['properties']['compleet'] = link_dict[prof_id]

            if p['properties']['code'] == '22l':
                p['geometry']['coordinates'] = ttl_point
            elif p['properties']['code'] == '22r':
                p['geometry']['coordinates'] = ttr_point
                p['properties']['afstand'] = distance
            else:
                p['properties']['afstand'] = distance
                ok_nap = round(np.interp(distance, array_dist, array_level), 3)
                if ok_nap > p['properties']['bk_nap']:
                    p['properties']['ok_nap'] = p['properties']['bk_nap']
                else:
                    p['properties']['ok_nap'] = ok_nap
        l['geometry']['coordinates'] = new_line.coords

        new_point_col_bovenkant_8.writerecords(bovenkant_points)


## --------------------------- Step x: convert these geometry collections to shapefile ------------------------------ ##


def convert_to_point_shapefile(output_folder, file_name, point_collection):
    output_points = arcpy.CreateFeatureclass_management(output_folder, file_name, 'POINT', spatial_reference=28992)

    arcpy.AddField_management(output_points, 'prof_ids', "TEXT")
    arcpy.AddField_management(output_points, 'code', 'TEXT')
    arcpy.AddField_management(output_points, 'afstand', 'DOUBLE')
    arcpy.AddField_management(output_points, 'bk_nap', "TEXT")
    arcpy.AddField_management(output_points, 'ok_nap', "TEXT")
    arcpy.AddField_management(output_points, 'compleet', "TEXT")


    dataset = arcpy.InsertCursor(output_points)

    for p in point_collection.filter():
        row = dataset.newRow()
        point = arcpy.Point()
        point.X = p['geometry']['coordinates'][0]
        point.Y = p['geometry']['coordinates'][1]
        row.Shape = point

        row.setValue('prof_ids', p['properties'].get('prof_ids', None))
        row.setValue('code', p['properties'].get('code', None))
        row.setValue('afstand', p['properties'].get('afstand', None))
        row.setValue('bk_nap', p['properties'].get('bk_nap', None))
        row.setValue('ok_nap', p['properties'].get('ok_nap', None))
        row.setValue('compleet', p['properties'].get('compleet', None))

        dataset.insertRow(row)

    return


def convert_to_line_shapefile(output_folder, file_name, line_collection):
    output_points = arcpy.CreateFeatureclass_management(output_folder, file_name, 'POLYLINE', spatial_reference=28992)

    arcpy.AddField_management(output_points, 'prof_ids', "TEXT")
    arcpy.AddField_management(output_points, 'breedte', 'DOUBLE')
    arcpy.AddField_management(output_points, 'compleet', 'TEXT')
    arcpy.AddField_management(output_points, 'situation', 'TEXT')

    dataset = arcpy.InsertCursor(output_points)

    for line in line_collection.filter():
        row = dataset.newRow()
        point = arcpy.Point()
        mline = arcpy.Array()
        array = arcpy.Array()

        for l in line['geometry']['coordinates']:
            point.X = l[0]
            point.Y = l[1]
            array.add(point)

        mline.add(array)
        row.Shape = mline

        row.setValue('prof_ids', line['properties'].get('prof_ids', None))
        row.setValue('breedte', line['properties'].get('breedte', None))
        row.setValue('compleet', line['properties'].get('compleet', None))
        row.setValue('compleet', line['properties'].get('situation', None))

        dataset.insertRow(row)

    return


# convert_to_point_shapefile(output_folder, bovenkant_8_name, new_point_col_bovenkant_8)
# convert_to_point_shapefile(output_folder, bovenkant_23_name, new_point_col_bovenkant_23)
# convert_to_point_shapefile(output_folder, complete_8_name, point_col_complete_8)
# convert_to_point_shapefile(output_folder, complete_23_name, point_col_complete_23)

convert_to_line_shapefile(output_folder, bovenkant_line_8_name, line_col_bovenkant_8)
convert_to_line_shapefile(output_folder, bovenkant_line_23_name, line_col_bovenkant_23)
convert_to_line_shapefile(output_folder, complete_line_8_name, line_col_complete_8)
convert_to_line_shapefile(output_folder, complete_line_23_name, line_col_complete_23)























