
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



# Van GIS shape naar Array

# Maken van groot grid, waarin beide jaren invallen - gridafstand mee kunnen geven

# Interpolatie jaar 1

# Interpolatie deel 2

# Berkenen van slibaanwas (jaar2-jaar1)

# Wil je uiteindelijk een soort gemiddelde van de binnenkant van de watergang?
# Dan handig om in een nieuwe tool een dwarsdoorsnede te kunnen maken van het grid, en deze als profielpunten te
# genereren. Dan kan je de andere tool gebruiken om per watergang de aanwas te berekenen.
# Zou dat niet sowieso handiger zijn eerst te maken?

# Output:
# Shape van het grid met de slibaanwas
# shape van de interpolatie jaar1
# shape van de interpolatie jaar2



import arcpy
from shapely.geometry import LineString, Point, MultiPoint
from gistools.utils.collection import MemCollection
# Tool 2: het maken van een puntenprofiel ahv lijn door electronische datawolk
input_lijnen = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\profielijn.shp'
input_punten = 'C:\Users\elma\Documents\GitHub\Test_data_werking_tools\Elektronische_data_interpolatie\Testdata\Meetpunten_elektronisch_test.shp'

# De functies om van arcgis naar python te gaan en terug
# Zet de profielpunten om naar een shapely multi points
z_waardes = []
punten = []

rows_in = arcpy.SearchCursor(input_punten)
fields_in = arcpy.ListFields(input_punten)
# Ga de input af en sla de punten op in Points
for row in rows_in:
    geom = row.getValue('SHAPE')
    punten.append(Point(geom.firstPoint.X, geom.firstPoint.Y))
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
            if key == 'z': # Sla de z-waardes op in een list
                z_waardes.append(value)
# Maak multipoints van de punten om dadelijk spatial actions te kunnen uitvoeren
punten_multi = MultiPoint(punten)

# Zet de profiellijnen om naar shapely linestrings
# ---------- Omzetten van shapefile input naar dict----------------
lijn_dict = {}
rows_in = arcpy.SearchCursor(input_lijnen)
fields_in = arcpy.ListFields(input_lijnen)
# Ga de input af en sla de geom op in dict
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
            if key == 'prof_ids': # Neem de prof_ids als key en sla de geom op
                lijn_dict[value] = [LineString([(geom.firstPoint.X,geom.firstPoint.Y), (geom.lastPoint.X, geom.lastPoint.Y)])]

# Maak een buffer van de lijn
for profielnaam in lijn_dict.keys():
    lijn = lijn_dict[profielnaam][0]
    lijn_buffer = lijn.buffer(0.1)
    punten_lijn = lijn_buffer.intersects(punten_multi)
    print profielnaam
# Vind de punten in de buffer

# Wellicht is het beter om er toch een memcollection van de punten te maken, anders moet je alle punten af en met de
# memcollection zit er in ieder geval nog een beetje een spatial filter op.
for p in point_col_mid_uit.filter(
                bbox=buffer_p.bounds):  # hier wordt spatial indexing van memcollection gebruikt
            punt_uit = Point(p['geometry']['coordinates'])
            if punt_uit.within(buffer_p):

# maak van die punten een buffer

# Vind de clusters van punten

# Maak 1 punt op de lijn met het gemiddelde van het cluster

# Bereken de afstand van de punten op de lijn

# Voeg 22 punten toe aan uiteinde van de lijn, en daarbij de waarde van z +0.2 ofzo. (testen)

# Sla de punten op als shapefile met devolgende kolommen:
# prof_ids, datum, code, afstand, x_coord, y_coord, _bk_nap

# Dan kun je deze profielen gebruiken in de slibaanwas tool.