import xml.etree.ElementTree as ET
import os.path

from math import sqrt, pow
from collection import MemCollection, OrderedDict
from gistools.utils.conversion_tools import get_float
from gistools.utils.iso8601 import parse_date

import logging
log = logging.getLogger(__name__)


def import_xml_to_memcollection(xml_file, zvalues):
    """ import content of a xml file with measurement points and attributes
    
    receives file location + name for xml 
            (file with metfile dialect)
            zvalues; order of z-values z1z2 (onderkant_bovenkant) 
                or z2z1 (bovenkant_onderkant)
                or z1 (alleen onderkant)
                or z2 (alleen bovenkant)
    
    returns Memcollection of points with attributes"""
    
    point_col = MemCollection(geometry_type='Point')
    ttlr_col = MemCollection(geometry_type='Point')
    line_col = MemCollection(geometry_type='LineString')

    records_p = []
    records_ttlr = []
    records_l = []   
    records_errors = []     

    pk = 0
    
    # add root element to file for correct parsing
    with open(xml_file, "r") as original:   
        data = original.read() 
    with open(xml_file, "w") as myfile:
        myfile.write('<data>\n' + data)
    with open(xml_file, "a") as myfile:
        myfile.write('\n</data>')


    tree = ET.parse(xml_file)
    root = tree.getroot()

    # remove root element from file to restore original data
    with open(xml_file, "w") as restored:   
        restored.write(data)
        
    for e in root:   
        properties_l = {}
        properties_l['xb_prof'] = 0.0
        properties_l['yb_prof'] = 0.0
        properties_l['xe_prof'] = 0.0
        properties_l['ye_prof'] = 0.0
        
        print ('Element gevonden; ' + str(e.tag) + ' ' +  str(e.text))
        
        if e.tag in ['reeks', 'REEKS', 'Reeks']:
            properties_reeks = {}
            reeks_list = e.text.split(',')
            properties_reeks['project_id'] = reeks_list[0]
            print ('Project informatie gevonden in reeks: ' + str(reeks_list[0]))
        
        if e.tag in ['profiel', 'PROFIEL', 'Profiel']:
            prof_list = e.text.split(',')
            properties_l['ids'] = prof_list[1]
            properties_l['datum'] = prof_list[2]
            properties_l['project_id'] = properties_reeks['project_id']
            

            i = 0
            j = 0   
            pk = pk + 1
            properties_l['pk'] = pk
            
            # Hier eerste door punten loopen om 22L en 22R te vinden ivm:
            # wpeil
            # breedte
            # afstanden voor punten tov 22L
            # dieptes tov wp bij punten
            
            wpeilen_list = []
            t = 0
            properties_l['breedte'] = 999
            
            for p in e:
                point_list = p.text.split(',')
                if point_list[0] == '22':
                    wpeilen_list.append(get_float(point_list[4]))  
                    if  t == 0:
                        nulpunt_x = point_list[2]
                        nulpunt_y = point_list[3]
                    if  t == 1:
                        eindpunt_x = point_list[2]
                        eindpunt_y = point_list[3]
                        properties_l['breedte'] = sqrt(pow(get_float(eindpunt_x) - 
                                                   get_float(nulpunt_x), 2) 
                                               + pow(get_float(eindpunt_y) - 
                                                     get_float(nulpunt_y),2))
                        
                    t = t + 1
            properties_l['wpeil'] = max(wpeilen_list)

                
            print ('Gemiddeld peil: ' + str(properties_l['wpeil']))  
            
            for p in e:
                properties_p = {}
                print ('Child gevonden; ' + str(p.tag) + ' ' +  str(p.text))
                j=j+1
                

                
                point_list = p.text.split(',')
                print point_list
                properties_p['volgnr'] = j
                properties_p['datum'] = properties_l['datum']                
                properties_p['prof_ids'] = prof_list[0]  
                properties_p['code'] = point_list[0]
                properties_p['tekencode'] = point_list[1]                
                properties_p['x_coord'] = get_float(point_list[2])  
                properties_p['y_coord'] = get_float(point_list[3])
                properties_p['zvalues'] = zvalues
                
                if zvalues == 'z1z2':
                    properties_p['_ok_nap'] = get_float(point_list[4])
                    properties_p['_bk_nap'] = get_float(point_list[5])                  
                elif zvalues == 'z2z1':                   
                    properties_p['_ok_nap'] = get_float(point_list[5])
                    properties_p['_bk_nap'] = get_float(point_list[4])
                elif zvalues == 'z1':               
                    properties_p['_ok_nap'] = get_float(point_list[4])
                    properties_p['_bk_nap'] = get_float(point_list[4])
                elif zvalues == 'z2':                 
                    properties_p['_ok_nap'] = get_float(point_list[5])
                    properties_p['_bk_nap'] = get_float(point_list[5])   
                
                properties_p['afstand'] = sqrt(pow(get_float(nulpunt_x) - 
                                                   get_float(properties_p['x_coord']), 2) 
                                               + pow(get_float(nulpunt_y) - 
                                                     get_float(properties_p['y_coord']),2))
           
                
                if properties_p['code'] == '22' and i == 0:
#                     print ('22L code gevonden met waterpeil:' + str(properties_p['_bk_nap']))
                    
                    properties_ttlr = {}
                    properties_ttlr['prof_ids'] = prof_list[0]  
                    properties_ttlr['code'] = '22L'  
                    properties_ttlr['prof_pk'] = pk
                    properties_ttlr['project_id'] = properties_reeks['project_id']
                    properties_ttlr['afstand'] = properties_p['afstand']
                    properties_ttlr['breedte'] = properties_l['breedte']                   
                    properties_ttlr['z'] = properties_p['_bk_nap'] 
                    properties_ttlr['x_coord'] = properties_p['x_coord']
                    properties_ttlr['y_coord'] = properties_p['y_coord']
                    properties_l['xb_prof'] = properties_p['x_coord']
                    properties_l['yb_prof'] = properties_p['y_coord']
                    properties_ttlr['wpeil'] = properties_l['wpeil']
                    properties_ttlr['wpeil_bron'] = '22L en 22R'                                                           
                    i = i+1
                    
                    records_ttlr.append({'geometry': {'type': 'Point',
                                 'coordinates': (properties_p['x_coord'], properties_p['y_coord'])},
                        'properties': properties_ttlr})                      

                    # afstanden van punten voor 22L negatief maken.
                    # als volgnr < volgnr van 22L dan afstand = -afstand
                    
                    if j > 1:
                        for punt in records_p:
                            if punt['properties'].get('prof_ids') == prof_list[0]:
                                dist = punt['properties'].get('afstand')
                                punt['properties'].update(afstand = -dist)
                    
                elif properties_p['code'] == '22' and i == 1:
#                     print ('22R code gevonden met waterpeil:' + str(properties_p['_bk_nap']))
                    
                    properties_ttlr = {}
                    properties_ttlr['prof_ids'] = prof_list[0]                     
                    properties_ttlr['code'] = '22R'
                    properties_ttlr['prof_pk'] = pk     
                    properties_ttlr['project_id'] = properties_l['project_id']
                    properties_ttlr['afstand'] = properties_p['afstand'] 
                    properties_ttlr['breedte'] = properties_l['breedte']                                         
                    properties_ttlr['z'] = properties_p['_bk_nap'] 
                    properties_ttlr['x_coord'] = properties_p['x_coord']
                    properties_ttlr['y_coord'] = properties_p['y_coord']                                                                             
                    properties_l['xe_prof'] = properties_p['x_coord']
                    properties_l['ye_prof'] = properties_p['y_coord']
                    properties_ttlr['wpeil'] = properties_l['wpeil']
                    properties_ttlr['wpeil_bron'] = '22L en 22R'            
                    i = i+1
                    
                    records_ttlr.append({'geometry': {'type': 'Point',
                                 'coordinates': (properties_p['x_coord'], properties_p['y_coord'])},
                        'properties': properties_ttlr})                           
            

                elif properties_p['code'] == '22' and i > 1: 
                    i = i+1
                    print ('Meer dan 2 punten met 22 code gevonden')  

                
                #TODO: deze moet buiten de iteratie over de punten geplaatst worden zodat wpeil
                #      al bekend is voordat punten worden benoemd. Idem voor bepaling afstand
                #      ten opzichte van 22L
  

                properties_p['_bk_wp'] = (get_float(get_float(properties_l['wpeil']) - get_float(properties_p['_bk_nap'])))*100
                properties_p['_ok_wp'] = (get_float(get_float(properties_l['wpeil']) - get_float(properties_p['_ok_nap'])))*100                                
                    
                records_p.append({'geometry': {'type': 'Point',
                                 'coordinates': (properties_p['x_coord'], properties_p['y_coord'])},
                        'properties': properties_p})
                

            

            print ('Aantal gevonden 22 punten: ' + str(i))
            errors_p = {}
            if i < 2:
                errors_p['Profiel'] = properties_p['prof_ids']
                errors_p['Error'] = 'Minder dan 2 punten met 22 code gevonden.. geen lijn gegenereerd'
                records_errors.append(errors_p)                
            if i > 2:
                errors_p['Profiel'] = properties_p['prof_ids']
                errors_p['Error'] = 'Meer dan 2 punten met 22 code gevonden... lijn gebaseerd op eerste 2 gevonden 22-punten'    
                records_errors.append(errors_p)
            
            if i >= 2:  
                records_l.append({'geometry': {'type': 'LineString',
                             'coordinates': ((properties_l['xb_prof'], properties_l['yb_prof']),(properties_l['xe_prof'], properties_l['ye_prof']))},
                    'properties': properties_l})
                

    
    point_col.writerecords(records_p)
    ttlr_col.writerecords(records_ttlr)
    line_col.writerecords(records_l)

    

    return point_col, line_col, ttlr_col, records_errors