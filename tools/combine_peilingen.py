import csv
import logging
import numpy as np

from shapely.geometry import MultiLineString, LineString
from gistools.utils.xml_handler import import_xml_to_memcollection
from gistools.utils.collection import MemCollection
from gistools.utils.metfile_generator import export_points_to_metfile

log = logging.getLogger(__name__)


def link_table_to_dict(link_table):
    with open(link_table, mode='r') as infile:
        dialect = csv.Sniffer().sniff(infile.read(1024), delimiters=';,')
        infile.seek(0)
        reader = csv.reader(infile, dialect)
        link_dict = {rows[0]: rows[1] for rows in reader}
    return link_dict


def make_lineString_object(line_collection):
    if type(line_collection['geometry']['coordinates'][0][0]) != tuple:
        line = LineString(line_collection['geometry']['coordinates'])
    else:
        line = MultiLineString(line_collection['geometry']['coordinates'])
    return line


def combine_profiles(out_points, in_points, scale_factor, scale_bank_distance=False, keep_only_in_points=True):

    dist_ttr_in = float([point for point in out_points if point['properties']['code'] in ('22', '22R')][-1]['properties']['afstand'])
    dist_ttr_uit = float([point for point in out_points if point['properties']['code'] in ('22', '22R')][-1]['properties']['afstand'])

    # todo:sort
    # todo: check and warning, don't throw exception

    # step1: distance
    for point in out_points:

        if point['properties']['code'] in ['99', '22', '22R']:
            point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
        elif point['properties']['code'] == '1':
            if scale_bank_distance:
                point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor

        elif point['properties']['code'] == '2':
            if scale_bank_distance:
                point['properties']['afstand'] = float(point['properties']['afstand']) * scale_factor
            else:
                point['properties']['afstand'] = float(point['properties']['afstand']) - dist_ttr_uit + dist_ttr_in

    # step 2: match inpeiling
    for key in ['_bk_nap', '_ok_nap']:
        array_dist = np.array([point['properties']['afstand']
                               for point in out_points if point['properties'].get(key) is not None])
        array_level = np.array([point['properties'][key]
                               for point in out_points if point['properties'].get(key) is not None])


        left = out_points[0]['properties']['afstand']
        right = out_points[-1]['properties']['afstand']

        for point in in_points:
            if left <= point['properties']['afstand'] <= right:
                point['properties']['uit'+ key] = round(np.interp(point['properties']['afstand'], array_dist,
                                                                  array_level), 2)

    return in_points


def combine_peilingen(inpeil_file, uitpeil_file, link_table, scale_threshold=0.05, scale_bank_distance=False):
    in_point_col, in_line_col, in_tt_col, in_errors = import_xml_to_memcollection(inpeil_file, 'z2z1', "Tweede plaats")

    uit_point_col, uit_line_col, uit_tt_col, uit_errors = import_xml_to_memcollection(uitpeil_file, 'z2z1',
                                                                                      "Tweede plaats")

    link_dict = link_table_to_dict(link_table)
    out_points = []

    for i, in_line in enumerate(in_line_col):
        prof_id = in_line['properties']['ids']
        prof_width = in_line['properties']['breedte']

        if prof_id not in link_dict:
            log.info('profiel %s is niet gelinkt aan een uitpeiling.', prof_id)
            continue

        uit_lines = list(uit_line_col.filter(property={'key': 'ids', 'values': [link_dict[prof_id]]}))

        if len(uit_lines) != 1:
            if len(uit_lines) == 0:
                log.warning('kan opgegeven uipeiling met id %s van profiel %s niet vinden', link_dict[prof_id], prof_id)
            else:
                log.warning('meerdere uipeilingen met id %s aanwezig', link_dict[prof_id])
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
            continue

        in_points = list(in_point_col.filter(property={'key': 'prof_ids', 'values': [prof_id]}))
        uit_points = list(uit_point_col.filter(property={'key': 'prof_ids', 'values': [link_dict[prof_id]]}))

        combined_points = combine_profiles(
            uit_points,
            in_points,
            scale_factor=prof_width/uit_width,
            scale_bank_distance=scale_bank_distance,
            keep_only_in_points=True
        )
        out_points += combined_points

    # Make new collection with only those profiles that should be scaled and combined
    output_collection = MemCollection(geometry_type='Point')
    output_collection.writerecords(out_points)

    return output_collection
