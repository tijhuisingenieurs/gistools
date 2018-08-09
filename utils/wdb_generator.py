import csv
import logging
import os
import os.path
import xlwt
from gistools.utils.conversion_tools import get_float

log = logging.getLogger(__name__)


def export_points_to_wdb(point_col, line_col, wdb_path, afstand, project, rep_length):
    """ export content of point collection with appropriate attributes to 
    xls tabels for WDB
    
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
    
    returns xls files in WDB dialect"""
    
    # opzetten gebied tabel
    style_str = xlwt.easyxf('font: name Calibri, height 220')

    wb_gebied = xlwt.Workbook()
    ws = wb_gebied.add_sheet('Gebied')

    ws.write(0, 0, 'id_opp_water', style_str)
    ws.write(0, 1, 'omschrijving', style_str)
    ws.write(1, 0, project, style_str)
    ws.write(1, 1, project, style_str)

    file_path = os.path.join(wdb_path, 'gebied.xls')
    wb_gebied.save(file_path)

    # opzetten locatie tabel
    wb_locatie = xlwt.Workbook()
    ws = wb_locatie.add_sheet('Locatie')

    fieldnames_location = ['id_opp_water', 'id_vak', 'polderpeil', 'projekt',
                           'datum_uitvoering', 'situateTekNr', 'grf_xmin',
                           'grf_xmax', 'grf_ymax', 'grf_ymin', 'grf_stapx',
                           'grf_stapy', 'grf_manual_bounds', 'grf_includeAnchor', 'grf_anchor']

    fields_location = [project, project, 0, project, point_col[0]['properties']['datum'], "",
                       "", "", "", "", "", "", "False", "False", ""]

    for i, fieldname in enumerate(fieldnames_location):
        ws.write(0, i, fieldname, style_str)
        ws.write(1, i, fields_location[i], style_str)

    file_path = os.path.join(wdb_path, 'locatie.xls')
    wb_locatie.save(file_path)

    # opzetten metingen tabel
    wb_metingen = xlwt.Workbook()
    ws = wb_metingen.add_sheet('Metingen')

    fieldnames_metingen = ['id_opp_water', 'id_vak', 'id_profiel', 'raai',
                           'bagger', 'vast', 'uitpeiling', 'PBPSOORT',
                           'X_GPS_bk', 'Y_GPS_bk', 'X_pr_gps_bk', 'Y_pr_gps_bk',
                           'X_GPS_ok', 'Y_GPS_ok', 'X_pr_gps_ok', 'Y_pr_gps_ok']

    for i, fieldname in enumerate(fieldnames_metingen):
        ws.write(0, i, fieldname, style_str)

    for j, row in enumerate(point_col):
        index = j + 1

        try:
            prof_id = int(point_col[j]['properties']['prof_ids'])
        except ValueError:
            prof_id = point_col[j]['properties']['prof_ids']

        try:
            pbpsoort = int((str(point_col[j]['properties']['code']))[:2])
        except ValueError:
            pbpsoort = (str(point_col[j]['properties']['code']))[:2]

        fields_profiles = [project, project, prof_id, point_col[j]['properties']['afstand'],
                           get_float(point_col[j]['properties'].get('_bk_wp', '0.00')),
                           get_float(point_col[j]['properties'].get('_ok_wp', '0.00')),
                           0, pbpsoort, "", "", "", "", "", "", "", ""]

        for m, fieldname in enumerate(fields_profiles):
            ws.write(index, m, fieldname, style_str)
        current_profile = prof_id

    file_path = os.path.join(wdb_path, 'metingen.xls')
    wb_metingen.save(file_path)

    # opzetten profielen tabel
    wb_profielen = xlwt.Workbook()
    ws = wb_profielen.add_sheet('Profielen')

    fieldnames_profielen = ['id_opp_water', 'id_vak', 'id_profiel', 'wl_breedte',
                            'afstand', 'bagger', 'water', 'baggerInLegger',
                            'grondInLegger', 'waterdiepte', 'bodemdiepte',
                            'natPercentage', 'waterBuitenLegger', 'baggerVerw',
                            'grondVerw', 'datum_opname', 'opnamepeil',
                            'datum_uitpeiling', 'uitpeilingpeil', 'beschrijving',
                            'check_y2', 'check_up', 'afstandVoor', 'afstandNa',
                            'Xb_profiel', 'Yb_profiel', 'Xe_profiel', 'Ye_profiel']

    for i, fieldname in enumerate(fieldnames_profielen):
        ws.write(0, i, fieldname, style_str)

    for j, row in enumerate(line_col):
        index = j + 1
        remarks = ""

        try:
            prof_id = int(line_col[j]['properties']['ids'])
        except ValueError:
            prof_id = line_col[j]['properties']['ids']

        prof_points = list(point_col.filter(property={'key': 'prof_ids', 'values': [str(prof_id)]}))
        for point in prof_points:
            remark = point['properties'].get('opm', "")
            if remark not in ["", " "]:
                remarks = "{0} Op afstand {1}: {2}.".format(
                    remarks,
                    point['properties']['afstand'],
                    remark
                )

        if rep_length:
            afstand_voor = line_col[j]['properties']['voor_leng']
            afstand_na = line_col[j]['properties']['na_leng']
            afstand_totaal = line_col[j]['properties']['tot_leng']
        else:
            afstand_voor = afstand / 2
            afstand_na = afstand / 2
            afstand_totaal = ""

        remark = line_col[j]['properties']['opm']
        if remark not in ["", " "]:
            opm = '{0}. {1}'.format(remark, remarks)
        else:
            opm = remarks

        fields_profiles = [project, project, prof_id, "", afstand_totaal, "", "", "", "", "", "", "", "",
                           "", "", line_col[j]['properties']['datum'], line_col[j]['properties']['wpeil'],
                           "", "", opm, "True", "", afstand_voor,
                           afstand_na, line_col[j]['properties']['xb_prof'], line_col[j]['properties']['yb_prof'],
                           line_col[j]['properties']['xe_prof'], line_col[j]['properties']['ye_prof']]

        for m, fieldname in enumerate(fields_profiles):
            ws.write(index, m, fieldname, style_str)

    file_path = os.path.join(wdb_path, 'profielen.xls')
    wb_profielen.save(file_path)

    return
