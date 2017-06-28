import logging


from gistools.utils.collection import MemCollection, OrderedDict
from gistools.utils.conversion_tools import get_float
from gistools.utils.iso8601 import parse_date
from gistools.utils.json_handler import json_to_dict
from gistools.utils.geometry import TLine


log = logging.getLogger(__name__)


def create_fieldwork_output_shapes(line_col, point_col):
    """
    
    line_col (MemCollection): profile line collection 
    point_col (MemCollection): profile point collection
    return: tuple with:
    - corrected profile line collection, with points as vertexes
    - corrected profile point collection based on calculated point locations
    """

    #
    output_line_col = MemCollection(geometry_type='LineString')
    output_point_col = MemCollection(geometry_type='Point')

    for line in line_col:

        line_props = line['properties']

        l = {
            'pk': line_props['pk'],
            'ids': line_props['ids'],
            'project_id': line_props['project_id'],
            'opm': line_props['opm'],
            'wpeil': line_props['wpeil'],
            'datum': line_props['datum'],
            'breedte': line_props['breedte']
        }

        # todo: geometry

        line['geometry']

        ttl = line['geometry']['coordinates'][0]
        ttr = line['geometry']['coordinates'][1]

        # afstand berekenen
        # cor_ttl en cor_ttr berekenen

        line = TLine((ttl_cor, ttr_cor))

        for point in point_col.filter({'prof_ids': line['ids']}):

            point_props = point['properties']

            xy = line.get_point_at_distance(point_props['afstand']) #todo: check if values before and after are supported


            p = {
                'prof_ids': point_props['prof_ids'],
                'datum': l['datum'],
                'code': point_props['code'],
                'afstand': point_props['afstand'],
                'bk_wp': point_props['bk_wp'],
                'bk_nap': l['wpeil'] - (point_props['bk_wp'] / 100),
                'ok_wp': point_props['ok_wp'],
                'ok_nap': l['wpeil'] - (point_props['ok_wp'] / 100),
                'x': xy.x,
                'y': xy.y,
            }

            output_point_col.writerecords([{
                'geometry': {
                    'type': 'Point',
                    'coordinates': xy.coords()
                },
                'properties': p
            }])

        l['xb_prof'] = line.coords[0][0]
        l['yb_prof'] = line.coords[0][1]

        l['xe_prof'] = line.coords[1][0]
        l['ye_prof'] = line.coords[1][1]

        output_line_col.writerecords([{
            'geometry': {
                'type': 'LineString',
                'coordinates': line.coords()
            },
            'properties': l
        }])


    return output_line_col, output_point_col






