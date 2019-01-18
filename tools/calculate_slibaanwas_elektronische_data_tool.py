import numpy as np
from scipy.interpolate import griddata
from gistools.utils.collection import MemCollection
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

def from_shapegrid_to_memcollection_points(input_shape):
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

def from_grid_to_shapefile_points(x_coordinaten, y_coordinaten, z_waardes, output_folder, output_name, output_number):
    '''functie om de grid met punten naar arcgis te halen'''

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
    # arcpy.AddField_management(output_file, 'datum', "TEXT")
    dataset = arcpy.InsertCursor(output_file)
    # gebruik numpy.ndenumerate
    # De punten en de gegevens van de punten overbrengen naar de shapefile
    for ind, p in np.ndenumerate(z_waardes):
        # uitgaande van eregular grid van z-waardes
        x_waarde = x_coordinaten[ind]
        y_waarde = y_coordinaten[ind]

        row = dataset.newRow()
        point = arcpy.Point(x_waarde,y_waarde)
        row.Shape = point

        # Voeg de properties toe aan de attribuuttable
        row.setValue('_bk_nap', p)
        row.setValue('x_coord', x_waarde)
        row.setValue('y_coord', y_waarde)
        # row.setValue('datum')

        dataset.insertRow(row)


# Inpur data voor in PYCHARM
# input_jaar_1 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\elec_jaar1_test.shp'
input_jaar_1 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\simple_grid_elec.shp'
# input_jaar_2 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\elec_jaar2_test.shp'
input_jaar_2 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\simple_grid_jr2.shp'

output_folder = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata'
output_name = 'Test_grid_real'#'Test_grid_interpolatie'

output_name_jr1 = 'Test_grid_jr_1'
output_name_jr2 = 'Test_grid_jr_2'
output_name_verschil = 'Test_grid_verschil'
output_number = str(np.random.random_integers(1, 100))
gridcel = 0.5

# input_jaar_2 = input_jaar_1

# Deze tool gaat de slibaanwas van de elektronische data berekenen.
# Hiervoor wordt eerts de data geinterpoleerd op een grid.
# Vervolgens kan dan de slibaanwas worden berekend.

# ---------------- START CODE -----------------------------

def interpol_elec_data(jr_1_point_col, jr_2_point_col, gridcel):
    '''Deze functie maakt een interpolatie van de ingegeven data. Deze input data zijn point collections van
    electronische data. Waarbij beide datasets hetzelfde gebied weergeven. De interpolatie wordt voor beide
    uitgevoerd over hetzelfde grid.
    Dit grid is ofwel nieuw:
    Er wordt een grid gemaakt ahv de grootst mogelijke bounding box van de input data en een
    grid afstand.
    ofwel gebasseerd op een grid die door deze tool al is gemaakt (dus wanneer deze tool meerdere keren wordt gerund.
     In dit laatste geval wordt alleen jr_1_point_col geinterpoleerd, de gegevens van jr_2_point_col worden gebruikt
     voor het grid.

    Het resultaat is een shapefile (punten) op het grid geinterpoleerd. Punten zonder interpolatie hebben de waarde
    999. Dit zijn de punten buiten de exterior van de point_col.'''

    # Initializatie
    jr_1_point_list = []
    jr_2_point_list = []
    jr_1_z = []
    jr_2_z = []
    jr_1_x = []
    jr_1_y = []
    jr_2_x = []
    jr_2_y = []


    # Zet de gegevens om in een array
    # ---------- Jaar 1 --------------
    for p in jr_1_point_col.filter():
        coordinaten = p['geometry']['coordinates']
        z_waarde = p['properties']['z']
        jr_1_point_list.append(coordinaten)
        jr_1_z.append(float(z_waarde))
        jr_1_x.append(coordinaten[0])
        jr_1_y.append(coordinaten[1])

    # ---------- Jaar 2 ---------------
    for p in jr_2_point_col.filter():
        coordinaten = p['geometry']['coordinates']
        if gridcel != -1:
            z_waarde = p['properties']['z']
        else:
            z_waarde = p['properties']['_bk_nap']
        jr_2_point_list.append(coordinaten)
        jr_2_z.append(z_waarde)
        jr_2_x.append(coordinaten[0])
        jr_2_y.append(coordinaten[1])

    # Bepaal of er een nieuw grid moet worden aangemaakt.
    if gridcel != -1:
        # Krijg de coordinaten van de boundingbox van beide jaren. Neem de uiterste coordinaten voor het grid
        # col.bounds geeft list(minx, miny, maxx, maxy)
        jr_1_bbox = jr_1_point_col.bounds
        jr_2_bbox = jr_2_point_col.bounds

        x_max_coor = max(jr_1_bbox[2], jr_2_bbox[2])
        x_min_coor = min(jr_1_bbox[0], jr_2_bbox[0])
        y_max_coor = max(jr_1_bbox[3], jr_2_bbox[3])
        y_min_coor = min(jr_1_bbox[1], jr_2_bbox[1])

        # Je wilt een list maken met de waardes voor het grid, in x en y richting
        # Waardes voor het x-grid
        aantal_punten_x = int((x_max_coor-x_min_coor)/gridcel)
        x_waarde = x_min_coor
        x_values = []
        for punten in range(0, aantal_punten_x+1,1):
            if punten == 0:
                x_values.append(x_waarde)
            else:
                x_waarde += gridcel
                x_values.append(x_waarde)

        # Waardes voor het y-grid
        aantal_punten_y = int((y_max_coor - y_min_coor) / gridcel)
        y_waarde = y_min_coor
        y_values = []
        for punten in range(0, aantal_punten_y + 1, 1):
            if punten == 0:
                y_values.append(y_waarde)
            else:
                y_waarde += gridcel
                y_values.append(y_waarde)

        # Maken van grid
        grid_x, grid_y = np.meshgrid(x_values,y_values)

        # Interpolatie jaar 1
        jr_1_grid_z = griddata(np.array(jr_1_point_list), np.array(jr_1_z), (grid_x,grid_y), method='cubic', fill_value=999)

        # Interpolatie jaar 2
        jr_2_grid_z = griddata(np.array(jr_2_point_list), np.array(jr_2_z), (grid_x,grid_y), method='cubic', fill_value=999)

        return [jr_1_grid_z, jr_2_grid_z, grid_x, grid_y]

    else:
        # Interpolatie jaar 1 ahv het grid van jaar 2
        jr_1_grid_z = griddata(np.array(jr_1_point_list), np.array(jr_1_z), jr_2_point_list, method='cubic',
                               fill_value=999)
        return [jr_1_grid_z, jr_2_point_list]




    # # Berkenen van slibaanwas (jaar2-jaar1)
    # # Hier wil je nog wat doen met de 999 waardes, die moeten eigenlijk blijven staan!
    # # Kan dat ook op een andere manier dan met een loop?
    # # Anders doe het niet en laat het achteraf zelf in GIS doen, dan kan je selecteren op de lijnen zonder 999 en alleen
    # # die meenemen in de analyse van het berekenen van het slib.
    # verschil_grid_m = jr_2_grid_z - jr_1_grid_z
    #
    # verschil_grid = np.empty(jr_1_grid_z.shape)
    #
    # for ind, value_jr2 in np.ndenumerate(jr_2_grid_z):
    #     value_jr1 = jr_1_grid_z[ind]
    #     if value_jr1 == 999 or value_jr2 == 999:
    #         verschil_grid[ind] = 999
    #     else:
    #         verschil_grid[ind] = value_jr2 - value_jr1
    #
    #
    #
    # # Opslaan van de interpolatie verschil (slibaanwas)
    # from_grid_to_shapefile_points(grid_x, grid_y, verschil_grid,output_folder,output_name_verschil,output_number)
    # from_grid_to_shapefile_points(grid_x, grid_y, verschil_grid_m,output_folder,output_name_verschil + '_m',output_number)
    #

    print output_number
    k=3

    # Vraag: zou je de tool niet zo kunnen maken dat je een grid meegeeft? Dan kan je voor jaar 1 en 2 een grid maken
    # en deze toepassen op jaar 3. Dat is wel een idee! Straks uitvoeren wanneer je arcgistool boorpunten is gemerged,

