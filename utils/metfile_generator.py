import json
import csv
import dateutil.parser as parser
import os.path

from collection import MemCollection, OrderedDict
from gistools.utils.conversion_tools import get_string

import logging
log = logging.getLogger(__name__)


def export_points_to_metfile(point_col, project, metfile_name, codering, type_metfile, type_peiling = None):
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
        
        current_profile = ''
        profiel_eind = '</PROFIEL>'

        unsorted_points = [p for p in point_col]
        sorted_points = sorted(unsorted_points, key = lambda x: (x['properties']['prof_ids'],
                                                                 x['properties']['afstand']))

        prefix = None
        if type_peiling != None:
            if type_peiling == "Inpeiling":
                prefix = "in_"
            elif type_peiling == "Uitpeiling":
                prefix = "uit_"
        else:
            pass

        # Temporarily for users to get used to new method
        if "," not in project:
            project = project + "," + project

        if type_metfile == "WIT":
            # write version
            version = ('<VERSIE>' + "1.0" + '</VERSIE>')
            writer.writerow({'regel': version})

            # write project data in REEKS
            project_tekst = ('<REEKS>' + project + ',</REEKS>')
            writer.writerow({'regel': project_tekst})

            for i, row in enumerate(sorted_points):
                profiel = str(sorted_points[i]['properties']['prof_ids'])

                if prefix != None:
                    profiel = prefix + profiel

                datum = (str(sorted_points[i]['properties']['datum']))[:10]
                code = (str(sorted_points[i]['properties']['code']))
                tekencode = 999
                if code in ['22L', '22l', '22R', '22r']:
                    code = 22
                if codering == 1:
                    tekencode = (str(sorted_points[i]['properties']['tekencode']))
                if codering == 2:
                    if len(str(code)) > 3:
                        a = str(code).split('_')
                        code = a[0]
                        tekencode = a[1]


                x_coord = str(sorted_points[i]['properties']['x_coord'])
                y_coord = str(sorted_points[i]['properties']['y_coord'])
                upper_level = str(sorted_points[i]['properties']['_bk_nap'])
                lower_level = str(sorted_points[i]['properties']['_ok_nap'])

                # check nieuw profiel
                if current_profile != profiel:

                    # check niet eerste profiel -> dan vorige profiel nog afsluiten
                    if current_profile != '':
                        writer.writerow({'regel': profiel_eind})

                    # wegschrijven profielregel
                    profiel_tekst = ('<PROFIEL>' + profiel + ',' + profiel + ',' +
                                     datum + ',' + '0.00,NAP,ABS,2,XY,' + x_coord + ',' +
                                     y_coord + ',')

                    writer.writerow({'regel': profiel_tekst})
                    current_profile = profiel

                # wegschrijven meting regels
                meting_tekst = ('<METING>' + str(code) + ',' + str(tekencode) + ',' +
                                x_coord + ',' + y_coord + ',' +
                                upper_level + ',' + lower_level + ',</METING>')
                writer.writerow({'regel': meting_tekst})

            writer.writerow({'regel': profiel_eind})

        elif type_metfile == "Wetterskip Fryslan":
            # write version
            version = ('<VERSIE>' + "1.0" + '</VERSIE>')
            writer.writerow({'regel': version})
            csvfile.write("\n")

            # write project data in REEKS
            project_tekst = ('<REEKS>' + "\n" + project + "\n" + '</REEKS>' + "\n\n")
            csvfile.write(project_tekst)

            for i, row in enumerate(sorted_points):
                profiel = str(sorted_points[i]['properties']['prof_ids'])

                if prefix != None:
                    profiel = prefix + profiel

                datum = (str(sorted_points[i]['properties']['datum']))[:10]
                date = parser.parse(datum)
                new_date = date.strftime("%Y%m%d")
                code = (str(sorted_points[i]['properties']['code']))
                tekencode = 999
                if code in ['22L', '22l', '22R', '22r']:
                    code = 22
                if codering == 1:
                    tekencode = (str(sorted_points[i]['properties']['tekencode']))
                if codering == 2:
                    if len(str(code)) > 3:
                        a = str(code).split('_')
                        code = a[0]
                        tekencode = a[1]


                x_coord = str(sorted_points[i]['properties']['x_coord'])
                y_coord = str(sorted_points[i]['properties']['y_coord'])
                upper_level = str(sorted_points[i]['properties']['_bk_nap'])
                lower_level = str(sorted_points[i]['properties']['_ok_nap'])

                # check nieuw profiel
                if current_profile != profiel:

                    # check niet eerste profiel -> dan vorige profiel nog afsluiten
                    if current_profile != '':
                        writer.writerow({'regel': profiel_eind})
                        csvfile.write("\n")

                    # wegschrijven profielregel
                    profiel_tekst = ('<PROFIEL>\n' + profiel + ',,\n' +
                                     new_date + ',\n' +
                                     '0.0,NAP,\n' +
                                     'ABS,2,\n' +
                                     'XY,' + x_coord + ',' + y_coord + ',\n')

                    # writer.writerow({'regel': profiel_tekst})
                    csvfile.write(profiel_tekst)
                    current_profile = profiel

                # wegschrijven meting regels
                meting_tekst = ('<METING>' + str(code) + ',' + str(tekencode) + ',' +
                                x_coord + ',' + y_coord + ',' +
                                upper_level + ',' + lower_level + ',</METING>')
                writer.writerow({'regel': meting_tekst})

            writer.writerow({'regel': profiel_eind})

        elif type_metfile == "Scheldestromen":
            # write version
            version = ('<VERSIE>' + "1.0" + '</VERSIE>')
            writer.writerow({'regel': version})

            # write project data in REEKS
            proj_nameList = project.split(",")
            project_tekst = ('<REEKS>' + "\n" + proj_nameList[0] + "\n" + proj_nameList[1] + "\n" + '</REEKS>' + "\n")
            csvfile.write(project_tekst)

            for i, row in enumerate(sorted_points):
                profiel = str(sorted_points[i]['properties']['prof_ids'])
                profiel = profiel.split("_")[-1]

                if prefix != None:
                    profiel = prefix + profiel

                datum = (str(sorted_points[i]['properties']['datum']))[:10]
                date = parser.parse(datum)
                new_date = date.strftime("%Y%m%d")
                code = sorted_points[i]['properties']['code']
                sub_code = get_string(sorted_points[i]['properties']['sub_code'])
                tekencode = sorted_points[i]['properties']['tekencode']

                if code in ['22L', '22l', '22R', '22r']:
                    code = 22
                if codering == 1:
                    tekencode = sorted_points[i]['properties']['tekencode']
                if codering == 2:
                    if len(str(code)) > 3:
                        a = str(code).split('_')
                        code = a[0]
                        tekencode = a[1]

                if sub_code:
                    code = sub_code

                x_coord = str(sorted_points[i]['properties']['x_coord'])
                y_coord = str(sorted_points[i]['properties']['y_coord'])
                upper_level = str(sorted_points[i]['properties']['_bk_nap'])
                lower_level = str(sorted_points[i]['properties']['_ok_nap'])

                # check nieuw profiel
                if current_profile != profiel:

                    # check niet eerste profiel -> dan vorige profiel nog afsluiten
                    if current_profile != '':
                        writer.writerow({'regel': profiel_eind})

                    # wegschrijven profielregel
                    # TODO: remove hardcoded, find different solution
                    profiel_tekst = ('<PROFIEL>\n' + "OPR" + profiel + ',\n' +
                                     "KIO_RTK-GPS (NTRIP)_Harde bodem" + ',\n' + #hardcoded
                                     new_date + ',\n' +
                                     '0.00,\nNAP,\n' +
                                     'ABS,\n2,\n' +
                                     'XY,' + "\n" + x_coord + ',\n' + y_coord + ',\n')

                    # writer.writerow({'regel': profiel_tekst})
                    csvfile.write(profiel_tekst)
                    current_profile = profiel

                # wegschrijven meting regels
                meting_tekst = ('<METING>' + str(code) + ',' + str(tekencode) + ',' +
                                x_coord + ',' + y_coord + ',' +
                                upper_level + ',' + lower_level + ',</METING>')
                writer.writerow({'regel': meting_tekst})

            writer.writerow({'regel': profiel_eind})

    
    return
