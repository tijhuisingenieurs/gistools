from shapely.geometry import Point

from gistools.utils.collection import MemCollection


def elec_punt_to_profiel(lijn, points_col, naam, zoekafstand):
    '''Deze functie zoekt punten bij een lijn, die binnen de zoekafstand vallen.
    Vervolgens worden er ter hoogte van de gevonden punten per cluster 1 punt op de lijn gemaakt.
    Bij dit punt wordt de gemeten z-waarde gemiddeld. Deze punten worden teruggegeven
    input:
    lijn = shapely linestring,
    points_col = memcollection met punten erin, minimaal per punt een z-waarde meegegeven,
    naam = profielnaam string,
    zoekafstand = int, waarde voor radius buffer waarin per profiel de meetpunten worden gezocht
    returns: een list met daarin per punt een dict. In deze dict staan: de profielnaam, coordinaten van het punt,
    gemiddelde z-waarde, code, afstand tov begin van de lijn, aantal meetpunten per cluster, profielnaam'''

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
            afstand = round(dist_on_line, 1)  # Op 1 decimaal is dus 10 cm uit elkaar
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
            z_gemiddeld = som_z / aantal_p
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

    # Toevoegen van 22 punten. Neem voor nu het begin en eindpunt als 22 punt
    # Zorg ervoor dat het waterpeil (de z waarde) gelijk is, kies het hoogste waarde
    z_22 = max(z_max_afstand, z_min_afstand) + 0.05
    # Het eerste 22 punt is aan het eind van de lijn op een afstand -0.1m (NOG IMPLEMENTEREN!)
    plek_punten_list.append(
        {'geometry': dict(type='Point', coordinates=(lijn.coords.xy[0][0], lijn.coords.xy[1][0])),
         'properties': dict(z=z_22, afstand=0, aantal=-1, code='22', prof_ids=naam)}
    )

    # Het tweede 22 punt is aan het eind van de lijn op een afstand +0.1m (NOG IMPLEMENTEREN)
    plek_punten_list.append(
        {'geometry': dict(type='Point', coordinates=(lijn.coords.xy[0][1], lijn.coords.xy[1][1])),
         'properties': dict(z=z_22, afstand=lijn.length, aantal=-1, code='22', prof_ids=naam)}
    )

    # Geef terug de plek van het gemiddelde punt
    return plek_punten_list


def get_elec_meetpunten_profielen_all(lijn_list, elek_punten_col, zoekafstand):
    '''Deze functie gaat alle profiellijnen af en vindt voor elke lijn de meetpunten die in de buurt liggen.
    Hiervoor wordt gebruikt gemaakt van de functie elec_punt_to_profiel
    input:
    lijn_lijst = list met daarin list van profiel naam en shapely linestring van het profiel
    elek_punten_col = memcollection met meetpunten, per meetpunt minimaal een z-waarde meegegeven
    zoekafstan = int met daarin de afstand waarbinnen de meetpunten van de profielen wordt gezocht

    returns: list met daarin dicts met de meetpunten'''
    # Ga elke lijn af en vind de meetpunten uit de electronische gegevens. En zet die als punten op de lijn.
    gemiddeld_punt_all = []
    for gegevens in lijn_list:
        lijn = gegevens[1]
        prof_ids = gegevens[0]
        # Zoek welke elektronische meetpunten binnen de zoekafstand vallen,
        # Cluster deze punten en neem de gemiddelde z waarde. Ze komen terug in memcollection op 1 gezamelijk punt
        gemiddeld_punt_deel = elec_punt_to_profiel(lijn, elek_punten_col, prof_ids, zoekafstand)
        # Voeg alle punten toe aan 1 list
        gemiddeld_punt_all += gemiddeld_punt_deel
    return gemiddeld_punt_all
