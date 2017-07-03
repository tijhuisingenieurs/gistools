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
            'wpeil': get_float(line_props['wpeil']),
            'datum': line_props['datum'],
            'breedte': get_float(line_props['breedte'])
        }

        line = TLine((line['geometry']['coordinates'][0], line['geometry']['coordinates'][-1]))
        line = line.get_line_with_length(l['breedte'], 0.5)

        for point in point_col:
            if point['properties']['prof_ids'] == l['ids']:
    
                point_props = point['properties']
                afstand = get_float(point_props['afstand'])
    
                xy = line.get_projected_point_at_distance(afstand) # todo: check if values before and after are supported
    
                p = {
                    'prof_ids': point_props['prof_ids'],
                    'datum': l['datum'],
                    'code': point_props['code'],
                    'afstand': get_float(point_props['afstand']),
                    'bk_wp': get_float(point_props['bk_wp']),
                    'bk_nap': get_float(l['wpeil']) - (get_float(point_props['bk_wp']) / 100),
                    'ok_wp': get_float(point_props['ok_wp']),
                    'ok_nap': get_float(l['wpeil']) - (get_float(point_props['ok_wp']) / 100),
                    'x': xy[0],
                    'y': xy[1],
                }
    
                output_point_col.writerecords([{
                    'geometry': {
                        'type': 'Point',
                        'coordinates': xy
                    },
                    'properties': p
                }])

        l['xb_prof'] = line.coords[0][0]
        l['yb_prof'] = line.coords[0][1]

        l['xe_prof'] = line.coords[-1][0]
        l['ye_prof'] = line.coords[-1][1]

        output_line_col.writerecords([{
            'geometry': {
                'type': 'LineString',
                'coordinates': line.coordinates
            },
            'properties': l
        }])

    return output_line_col, output_point_col






