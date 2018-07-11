import csv
import datetime

import logging
log = logging.getLogger(__name__)


def extract_puntpeilingen(point_col, output_path, reeks):
    with open(output_path, 'wb') as csvfile:

        fieldnames = ['regel']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|',
                                quoting=csv.QUOTE_NONE,
                                quotechar='', escapechar='\\')

        current_profile = ''
        profile_end = '</PROFIEL>'

        unsorted_points = [p for p in point_col]
        sorted_points = sorted(unsorted_points, key=lambda x: (x['properties']['Meetpunt']))

        # write version
        version = "<VERSIE>1.0</VERSIE>"
        writer.writerow({'regel': version})

        # write project data in REEKS
        project_tekst = "<REEKS>{0},</REEKS>".format(reeks)
        writer.writerow({'regel': project_tekst})

        for i, row in enumerate(sorted_points):
            profiel = str(sorted_points[i]['properties']['Meetpunt'])

            datum = (str(sorted_points[i]['properties']['Datum']))
            date = datetime.datetime.strptime(datum, "%d/%m/%Y")
            new_date = date.strftime("%Y%m%d")
            tekencode = 999
            x_coord = str(sorted_points[i]['properties']['X'])
            y_coord = str(sorted_points[i]['properties']['Y'])
            upper_level = float(sorted_points[i]['properties']['BK'])
            lower_level = float(sorted_points[i]['properties']['OK'])
            water_level = float(sorted_points[i]['properties']['Opnamepeil'])

            upper_level_nap = str(water_level - (upper_level/100))
            lower_level_nap = str(water_level - (lower_level/100))

            # check nieuw profiel
            if current_profile != profiel:

                # check niet eerste profiel -> dan vorige profiel nog afsluiten
                if current_profile != '':
                    writer.writerow({'regel': profile_end})

                # wegschrijven profielregel
                profiel_tekst = "<PROFIEL>{0},{1},{2},0.00,NAP,ABS,2,XY,{3},{4},".format(
                    profiel,
                    profiel,
                    new_date,
                    x_coord,
                    y_coord
                )

                writer.writerow({'regel': profiel_tekst})
                current_profile = profiel

            # wegschrijven meting regels 22 punt
            meting_tekst = "<METING>{0},{1},{2},{3},{4},{5},</METING>".format(
                "22",
                tekencode,
                x_coord,
                y_coord,
                str(water_level),
                str(water_level)
            )
            writer.writerow({'regel': meting_tekst})

            # wegschrijven meting regels puntpeiling
            meting_tekst = "<METING>{0},{1},{2},{3},{4},{5},</METING>".format(
                "99",
                tekencode,
                x_coord,
                y_coord,
                upper_level_nap,
                lower_level_nap
            )
            writer.writerow({'regel': meting_tekst})

        writer.writerow({'regel': profile_end})
