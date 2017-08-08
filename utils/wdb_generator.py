import json
import csv
import os.path

from collection import MemCollection, OrderedDict
from gistools.utils.conversion_tools import get_float

import logging
log = logging.getLogger(__name__)


def export_points_to_wdb(point_col, line_col, wdb_path, afstand, project):
    """ export content of point collection with appropriate attributes to 
    csv tabels for WDB
    
    receives collection of points with some project and profile info, and point 
    specific data, at least:
    - profile name (prof_ids)
    - datetime (datum)
    - code
    - distance (afstand)
    - x_coord -> x coordinate of point
    - y_coord -> y coordinate of point
    - _bk_nap -> height of soil in mNAP
    - _ok_nap -> height of top of sediment in mNAP
    
    and collection of lines with profile location and project data of profiles,
    at least:
    - profile name (ids)
    - reference level (wpeil)
    - xb_profiel
    - yb_profiel
    - xe_profiel
    - ye_profiel
 
    
    and file location for wdb tables
    
    returns csv files in WDB dialect"""
    
   # opzetten gebied tabel
    gebied_csv = os.path.join(wdb_path, 'gebied.csv')
    with open(gebied_csv, 'wb') as csvfile1:
     
        fieldnames1 = ['id_opp_water', 'omschrijving']
        writer1 = csv.DictWriter(csvfile1, fieldnames=fieldnames1, delimiter=',',
                                quoting=csv.QUOTE_NONE,
                                quotechar='', escapechar='\\')
        writer1.writeheader()
    
        # wegschrijven gebied tabel (code kan compacter, maar expliciet uitgeschreven
        # zodat bij toekomstige doorontwikkeling makkelijk aanpassingen gedaan kunnen worden)
        id_opp_water = str(project)
        omschrijving = id_opp_water
        writer1.writerow({'id_opp_water': id_opp_water ,'omschrijving': omschrijving })

    
    # opzetten locatie tabel
    locatie_csv = os.path.join(wdb_path, 'locatie.csv')
    with open(locatie_csv, 'wb') as csvfile2:
    
        fieldnames2 = ['id_opp_water', 'id_vak', 'polderpeil', 'projekt', 
                  'datum_uitvoering', 'situateTekNr', 'grf_xmin', 
                  'grf_xmax', 'grf_ymax', 'grf_ymin', 'grf_stapx', 
                  'grf_stapy', 'grf_manual_bounds', 'grf_includeAnchor', 'grf_anchor']

        writer2 = csv.DictWriter(csvfile2, fieldnames=fieldnames2)  
        writer2.writeheader()     
        
        for i, row in enumerate(line_col):
            id_opp_water = str(project)
            id_vak = str(line_col[i]['properties']['ids'])
            datum_uitvoering = (str(point_col[i]['properties']['datum']))[:10]
            projekt =  str(project)
                                            
            # wegschrijven locatie regels
            writer2.writerow({'id_opp_water': id_opp_water, 'id_vak': id_vak, 
                             'projekt': projekt, 
                             'datum_uitvoering': datum_uitvoering,
                             'polderpeil': '0',
                             'grf_manual_bounds': 'ONWAAR',
                             'grf_includeAnchor': 'ONWAAR'
                              })



    # opzetten profielen tabel
    profielen_csv = os.path.join(wdb_path, 'profielen.csv')
    with open(profielen_csv, 'wb') as csvfile3:
        
        fieldnames3 = ['id_opp_water', 'id_vak', 'id_profiel', 'wl_breedte', 
                      'afstand', 'bagger', 'water', 'baggerInLegger', 
                      'grondInLegger', 'waterdiepte', 'bodemdiepte', 
                      'natPercentage', 'waterBuitenLegger', 'baggerVerw', 
                      'grondVerw', 'datum_opname', 'opnamepeil', 
                      'datum_uitpeiling', 'uitpeilingpeil', 'beschrijving', 
                      'check_y2', 'check_up', 'afstandVoor', 'afstandNa', 
                      'Xb_profiel', 'Yb_profiel', 'Xe_profiel', 'Ye_profiel']

        writer3 = csv.DictWriter(csvfile3, fieldnames=fieldnames3)      
        writer3.writeheader()
        
        for i, row in enumerate(line_col):
            id_opp_water = str(project)   
            id_vak = str(line_col[i]['properties']['ids'])
            id_profiel = str(line_col[i]['properties']['ids'])
            opnamepeil = str(line_col[i]['properties']['wpeil']) 
            # in geval van oude Access versies moet check_y2 gelijk zijn aan -1
            # in geval van MDB viewer moet dit 'True' zijn
            # implementatie nu voor Access
            check_y2 = '-1'
            afstandVoor = str(afstand / 2)
            afstandNa = str(afstand / 2)
            Xb_profiel = str(line_col[i]['properties']['xb_prof'])   
            Yb_profiel = str(line_col[i]['properties']['yb_prof'])   
            Xe_profiel = str(line_col[i]['properties']['xe_prof'])   
            Ye_profiel = str(line_col[i]['properties']['ye_prof'])   
                                            
            # wegschrijven profiel regels
            writer3.writerow({'id_opp_water': id_opp_water, 'id_vak': id_vak, 
                             'id_profiel': id_profiel, 'opnamepeil': opnamepeil,
                             'check_y2': check_y2, 'afstandVoor': afstandVoor,
                             'afstandNa': afstandNa,
                             'Xb_profiel': Xb_profiel, 'Yb_profiel': Yb_profiel, 
                             'Xe_profiel': Xe_profiel, 'Ye_profiel': Ye_profiel })

           
    # opzetten metingen tabel
    metingen_csv = os.path.join(wdb_path, 'metingen.csv')
    with open(metingen_csv, 'wb') as csvfile4:
        
        fieldnames4 = ['id_opp_water', 'id_vak', 'id_profiel', 'raai', 
                       'bagger', 'vast', 'uitpeiling', 'PBPSOORT', 
                       'X_GPS_bk', 'Y_GPS_bk', 'X_pr_gps_bk', 'Y_pr_gps_bk', 
                       'X_GPS_ok', 'Y_GPS_ok', 'X_pr_gps_ok', 'Y_pr_gps_ok']
        
        writer4 = csv.DictWriter(csvfile4, fieldnames=fieldnames4)      
        writer4.writeheader()
        
        for i, row in enumerate(point_col):
            id_opp_water = str(project)
            id_vak = str(point_col[i]['properties']['prof_ids'])
            id_profiel = str(point_col[i]['properties']['prof_ids'])
            raai = str(point_col[i]['properties']['afstand'])
            
            # poging afvangen lege velden upper en lower level lukt nog niet !!!
            bagger = str(get_float(point_col[i]['properties'].get('_bk_wp', '0.00')))
            vast = str(get_float(point_col[i]['properties'].get('_ok_wp', '0.00')))
            
            pbpsoort = (str(point_col[i]['properties']['code']))[:2]
            
            
            # wegschrijven meting regels
            writer4.writerow({'id_opp_water': id_opp_water, 'id_vak': id_vak, 
                             'id_profiel': id_profiel, 'raai': raai,
                             'bagger': bagger, 'vast': vast,
                             'uitpeiling': '0', 'PBPSOORT': pbpsoort})
    
    return
    