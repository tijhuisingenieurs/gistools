import os
import os.path

from shapely.geometry import Point, Polygon

from gistools.utils.collection import MemCollection

def get_profiel_middelpunt(point_col_in, point_col_uit):
    ''' Deze functie maakt van de metingen een overzicht van de profielen en een middelpunt.
         Het middelpunt kan later gebruikt worden voor het vinden van het dichtsbijzijnde profiel.
         input: point_col_in(memcollection punten inpeiling), point_col_uit(memcollection punten uitpeiling)
         return:
         pointcollection middelpunten van de inpeilingen, pointcollection middelpunten van de uitpeilingen,
         list van de profielnamen van de inpeilingen, list van de profielnamen van de uitpeilingen'''

    # ---------- Get unieke waardes van profielnamen en hun middelpunt----------------
    # --- Van de inpeilingen
    profiel_namen_in = set(p['properties']['prof_ids'] for p in point_col_in.filter())

    # Initialize point collection -> middelpunten (inpeilingen)
    point_col_mid_in = MemCollection(geometry_type='MultiPoint')
    records_mid_in = []

    # Vindt voor elk profiel het middelste meetpunt
    for profiel in profiel_namen_in:
        profiel_punten = list(point_col_in.filter(property={'key': 'prof_ids', 'values': [profiel]}))
        middelpunt_nr = int(round(len(profiel_punten) / 2, 0))
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
        profiel_punten = list(point_col_uit.filter(property={'key': 'prof_ids', 'values': [profiel]}))
        middelpunt_nr = int(round(len(profiel_punten) / 2, 0))
        middelpunt = profiel_punten[middelpunt_nr]
        records_mid_uit.append(middelpunt)

    # sla deze middelpunten op in een memcollection
    point_col_mid_uit.writerecords(records_mid_uit)

    return point_col_mid_in, point_col_mid_uit, profiel_namen_in, profiel_namen_uit


def get_profiel_middelpunt_oud(input_inpeil, input_uitpeil):
    ''' Deze functie maakt van de metingen een overzicht van de profielen in deze shape en een middelpunt.
     Het middelpunt kan later gebruikt worden voor het vinden van het dichtsbijzijnde profiel.
     input: input_inpeil(shapefile), input_uitpeil(shapefile)
     return:
     pointcollection input inpeilingen, pointcollection input uitpeilingen,
     pointcollection middelpunten van de inpeilingen, pointcollection middelpunten van de uitpeilingen,
     list van de profielnamen van de inpeilingen, list van de profielnamen van de uitpeilingen'''

    # ---------- Omzetten van shapefile input naar memcollection----------------
    # --- Initialize point collection -> inpeilingen
    import arcpy

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

    # --- Initialize point collection -> uitpeilingen
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
        middelpunt_nr = int(round(len(profiel_punten) / 2, 0))
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
        profiel_punten = list(point_col_uit.filter(property={'key': 'prof_ids', 'values': [profiel]}))
        middelpunt_nr = int(round(len(profiel_punten) / 2, 0))
        middelpunt = profiel_punten[middelpunt_nr]
        records_mid_uit.append(middelpunt)

    # sla deze middelpunten op in een memcollection
    point_col_mid_uit.writerecords(records_mid_uit)

    return point_col_in, point_col_uit, point_col_mid_in, point_col_mid_uit, profiel_namen_in, profiel_namen_uit


def create_buffer(point_col, radius=5):
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
        records.append([profielnaam, buffered])

    return records


def calc_slibaanwas_polygons(point_list_in, point_list_uit, tolerantie_breedte, tolerantie_wp, meter_factor=-1):
    '''Deze functie berekent de slibaanwas tussen 2 profielen. Hierbij worden polygonen gebruikt.
    Het heeft de inpeiling als basis. De profielen worden beide vanaf het middelpunt getekend.
    input: list van 1 profiel inpeiling, list van 1 profiel uitpeiling, meter_factor(aantal meters vanaf
    de eerste meting, welke mee wordt genomen in de slibaanwas berekening (dus meters vanaf kant) Als er geen positieve
    meters wordt meegegeven, neem 10% van de breedte), tolerantie_breedte (waarde van verschil in breedte, wanneer deze
    waarde wordt overschreden wordt er geen slib berekend), tolerantie_wp (waarde van verschil in waterpeil, wanneer
    deze waarde wordt overschreden wordt er geen slib berekend)
    return: waarde van de hoeveelheid slibaanwas'''

    # parameters om de gegevens in op te slaan
    afstand_in = []
    afstand_uit = []
    bk_in = []
    bk_uit = []
    ind_22_in = []
    ind_22_uit = []
    coor_in = []
    coor_uit = []

    # Parameters voor de output
    slibaanwas_lengte = 999
    box_lengte = 999
    breedte_verschil = 999
    errorwaarde = None

    # ------- Inlezen van de gegegens
    # Get de meetpuntgegevens van de inpeiling: de meetafstand en de bovenkant slip in NAP en de index van het 22 punt
    for ind, meetpunt in enumerate(point_list_in):
        afstand_in.append(meetpunt['properties']['afstand'])
        bk_in.append(meetpunt['properties']['_bk_nap'])
        coor_in.append((meetpunt['properties']['afstand'], meetpunt['properties']['_bk_nap']))
        if meetpunt['properties']['code'] == '22':
            ind_22_in.append(ind)

    # Get de meetpuntgegevens van de uitpeiling: de meetafstand en de bovenkant slip in NAP en de index van het 22 punt
    for ind, meetpunt in enumerate(point_list_uit):
        afstand_uit.append(meetpunt['properties']['afstand'])
        bk_uit.append(meetpunt['properties']['_bk_nap'])
        coor_uit.append((meetpunt['properties']['afstand'], meetpunt['properties']['_bk_nap']))
        if meetpunt['properties']['code'] == '22':
            ind_22_uit.append(ind)

    # ------- Check of de gegevens goed zijn ------
    # Check of er twee 22-codes zijn -> zo niet stop de berekening
    if len(ind_22_uit) < 2 or len(ind_22_in) < 2:
        errorwaarde = '22code'
        return slibaanwas_lengte, box_lengte, meter_factor, breedte_verschil, errorwaarde

    # Check of de profielbreedtes niet te veel verschillen -> teveel verschil stop de berekening
    breedte_verschil = abs(afstand_in[ind_22_in[1]] - afstand_uit[ind_22_uit[1]])
    if breedte_verschil > tolerantie_breedte:
        errorwaarde = 'breedteverschil'
        return slibaanwas_lengte, box_lengte, meter_factor, breedte_verschil, errorwaarde

    # Check of de waterpeil veel verschilt -> teveel verschil stop de berekening
    wp_verschil_22L = abs(bk_in[ind_22_in[0]] - bk_uit[ind_22_uit[0]])
    wp_verschil_22R = abs(bk_in[ind_22_in[1]] - bk_uit[ind_22_uit[1]])
    if wp_verschil_22L > tolerantie_wp or wp_verschil_22R > tolerantie_wp:
        errorwaarde = 'waterpeilverschil'
        return slibaanwas_lengte, box_lengte, meter_factor, breedte_verschil, errorwaarde

    # Pas de meter_factor aan als percentage van de breedte
    # Als er geen positieve meters wordt meegegeven, neem 10% van de breedte
    if meter_factor == -1:
        meter_factor = afstand_in[ind_22_in[1]] * 0.1

    # -------- Maak polygons -------------------
    # Om de middelpunten van de polygonen gelijkt te hebben, verschuif de uitpeiling naar de inpeiling
    verschuif = (afstand_in[ind_22_in[1]] / 2) - (afstand_uit[ind_22_uit[1]] / 2)
    for ind, coordinate in enumerate(coor_uit):
        afstand, waarde = coordinate
        coor_uit[ind] = (afstand + verschuif, waarde)

    # Polygons van de in- en uitpeiling
    poly_in = Polygon(coor_in[ind_22_in[0]:ind_22_in[1] + 1])
    poly_uit = Polygon(coor_uit[ind_22_uit[0]:ind_22_uit[1] + 1])

    # Polygon vierkant (nodig voor berekening slib)
    # Bereken vanaf het 22 punt de bounding box met daarbij de meters vanaf de kant
    afstand_begin = afstand_in[ind_22_in[0]] + meter_factor
    afstand_eind = afstand_in[ind_22_in[1]] - meter_factor
    waterlijn = min(bk_in[ind_22_in[0]], bk_uit[ind_22_in[0]]) - 0.01  # Zorg dat het vierkant onder de waterlijn ligt
    onderlijn = min(bk_uit) - 0.5  # Zorg dat het vierkant onder de onderlijn ligt

    poly_square = Polygon([(afstand_begin, waterlijn), (afstand_begin, onderlijn), (afstand_eind, onderlijn),
                           (afstand_eind, waterlijn)])

    # Check of de polygons geen dubbele lijnen hebben/valid zijn ( anders kan de difference niet berekend worden)
    # Zo wel oplossen door het om te zetten naar een zeer kleine buffer. Wanneer het dan nog steeds fout is, dan
    # moet er verder naar gekeken worden.
    if (poly_square.is_valid and poly_in.is_valid and poly_uit.is_valid) is False:
        if poly_uit.is_valid is False:
            poly_uit = poly_uit.buffer(0.00001)
        if poly_in.is_valid is False:
            poly_in = poly_in.buffer(0.00001)
        if (poly_square.is_valid and poly_in.is_valid and poly_uit.is_valid) is False:
            errorwaarde = 'invalid polygon'
            return slibaanwas_lengte, box_lengte, meter_factor, breedte_verschil, errorwaarde

    # # ------- Bereken hoeveelheid slib binnen box van interest -------------
    # Slib in de inpeiling
    slib_in = poly_square.difference(poly_in).area
    # Slib in de uitpeiling
    slib_uit = poly_square.difference(poly_uit).area

    # Hoeveelheid slib in m2 in het hele profiel
    slibaanwas_totaal = slib_in - slib_uit
    # Hoeveelheid slib in m per lengte-eenheid
    box_lengte = afstand_eind - afstand_begin
    slibaanwas_lengte = slibaanwas_totaal / ((box_lengte))

    # # ------- Test figures om de dataset te bekijken
    # print(point_list_in[0]['properties']['prof_ids'])
    # x_in, y_in = poly_in.exterior.xy
    # x_uit, y_uit = poly_uit.exterior.xy
    # x_square, y_square = poly_square.exterior.xy
    # plt.figure()
    # plt.title('{0}'.format(point_list_in[0]['properties']['prof_ids']))
    # plt.plot(x_in, y_in,'r')
    # plt.hold(True)
    # plt.plot(x_uit, y_uit,)
    # plt.plot(x_square,y_square,'g')
    # plt.hold(False)
    # plt.show()
    return slibaanwas_lengte, box_lengte, meter_factor, breedte_verschil, errorwaarde


def get_slibaanwas(point_col_in, point_col_uit, point_col_mid_uit, buffer_list, tolerantie_breedte, tolerantie_wp):
    '''Deze funtie zoekt bij elke inpeiling een uitpeiling en berekent dan het verschil in slib (de slibaanwas)
    input:
    memcollection van de inpeilingen
    memcollection van de uitpeilingen
    memcollection van de middenpunten van de uitpeilingen
    list met bufferpolygons en profielnamen inpeilingen
    meter_factor (nog in aanmaak)

    result: memcollection lines met bij elke inpeilingprofiellijn een slibaanwas en de meter_factor vermeld.'''
    in_uit_combi = []
    slibaanwas_all = []
    box_lengte_all = []
    meter_factor_all = []
    datum_in_all = []
    datum_uit_all = []
    breedte_verschil_all = []
    coordinates_in_all = []
    afstand_all = []
    errorwaarde_all = []

    # Vind bij elk profiel van de inpeilingen de uitpeiling die binnen de buffer valt,
    # en check welke het dichstbijzijnde is
    for profiel_naam, buffer_p in buffer_list:
        afstand_temp = 1000
        uitpeiling_aanwezig = False
        for p in point_col_mid_uit.filter(bbox=buffer_p.bounds):#hier wordt spatial indexing van memcollection gebruikt
            punt_uit = Point(p['geometry']['coordinates'])
            if punt_uit.within(buffer_p):
                uitpeiling_aanwezig = True
                if buffer_p.centroid.distance(punt_uit) < afstand_temp:  # check of het de dichtstbijzijnde is
                    profiel_naam_temp = profiel_naam
                    properties_temp = p['properties']['prof_ids']
                    afstand_temp = buffer_p.centroid.distance(punt_uit)
        if uitpeiling_aanwezig:  # check of er inderdaad een profiel is gevonden, dan sla de dichtstbijzijnde info op
            in_uit_combi.append([profiel_naam_temp, properties_temp])
            coordinates_in_all.append(buffer_p.centroid.coords[0])
            afstand_all.append(afstand_temp)

    # Ga elk profiel af en bereken de slibaanwas en verzamel info voor de output
    for prof_in, prof_uit in in_uit_combi:
        prof_list_in = list(point_col_in.filter(property={'key': 'prof_ids', 'values': [prof_in]}))
        prof_list_uit = list(point_col_uit.filter(property={'key': 'prof_ids', 'values': [prof_uit]}))
        slibaanwas_profiel, box_lengte, meter_factor, breedte_verschil, errorwaarde = \
            calc_slibaanwas_polygons(prof_list_in, prof_list_uit, tolerantie_breedte, tolerantie_wp)
        slibaanwas_all.append(slibaanwas_profiel)
        box_lengte_all.append(box_lengte)
        meter_factor_all.append(meter_factor)
        breedte_verschil_all.append(breedte_verschil)
        datum_in_all.append(prof_list_in[0]['properties']['datum'])
        datum_uit_all.append(prof_list_uit[0]['properties']['datum'])
        errorwaarde_all.append(errorwaarde)

    # sla de gegevens op in een dict om straks op te slaan in een shapefile
    info_list = {}
    info_list['geometrie'] = coordinates_in_all
    info_list['slibaanwas'] = slibaanwas_all
    info_list['box_lengte'] = box_lengte_all
    info_list['datum_in'] = datum_in_all
    info_list['datum_uit'] = datum_uit_all
    info_list['meter_factor'] = meter_factor_all
    info_list['breedte_verschil'] = breedte_verschil_all
    info_list['errorwaarde'] = errorwaarde_all
    info_list['afstand'] = afstand_all

    return in_uit_combi, info_list
