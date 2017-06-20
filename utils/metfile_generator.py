import json
import csv
import os.path

from collection import MemCollection, OrderedDict

import logging
log = logging.getLogger(__name__)


def export_points_to_metfile(point_col, metfile_name):
    """ export content of point collection with appropriate attributes to 
    metfile in dicts
    
    receives collection of points with project and profile info, and point 
    specific data:
    - profiel
    - datetime 
    - code
    - opnamepeil
    - distance
    - x_coord -> x coordinate of point
    - y_coord -> y coordinate of point
    - lowerlevel -> height of soil in mNAP
    - upperlevel -> height of top of sediment in mNAP
    
    and file location + name for metfile
    
    returns csv file in metfile dialect"""
    
    # Oplossen met writer = csv.DictWriter en aantal benodigde kolommen? ????

    metfile_csv = metfile_name
    with open(metfile_csv, 'wb') as csvfile:
     
        fieldnames = ['regel']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|',
                                quoting=csv.QUOTE_NONE,
                                quotechar='', escapechar='\\')
        
        # wegschrijven project data in REEKS
        project =  str(point_col[0]['properties']['project'])
        project_tekst = ('<REEKS>' + project + ',' + project + ',</REEKS>')
        writer.writerow({'regel': project_tekst})
        
        current_profile = ''
        profiel_eind = '</PROFIEL>'
        
        for i, row in enumerate(point_col):
            profiel = str(point_col[i]['properties']['profiel'])
            datum = (str(point_col[i]['properties']['datetime']))[:10]
            code = (str(point_col[i]['properties']['code']))[:2]
                
            
            x_coord = str(point_col[i]['properties']['x_coord'])
            y_coord = str(point_col[i]['properties']['y_coord'])
            upper_level = str(point_col[i]['properties']['upperlevel'])
            lower_level = str(point_col[i]['properties']['lowerlevel'])                      
            
            # check nieuw profiel
            if current_profile <> profiel:
                
                # check niet eerste profiel -> dan vorige profiel nog afsluiten
                if current_profile <> '':                                      
                    writer.writerow({'regel': profiel_eind})
                
                # wegschrijven profielregel
                profiel_tekst = ('<PROFIEL>' + profiel + ',' + profiel + ',' + 
                            datum + ',' + '0.00,NAP,ABS,2,XY,' + x_coord + ',' + 
                            y_coord + ',')
                                  
                writer.writerow({'regel': profiel_tekst})
                current_profile = profiel
            
            # wegschrijven meting regels   
            meting_tekst = ('<METING>' + code + ',' + '999' + ',' +
                            x_coord + ',' + y_coord + ',' +
                            upper_level + ',' + lower_level + ',</METING>')
            writer.writerow({'regel': meting_tekst})
        
        writer.writerow({'regel': profiel_eind})
    
    return
    