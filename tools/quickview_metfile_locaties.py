'''Een metfile wordt ingelezen en per profiel wordt 1 punt gemaakt als shapefile,
Zo heb je een quickview waar de profiellocaties zijn.'''
import os
from gistools.utils.collection import MemCollection

def quickview_metfile_locaties(list_metfile_names):
    # Assign some objects, used to store the information
    info_list = []
    properties_dict = {}
    point_col = MemCollection(geometry_type='Point')
    list_properties = ['Metfile','P_naam','P_naam_2','Datum']

    # Take each metfile and store the information
    for eachfile in list_metfile_names:
        # Check whether it is a metfile or not
        if eachfile[-3:] == 'met' or eachfile[-3:] == 'MET':
            path_metfile = eachfile
            with open (path_metfile, 'r') as metfile:
                print 'Metfile geopend: ', eachfile
                met = metfile.read().replace('\n', '').replace('\r', '')
                ind_meting = 0

                # Split de data op profielniveau
                profielen = met.split('<PROFIEL>')

                # Ga elk profiel af
                for each in profielen[1:]:
                    # Vind het indices waartussen de informatie staat waarin je geinteresseerd bent
                    ind_meting = each.find('<METING>')
                    # Krijg de informatie waarin je geinteresserd bent (de eerste regel van het meetprofiel. Hierin staat de algemene
                    # informatie van het meetpunt
                    info = each[:ind_meting]
                    naam_metfile = os.path.split(path_metfile)[1]
                    # Voeg de informatie toe aan de dict, zodat je uiteindelijk alle info bij elkaar hebt staan
                    info_samengevoegd = (naam_metfile+','+info).split(',')
                    coordinates = info_samengevoegd[9:11]
                    # Storage of properties in a dict
                    for ind, p in enumerate(list_properties):
                        properties_dict = properties_dict.copy()
                        properties_dict[p] = info_samengevoegd[ind]
                    # Add the info and coordinates to list
                    info_list.append({'geometry': {'type': 'Point',
                                                      'coordinates': (float(coordinates[0]),float(coordinates[1]))},
                                      'properties': properties_dict})
            metfile.close()

    # Now you have all the information you are interested in in a list
    # Restore those in a memcollection
    point_col.writerecords(info_list)
    return point_col
