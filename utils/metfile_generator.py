import json
import csv
import os.path

from collection import MemCollection, OrderedDict

import logging
log = logging.getLogger(__name__)


def export_points_to_metfile(point_col, project, metfile_name):
    """ export content of point collection with appropriate attributes to 
    metfile in dicts
    
    receives collection of points with project and profile info, and point 
    specific data, at least:                    
    - profile name (prof_ids)
    - datetime (datum)
    - code
    - distance (afstand)
    - x_coord -> x coordinate of point
    - y_coord -> y coordinate of point
    - _bk_nap -> height of soil in mNAP
    - _ok_nap -> height of top of sediment in mNAP
    
    and file location + name for metfile
    
    returns csv file in metfile dialect"""
    
    with open(metfile_name, 'wb') as csvfile:
     
        fieldnames = ['regel']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|',
                                quoting=csv.QUOTE_NONE,
                                quotechar='', escapechar='\\')
        
        # wegschrijven project data in REEKS
        project_tekst = ('<REEKS>' + project + ',' + project + ',</REEKS>')
        writer.writerow({'regel': project_tekst})
        
        current_profile = ''
        profiel_eind = '</PROFIEL>'
        
        unsorted_points = [p for p in point_col]
        sorted_points = sorted(unsorted_points, key = lambda x: (x['properties']['prof_ids'], x['properties']['afstand']))
        
        for i, row in enumerate(sorted_points):
            profiel = str(sorted_points[i]['properties']['prof_ids'])
            datum = (str(sorted_points[i]['properties']['datum']))[:10]
            code = (str(sorted_points[i]['properties']['code']))[:2]
                
            
            x_coord = str(sorted_points[i]['properties']['x_coord'])
            y_coord = str(sorted_points[i]['properties']['y_coord'])
            upper_level = str(sorted_points[i]['properties']['_bk_nap'])
            lower_level = str(sorted_points[i]['properties']['_ok_nap'])                      
            
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
    