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


def from_grid_to_shapefile_points(x_coordinaten, y_coordinaten, z_waardes, output_folder, output_name, output_number):
    '''functie om de grid met punten naar arcgis te halen'''

    # Initializatie van het path en naam output en shapefile
    output_dir = os.path.dirname(output_folder)
    output_file = arcpy.CreateFeatureclass_management(output_dir, output_number + '_' + output_name, 'POINT',
                                                      spatial_reference=28992)
    arcpy.AddMessage('Outputname: ' + output_name)
    arcpy.AddMessage('Output: ' + output_file)

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
        x_waarde = x_coordinaten[ind[1]]
        y_waarde = y_coordinaten[ind[0]]

        row = dataset.newRow()
        point = arcpy.Point(x_waarde,y_waarde)
        row.Shape = point

        # Voeg de properties toe aan de attribuuttable
        row.setValue('_bk_nap', p)
        row.setValue('x_coord', x_waarde)
        row.setValue('y_coord', y_waarde)
        # row.setValue('datum')

        dataset.insertRow(row)


input_jaar_1 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\elec_jaar1_test.shp'
input_jaar_2 = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\elec_jaar2_test.shp'
output_folder = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata'
output_name = 'Test_grid_interpolatie'
output_number = str(np.random.random_integers(1, 100))
gridcel = 0.5

# Deze tool gaat de slibaanwas van de elektronische data berekenen.
# Hiervoor wordt eerts de data geinterpoleerd op een grid.
# Vervolgens kan dan de slibaanwas worden berekend.

# Vragen:
# Wil je vooraf de verschillende jaren bij elkaar zoeken en dan hetzelfde grid interpoleren?
# dat is wel handig... Ze staan per locatie opgeslagen in 1 shape!!! Dus inderdaad per meetlocatie doen.
# Wellicht handig om het zo te maken dat ie zelf de shapefiles uit een map kan lezen en tegelijk kan uitvoeren,
# dus dat je niet voor elke locatie de tool zelf moet aanzetten.

# Moeten de gemeten punten op het interpolatiegrid liggen?
# Grid afstand 50 cm. (of kan het nog kleiner? Daarmee testen)

# Van GIS shape naar memcollection
# --------- Inlezen jaar 1
jr_1_point_col = from_shape_to_memcollection_points(input_jaar_1)

# --------- Inlezen jaar 2
jr_2_point_col = from_shape_to_memcollection_points(input_jaar_2)


# Initializatie
jr_1_point_list = []
jr_2_point_list = []
jr_1_z = []
jr_2_z = []
jr_1_x = []
jr_1_y = []


# Zet de gegevens om in een array
# ---------- Jaar 1
for p in jr_1_point_col.filter():
    coordinaten = p['geometry']['coordinates']
    z_waarde = p['properties']['z']
    jr_1_point_list.append(coordinaten)
    jr_1_z.append(z_waarde)
    jr_1_x.append(coordinaten[0])
    jr_1_y.append(coordinaten[1])

# ---------- Jaar 2
for p in jr_2_point_col.filter():
    coordinaten = p['geometry']['coordinates']
    z_waarde = p['properties']['z']
    jr_2_point_list.append(coordinaten)
    jr_2_z.append(z_waarde)

# Krijg de coordinaten van de boundingbox van beide jaren. Neem de uiterste coordinaten voor de interpolatie grid
# col.bounds geeft list(minx, miny, maxx, maxy)
jr_1_bbox = jr_1_point_col.bounds
jr_2_bbox = jr_2_point_col.bounds
#
# x_max_coor = int(round(max(jr_1_bbox[2], jr_2_bbox[2])*100))
# x_min_coor = int(round(min(jr_1_bbox[0], jr_2_bbox[0])*100))
# y_max_coor = int(round(max(jr_1_bbox[3], jr_2_bbox[3])*100))
# y_min_coor = int(round(min(jr_1_bbox[1], jr_2_bbox[1])*100))

x_max_coor = max(jr_1_bbox[2], jr_2_bbox[2])
x_min_coor = min(jr_1_bbox[0], jr_2_bbox[0])
y_max_coor = max(jr_1_bbox[3], jr_2_bbox[3])
y_min_coor = min(jr_1_bbox[1], jr_2_bbox[1])

# Je wilt een list maken met de waardes voor het grid, in x en y richting
aantal_punten_x = int((x_max_coor-x_min_coor)/gridcel)
x_waarde = x_min_coor
x_values = []
for punten in range(1,aantal_punten_x+1,1):
    x_waarde += gridcel
    x_values.append(x_waarde)

aantal_punten_y = int((y_max_coor - y_min_coor) / gridcel)
y_waarde = y_min_coor
y_values = []
for punten in range(1, aantal_punten_y + 1, 1):
    y_waarde += gridcel
    y_values.append(y_waarde)

k = 0

# Maken van groot grid, waarin beide jaren invallen - gridafstand mee kunnen geven
# Voor de functie range is een integer nodig, maar het grid wil ik wel met een float
# x_values = np.array(range(x_min_coor,x_max_coor, gridcel))/100
# y_values = np.array(range(y_min_coor,y_max_coor, gridcel))/100

# Maken van grid ahv max en min coodrinates
grid_x, grid_y = np.meshgrid(x_values,y_values)

# Interpolatie jaar 1
jr_1_interpol = griddata(np.array(jr_1_point_list), np.array(jr_1_z), (grid_x,grid_y), method='cubic', fill_value=999)

# write outcome interpolation to shapfile


plt.figure()
plt.contourf(grid_x,grid_y, jr_1_interpol)

plt.figure()
plt.scatter(jr_1_x,jr_1_y, c=jr_1_z)

plt.show()

k = 2


# Opslaan van interpolatie naar shapefile
from_grid_to_shapefile_points(jr_1_x, jr_1_y, jr_1_interpol,output_folder,output_name,output_number)

k=3
# Interpolatie deel 2

# Berkenen van slibaanwas (jaar2-jaar1)

# Output:
# Shape van het grid met de slibaanwas
# shape van de interpolatie jaar1
# shape van de interpolatie jaar2






















