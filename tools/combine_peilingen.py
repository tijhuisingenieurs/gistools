import csv
import logging
import numpy as np
import datetime
import dateutil.parser as parser

from gistools.utils.xml_handler import import_xml_to_memcollection
from gistools.utils.collection import MemCollection
from gistools.utils.geometry import TLine

log = logging.getLogger(__name__)


def link_table_to_dict(link_table):
    with open(link_table, mode='r') as infile:
        dialect = csv.Sniffer().sniff(infile.read(1024), delimiters=';,')
        infile.seek(0)
        reader = csv.reader(infile, dialect)
        link_dict = {rows[0]: rows[1] for rows in reader}
    return link_dict


def results_dict_to_csv(results_list, results_file):
    with open(results_file, 'wb') as resultsfile:
        resultsfile.write("Inpeiling;Uitpeiling;Foutenrapport\n")
        for row in results_list:
            s = "{0};{1};{2}.\n".format(row[0], row[1], row[2])
            resultsfile.write(s)
    return


def combine_profiles(out_points, in_points, scale_factor, width_peiling, in_line, scale_bank_distance=False):

    dist_ttr_in = float([point for point in in_points if point['properties']['code'] in
                         ('22', '22R', '22r')][-1]['properties']['afstand'])
    dist_ttr_uit = float([point for point in out_points if point['properties']['code'] in
                          ('22', '22R', '22r')][-1]['properties']['afstand'])

    # todo: sort
    # todo: check and warning, don't throw exception

    # step1: distance
    count_22 = 0
    if width_peiling == "Inpeiling":
        for point in out_points:

            if point['properties']['code'] in ['22', '22R', '22r', '22L', '22l']:
                point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
                count_22 += 1
            elif count_22 == 0:
                if scale_bank_distance:
                    point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
            elif count_22 == 2:
                if scale_bank_distance:
                    point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
                else:
                    point['properties']['afstand'] = float(point['properties']['afstand']) - dist_ttr_uit + dist_ttr_in
            else:
                point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
    else:
        scale_factor = 1/scale_factor
        for point in in_points:
            if point['properties']['code'] in ['22', '22R', '22r', '22L', '22l']:
                point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
                count_22 += 1
                if count_22 > 0:
                    new_coords = in_line.get_projected_point_at_distance(point['properties']['afstand'])
                    point['geometry']['coordinates'] = new_coords
                    point['properties']['x_coord'] = new_coords[0]
                    point['properties']['y_coord'] = new_coords[1]
            else:
                if count_22 == 0:
                    if scale_bank_distance:
                        point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
                elif count_22 == 2:
                    if scale_bank_distance:
                        point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
                    else:
                        point['properties']['afstand'] = float(point['properties']['afstand']) - dist_ttr_uit + dist_ttr_in
                else:
                    point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
                new_coords = in_line.get_projected_point_at_distance(point['properties']['afstand'])
                point['geometry']['coordinates'] = new_coords
                point['properties']['x_coord'] = new_coords[0]
                point['properties']['y_coord'] = new_coords[1]

    # step 2: match inpeiling
    for key in ['_bk_nap', '_ok_nap']:
        array_dist = np.array([point['properties']['afstand']
                               for point in out_points if point['properties'].get(key) is not None])
        array_level = np.array([point['properties'][key]
                               for point in out_points if point['properties'].get(key) is not None])

        left = round(out_points[0]['properties']['afstand'], 8)
        right = round(out_points[-1]['properties']['afstand'], 8)

        for point in in_points:
            if left <= round(point['properties']['afstand'], 8) <= right:
                point['properties']['uit' + key] = round(np.interp(point['properties']['afstand'], array_dist,
                                                                  array_level), 2)

    return in_points


def combine_peilingen(inpeil_file, uitpeil_file, order_inpeiling, order_uitpeiling, loc_inpeiling, loc_uitpeiling,
                      link_table, width_peilingen="Inpeiling", scale_threshold=0.05, scale_bank_distance=False):

    in_point_col, in_line_col, in_tt_col, in_errors = import_xml_to_memcollection(inpeil_file, order_inpeiling,
                                                                                  loc_inpeiling)

    uit_point_col, uit_line_col, uit_tt_col, uit_errors = import_xml_to_memcollection(uitpeil_file, order_uitpeiling,
                                                                                      loc_uitpeiling)

    link_dict = link_table_to_dict(link_table)
    results_list = []
    out_points = []
    unscaled_points = []

    for i, in_line in enumerate(in_line_col):
        prof_id = in_line['properties']['ids']
        prof_width = in_line['properties']['breedte']

        if prof_id not in link_dict:
            log.info('profiel %s is niet gelinkt aan een uitpeiling.', prof_id)
            results_list.append([prof_id, "", "Profiel is niet gelinkt aan een uitpeiling"])
            continue

        uit_lines = list(uit_line_col.filter(property={'key': 'ids', 'values': [link_dict[prof_id]]}))

        if len(uit_lines) != 1:
            if len(uit_lines) == 0:
                log.warning('kan opgegeven uitpeiling met id %s van profiel %s niet vinden',
                            link_dict[prof_id], prof_id)
                results_list.append([prof_id, link_dict['prof_id'], "Kan opgegeven uitpeiling niet vinden"])
            else:
                log.warning('meerdere uitpeilingen met id %s aanwezig', link_dict[prof_id])
                results_list.append([prof_id, link_dict[prof_id], "Meerdere uitpeilingen aanwezig"])
            continue

        uit_line = uit_lines[0]

        uit_width = uit_line['properties']['breedte']
        perc_change = ((uit_width - prof_width) / prof_width)

        if abs(perc_change) > scale_threshold:
            log.warning('Inpeiling profiel %s en uitpeiling profiel %s verschillen meer dan %.2f%% in breedte',
                        prof_id,
                        link_dict[prof_id],
                        scale_threshold * 100
                        )
            message = "Inpeiling en uitpeiling verschillen {0}% in breedte".format(round(abs(perc_change*100), 2))
            results_list.append([prof_id, link_dict[prof_id], message])

            uit_points = list(uit_point_col.filter(property={'key': 'prof_ids', 'values': [link_dict[prof_id]]}))
            unscaled_points += uit_points
            continue

        in_points = list(in_point_col.filter(property={'key': 'prof_ids', 'values': [prof_id]}))
        uit_points = list(uit_point_col.filter(property={'key': 'prof_ids', 'values': [link_dict[prof_id]]}))

        combined_points = combine_profiles(
            uit_points,
            in_points,
            scale_factor=prof_width/uit_width,
            width_peiling=width_peilingen,
            in_line=TLine(in_line['geometry']['coordinates']),
            scale_bank_distance=scale_bank_distance
        )
        out_points += combined_points

    # Make new collection with only those profiles that should be scaled and combined
    output_collection = MemCollection(geometry_type='Point')
    output_collection.writerecords(out_points)

    # Make new collection with uitpeilingen that were not scaled
    if unscaled_points:
        unscaled_collection = MemCollection(geometry_type='Point')
        unscaled_collection.writerecords(unscaled_points)
    else:
        unscaled_collection = None

    return output_collection, results_list, unscaled_collection


def convert_to_metfile(point_col, project, metfile_name, results_list, order="z2z1", level_peiling="Inpeiling",
                       shore_peiling="Inpeiling"):

    with open(metfile_name, 'wb') as csvfile:

        fieldnames = ['regel']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|',
                                quoting=csv.QUOTE_NONE,
                                quotechar='', escapechar='\\')

        current_profile = ''
        profile_end = '</PROFIEL>'

        unsorted_points = [p for p in point_col]
        sorted_points = sorted(unsorted_points, key=lambda x: (x['properties']['prof_ids'],
                                                               x['properties']['afstand']))

        # Temporarily for users to get used to new method
        if "," not in project:
            project = project + "," + project

        # write version
        version = "<VERSIE>1.0</VERSIE>"
        writer.writerow({'regel': version})

        # write project data in REEKS
        proj_nameList = project.split(",")
        project_tekst = "<REEKS>{0},{1}</REEKS>".format(
            proj_nameList[0],
            proj_nameList[1]
        )
        writer.writerow({'regel': project_tekst})

        count_22 = 0

        for i, row in enumerate(sorted_points):
            profile = str(sorted_points[i]['properties']['prof_ids'])

            if current_profile != profile:
                count_22 = 0

            profile_1 = "{0}_{1}".format(
                proj_nameList[0],
                profile
            )

            profile_2 = "Profiel_{0}".format(profile)

            datum = (str(sorted_points[i]['properties']['datum']))

            try:
                date = datetime.datetime.strptime(datum, "%d/%m/%Y")
            except ValueError:
                try:
                    date = datetime.datetime.strptime(datum, "%Y%m%d")
                except ValueError:
                    date = parser.parse(datum)

            new_date = date.strftime("%Y%m%d")
            code = sorted_points[i]['properties']['code']
            tekencode = sorted_points[i]['properties']['tekencode']

            if code in ['22L', '22l', '22R', '22r', '22']:
                code = 22
                count_22 += 1

            if count_22 > 2:
                log.error('meerdere 22 punten aanwezig bij profiel %s', profile)
                results_list.append([profile, "", "Meerdere 22 punten aanwezig"])

            x_coord = str(sorted_points[i]['properties']['x_coord'])
            y_coord = str(sorted_points[i]['properties']['y_coord'])

            if code == 22:
                if level_peiling == "Inpeiling":
                    upper_level = sorted_points[i]['properties'].get('_bk_nap')
                    lower_level = sorted_points[i]['properties'].get('_ok_nap')
                else:
                    upper_level = sorted_points[i]['properties'].get('uit_bk_nap')
                    lower_level = sorted_points[i]['properties'].get('uit_ok_nap')
            elif count_22 != 1:
                if shore_peiling == "Inpeiling":
                    upper_level = sorted_points[i]['properties'].get('_bk_nap')
                    lower_level = sorted_points[i]['properties'].get('_ok_nap')
                else:
                    upper_level = sorted_points[i]['properties'].get('uit_bk_nap')
                    lower_level = sorted_points[i]['properties'].get('uit_ok_nap')
                    if upper_level is None or lower_level is None:
                        continue
            else:
                upper_level = sorted_points[i]['properties'].get('uit_bk_nap')
                lower_level = min(sorted_points[i]['properties'].get('uit_ok_nap'),
                                  sorted_points[i]['properties'].get('_ok_nap'))

                if upper_level < lower_level:
                    lower_level = upper_level

            # check nieuw profiel
            if current_profile != profile:

                # check niet eerste profiel -> dan vorige profiel nog afsluiten
                if current_profile != '':
                    writer.writerow({'regel': profile_end})
                    count_22 = 0

                # wegschrijven profielregel
                profiel_tekst = "<PROFIEL>{0},{1},{2},0.00,NAP,ABS,2,XY,{3},{4},".format(
                    profile_1,
                    profile_2,
                    new_date,
                    x_coord,
                    y_coord
                )

                # writer.writerow({'regel': profiel_tekst})
                writer.writerow({'regel': profiel_tekst})
                current_profile = profile

            # wegschrijven meting regels
            if order == "z2z1":
                meting_tekst = "<METING>{0},{1},{2},{3},{4},{5},</METING>".format(
                    code,
                    tekencode,
                    x_coord,
                    y_coord,
                    upper_level,
                    lower_level
                )
            else:
                meting_tekst = "<METING>{0},{1},{2},{3},{4},{5},</METING>".format(
                    code,
                    tekencode,
                    x_coord,
                    y_coord,
                    lower_level,
                    upper_level
                )

            writer.writerow({'regel': meting_tekst})

        writer.writerow({'regel': profile_end})

    return results_list
