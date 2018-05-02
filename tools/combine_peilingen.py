import csv
import logging
import numpy as np

from shapely.geometry import MultiLineString, LineString
from gistools.utils.xml_handler import import_xml_to_memcollection

log = logging.getLogger(__name__)


def link_table_to_dict(link_table):
    with open(link_table, mode='r') as infile:
        reader = csv.reader(infile, delimiter=";")
        link_dict = {rows[0]: rows[1] for rows in reader}

    return link_dict


def make_lineString_object(line_collection):
    if type(line_collection['geometry']['coordinates'][0][0]) != tuple:
        line = LineString(line_collection['geometry']['coordinates'])
    else:
        line = MultiLineString(line_collection['geometry']['coordinates'])
    return line


def combine_peilingen(inpeil_file, uitpeil_file, link_table):

    in_point_col, in_line_col, in_tt_col, in_errors = import_xml_to_memcollection(inpeil_file, 'z2z1', "Tweede plaats")

    uit_point_col, uit_line_col, uit_tt_col, uit_errors = import_xml_to_memcollection(uitpeil_file, 'z2z1',
                                                                                      "Tweede plaats")

    link_dict = link_table_to_dict(link_table)
    threshold = 5

    for i, in_line in enumerate(in_line_col):
        prof_id = in_line['properties']['ids']
        prof_width = in_line['properties']['breedte']

        for u, uit_line in enumerate(uit_line_col):
            if uit_line['properties']['ids'] == link_dict[prof_id]:
                uit_width = uit_line['properties']['breedte']
                perc_change = (abs(uit_width - prof_width)/prof_width)*100.0

                if perc_change < threshold:
                    ## Scale line
                    ## First make LineString objects
                    in_linestring = make_lineString_object(in_line)
                    uit_linestring = make_lineString_object(uit_line)

                    scale_factor = in_linestring.length/uit_linestring.length

                    uit_x = []
                    uit_y = []

                    for p, point in enumerate(uit_point_col):
                        if point['properties']['prof_ids'] == link_dict[prof_id]:
                            # Scale point based on inpeilingen-line
                            scaled_distance = point['properties']['afstand'] * scale_factor
                            scaled_point = in_linestring.interpolate(scaled_distance)

                            point['properties']['afstand'] = scaled_distance
                            point['geometry']['coordinates'] = scaled_point.coords[0]
                            point['properties']['x_coord'] = point['geometry']['coordinates'][0]
                            point['properties']['y_coord'] = point['geometry']['coordinates'][1]

                            uit_x.append(point['properties']['afstand'])
                            uit_y.append(point['properties']['_bk_nap'])

                    array_x = np.array(uit_x)
                    array_y = np.array(uit_y)

                    for p, point in enumerate(in_point_col):
                        if point['properties']['prof_ids'] == prof_id:
                            in_dis = point['properties']['afstand']
                            point['properties']['uit_bk_nap'] = np.interp(in_dis, array_x, array_y)

                else:
                    warning_message = 'Inpeiling profiel {0} en uitpeiling profiel {1} verschillen meer dan {2}% in ' \
                                      'breedte'.format(
                        prof_id,
                        link_dict[prof_id],
                        threshold
                    )
                    log.warning(warning_message)

    return in_point_col
