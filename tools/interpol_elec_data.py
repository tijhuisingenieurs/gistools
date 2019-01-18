# Deze straks naar de arcgis deel;
# Er is nog een foutmelding bij het omzetten naar GIS. NAKIJKEN!

import numpy as np
from scipy.interpolate import griddata
from gistools.utils.collection import MemCollection
from gistools.tools.calculate_slibaanwas_elektronische_data_tool import interpol_elec_data
import arcpy
import matplotlib.pyplot as plt
import os

# De functies om van arcgis naar python te gaan en terug
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

def from_grid_to_shapefile_points(grid, z_waardes, output_folder, output_name, output_number):
    '''functie om de grid met punten naar arcgis te halen'''

    # check of de coordinaten in een array of list staan:
    if len(grid) == 2:
        array = True
        # dan array coordinaten
    elif len(grid) == 1:
        array = False
        # dan list coordinaten

    # Initializatie van het path en naam output en shapefile
    output_dir = os.path.dirname(output_folder)
    output_file = arcpy.CreateFeatureclass_management(output_dir, output_number + '_' + output_name, 'POINT',
                                                      spatial_reference=28992)
    arcpy.AddMessage('Outputname: ' + output_name)
    arcpy.AddMessage('Output: ' + output_folder)

    # Toevoegen van Fields aan output shape
    arcpy.AddField_management(output_file, '_bk_nap', "DOUBLE")
    arcpy.AddField_management(output_file, 'x_coord', "DOUBLE")
    arcpy.AddField_management(output_file, 'y_coord', "DOUBLE")

    dataset = arcpy.InsertCursor(output_file)

    # De punten en de gegevens van de punten overbrengen naar de shapefile
    for ind, p in np.ndenumerate(z_waardes):
        # uitgaande van regular grid van z-waardes
        if array:
            # Grid als array
            x_waarde = grid[0][ind]
            y_waarde = grid[1][ind]
        else:
            # Grid als list
            x_waarde = grid[0][ind[0]][0]
            y_waarde = grid[0][ind[0]][1]

        row = dataset.newRow()
        point = arcpy.Point(x_waarde,y_waarde)
        row.Shape = point

        # Voeg de properties toe aan de attribuuttable
        row.setValue('_bk_nap', p)
        row.setValue('x_coord', x_waarde)
        row.setValue('y_coord', y_waarde)

        dataset.insertRow(row)


# Read the parameter values
# 0: Electronische data jaar 1 (puntenshape)
# 1: Electronische data jaar 2 (puntenshape)
# 2: Meegegeven gridcelgrootte
# 3: grid overnemen uit 1 van de puntendata (puntenshape)
# 3: Outputfolder


# # Script arguments
# input_jaar_1 = arcpy.GetParameterAsText(0)
# input_jaar_2 = arcpy.GetParameterAsText(1)
# gridcel = arcpy.GetParameterAsText(2)
# grid_overnemen = arcpy.GetParameterAsText(3)
# output_folder = arcpy.GetParameterAsText(4)

# Inpur data voor in PYCHARM
# input_jaar_1 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\elec_jaar1_test.shp'
input_jaar_1 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\simple_grid_elec.shp'
# input_jaar_2 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\elec_jaar2_test.shp'
# input_jaar_2 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\simple_grid_jr2.shp'
input_jaar_2 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\\resultaat_tool\\01_Test_grid_jr_2_interpolatie.shp'
output_folder = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\\resultaat_tool\\'
output_name = 'Test_grid_real'#'Test_grid_interpolatie'

output_name_jr1 = 'Test_grid_jr_1_interpolatie'
output_name_jr2 = 'Test_grid_jr_2_interpolatie'

output_name_jr1 = 'Test_grid_jr_1_interpolatie_gridovernemen'
output_name_jr2 = 'Test_grid_jr_2_interpolatie'
# output_number = str(np.random.random_integers(1, 100))
gridcel = 0.5
output_number = '01'
print output_number
grid_overnemen = True

# ---------------- START CODE -----------------------------
# Van GIS shape naar memcollection
# --------- Inlezen jaar 1
jr_1_point_col = from_shape_to_memcollection_points(input_jaar_1)

# --------- Inlezen jaar 2
jr_2_point_col = from_shape_to_memcollection_points(input_jaar_2)

# Interpoleer de gegevens
# Wanneer het grid kan worden overgenomen:
if grid_overnemen:
    gridcel = -1
    grid_data_overnemen = jr_2_point_col
    jr_1_grid_z, grid_list = interpol_elec_data(jr_1_point_col, grid_data_overnemen, gridcel)
    from_grid_to_shapefile_points([grid_list], jr_1_grid_z, output_folder, output_name_jr1, output_number)

# Wanneer het grid nieuw moet worden gemaakt:
else:
    jr_1_grid_z, jr_2_grid_z, grid_x, grid_y = interpol_elec_data(jr_1_point_col, jr_2_point_col, gridcel)
    # Opslaan van interpolatie naar shapefile
    from_grid_to_shapefile_points([grid_x, grid_y], jr_1_grid_z, output_folder, output_name_jr1, output_number)
    from_grid_to_shapefile_points([grid_x, grid_y], jr_2_grid_z, output_folder, output_name_jr2, output_number)