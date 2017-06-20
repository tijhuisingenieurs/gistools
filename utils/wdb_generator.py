import json
import csv
import os.path

from collection import MemCollection, OrderedDict

import logging
log = logging.getLogger(__name__)


def export_points_to_wdb(point_col, line_col, wdb_path, afstand):
    """ export content of point collection with appropriate attributes to 
    csv tabels for WDB
    
    receives collection of points with some project and profile info, and point 
    specific data:
    - profiel
    - datetime 
    - code
    - distance
    - x_coord -> x coordinate of point
    - y_coord -> y coordinate of point
    - lowerlevel -> height of soil in mNAP
    - upperlevel -> height of top of sediment in mNAP
    
    and collection of lines with profile location and project data of profiles:
    - profiel
    - opnamepeil
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
    
        # wegschrijven gebied tabel
        id_opp_water =  str(line_col[0]['properties']['project'])
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
            id_opp_water = str(line_col[i]['properties']['project'])
            id_vak = str(line_col[i]['properties']['profiel'])
            datum_uitvoering = (str(point_col[i]['properties']['datetime']))[:10]
            projekt =  str(point_col[i]['properties']['project']) 
                                            
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
            id_opp_water = str(line_col[i]['properties']['project'])    
            id_vak = str(line_col[i]['properties']['profiel'])
            id_profiel = str(line_col[i]['properties']['profiel'])
            opnamepeil = str(point_col[i]['properties']['opnamepeil']) 
            # in geval van oude Access versies moet check_y2 gelijk zijn aan -1
            # in geval van MDB viewer moet dit 'True' zijn
            # implementatie nu voor Access
            check_y2 = '-1'
            afstandVoor = str(afstand / 2)
            afstandNa = str(afstand / 2)
            Xb_profiel = str(line_col[i]['properties']['xb_profiel'])   
            Yb_profiel = str(line_col[i]['properties']['yb_profiel'])   
            Xe_profiel = str(line_col[i]['properties']['xe_profiel'])   
            Ye_profiel = str(line_col[i]['properties']['ye_profiel'])   
                                            
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
            id_opp_water = str(point_col[i]['properties']['project'])
            id_vak = str(point_col[i]['properties']['profiel'])
            id_profiel = str(point_col[i]['properties']['profiel'])
            raai = str(point_col[i]['properties']['distance'])
            
            # poging afvangen lege velden upper en lower level lukt nog niet !!!
            opnamepeil = float(point_col[i]['properties']['opnamepeil'])  
            bk = float(point_col[i]['properties'].get('upperlevel', '0.00'))
            ok = float(point_col[i]['properties'].get('lowerlevel', '0.00'))
            
            bagger = str((float(point_col[i]['properties']['opnamepeil']) - float(point_col[i]['properties'].get('upperlevel', '0.00'))) * 100)
            vast = str((float(point_col[i]['properties']['opnamepeil']) - float(point_col[i]['properties'].get('lowerlevel', '0.00'))) * 100)
            
            pbpsoort = (str(point_col[i]['properties']['code']))[:2]
            
            
            # wegschrijven meting regels
            writer4.writerow({'id_opp_water': id_opp_water, 'id_vak': id_vak, 
                             'id_profiel': id_profiel, 'raai': raai,
                             'bagger': bagger, 'vast': vast,
                             'uitpeiling': '0', 'PBPSOORT': pbpsoort})
    
    return
    