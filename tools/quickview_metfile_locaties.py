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
    for k in list_properties:
        properties_dict[k] = []

    # Take each metfile and store the information
    for eachfile in list_metfile_names:
        # Check whether it a metfile is or not
        if eachfile[-3:] == 'met' or eachfile[-3:] == 'MET':
            path_metfile = eachfile
            with open (path_metfile, 'r') as metfile:
                print 'Metfile geopend: ', eachfile
                met = metfile.read().replace('\n', '').replace('\r', '')
                ind_profiel = 0
                ind_meting = 0
                # Go through each profile
                while ind_profiel != -1: # Dan is er dus nog een profiel aanwezig
                    # Vind het indices waartussen de informatie staat waarin je geinteresseerd bent
                    ind_profiel = met.find('<PROFIEL>', ind_meting)
                    ind_meting = met.find('<METING>',ind_profiel)
                    if  ind_profiel != -1: # Dan is er dus nog een profiel aanwezig
                        # Krijg de informatie waarin je geinteresserd bent (de eerste regel van het meetprofiel. Hierin staat de algemene
                        # informatie van het meetpunt
                        info = met[ind_profiel+9:ind_meting]
                        naam_metfile = os.path.split(path_metfile)[1]
                        # Voeg de informatie toe aan de dict, zodat je uiteindelijk alle info bij elkaar hebt staan
                        info_samengevoegd = (naam_metfile+','+info).split(',')
                        coordinates = info_samengevoegd[9:11]
                        # Storage of properties in a dict
                        for ind, p in enumerate(list_properties):
                            properties_dict[p].append(info_samengevoegd[ind])
                        # Add the info and coordinates to list
                        info_list.append({'geometry': {'type': 'Point',
                                                          'coordinates': (float(coordinates[0]),float(coordinates[1]))},
                                          'properties': properties_dict})
            metfile.close()

    # Now you have all the information you are interested in in a list
    # Restore those in a memcollection

    point_col.writerecords(info_list)
    return point_col