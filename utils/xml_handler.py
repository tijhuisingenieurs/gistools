import xml.etree.ElementTree as ET
import os.path

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
    
    point_col = MemCollection(geometry_type='MultiPoint')
    ttlr_col = MemCollection(geometry_type='MultiPoint')
    line_col = MemCollection(geometry_type='MultiLineString')

    records_p = []
    records_ttlr = []
    records_l = []        

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
        print ('Element gevonden; ' + str(e.tag) + ' ' +  str(e.text))
        
        if e.tag in ['reeks', 'REEKS', 'Reeks']:
            properties_reeks = {}
            reeks_list = e.text.split(',')
            properties_reeks['project_id'] = reeks_list[0]
            print ('Project informatie gevonden in reeks: ' + str(reeks_list[0]))
        
        if e.tag in ['profiel', 'PROFIEL', 'Profiel']:
            prof_list = e.text.split(',')
            properties_l['ids'] = prof_list[0]
            properties_l['datum'] = prof_list[2]
            properties_l['project_id'] = properties_reeks['project_id']
            
            properties_p = {}
            i = 0
            j = 0   
            pk = pk + 1
            properties_l['pk'] = pk
            
            # Hier eerste door punten loopen om 22L en 22R te vinden ivm:
            # wpeil
            # breedte
            # afstanden voor punten tov 22L
            # dieptes tov wp bij punten
            
            
            for p in e:
                
                print ('Child gevonden; ' + str(p.tag) + ' ' +  str(p.text))
                j=j+1
                
                point_list = p.text.split(',')
                properties_p['volgnr'] = j
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
                
           
                
                if properties_p['code'] == '22' and i == 0:
                    print ('22L code gevonden met waterpeil:' + str(properties_p['_bk_nap']))
                    
                    properties_ttlr = {}
                    properties_ttlr['prof_ids'] = prof_list[0]  
                    properties_ttlr['code'] = '22L'  
                    properties_ttlr['prof_pk'] = pk
                    properties_ttlr['project_id'] = properties_reeks['project_id']
                    properties_ttlr['z'] = properties_p['_bk_nap'] 
                    properties_ttlr['x_coord'] = properties_p['x_coord']
                    properties_ttlr['y_coord'] = properties_p['y_coord']
                    properties_l['xb_prof'] = properties_p['x_coord']
                    properties_l['yb_prof'] = properties_p['y_coord']
                    
                    wpeilen_list = []
                    wpeilen_list.append(properties_p['_bk_nap'])                                      
                    i = i+1

                    
                elif properties_p['code'] == '22' and i == 1:
                    print ('22R code gevonden met waterpeil:' + str(properties_p['_bk_nap']))
                    
                    properties_ttlr = {}
                    properties_ttlr['prof_ids'] = prof_list[0]                     
                    properties_ttlr['code'] = '22R'
                    properties_ttlr['prof_pk'] = pk     
                    properties_ttlr['project_id'] = properties_l['project_id']
                    properties_ttlr['z'] = properties_p['_bk_nap'] 
                    properties_ttlr['x_coord'] = properties_p['x_coord']
                    properties_ttlr['y_coord'] = properties_p['y_coord']                                                                             
                    properties_l['xe_prof'] = properties_p['x_coord']
                    properties_l['ye_prof'] = properties_p['y_coord']
                      
                    wpeilen_list.append(properties_p['_bk_nap'])                                  
                    i = i+1

                elif properties_p['code'] == '22' and i > 1: 
                    print ('Meer dan 2 punten met 22 code gevonden')  
                
                
                #TODO: deze moet buiten de iteratie over de punten geplaatst worden zodat wpeil
                #      al bekend is voordat punten worden benoemd. Idem voor bepaling afstand
                #      ten opzichte van 22L
                properties_l['wpeil'] = max(wpeilen_list)
                properties_ttlr['wpeil'] = max(wpeilen_list)
                properties_ttlr['wpeil_bron'] = '22L en 22R'                
                print ('Gemiddeld peil: ' + str(properties_l['wpeil']))    
                
                properties_p['_bk_wp'] = get_float(properties_l['wpeil'] - properties_p['_bk_nap'])
                properties_p['_ok_wp'] = get_float(properties_l['wpeil'] - properties_p['_ok_nap'])                                
                
                records_p.append({'geometry': {'type': 'Point',
                                 'coordinates': (properties_p['x_coord'], properties_p['y_coord'])},
                        'properties': properties_p})
                
                records_ttlr.append({'geometry': {'type': 'Point',
                                 'coordinates': (properties_p['x_coord'], properties_p['y_coord'])},
                        'properties': properties_ttlr})                           
            
            print ('Aantal gevonden 22 punten: ' + str(i))
              
            records_l.append({'geometry': {'type': 'LineString',
                             'coordinates': ((properties_l['xb_prof'], properties_l['xb_prof']),(properties_l['xe_prof'], properties_l['xe_prof']))},
                    'properties': properties_l})
    
    point_col.writerecords(records_p)
    ttlr_col.writerecords(records_ttlr)
    line_col.writerecords(records_l)

    return point_col, line_col, ttlr_col