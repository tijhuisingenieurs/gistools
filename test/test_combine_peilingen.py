import os
from shapely.geometry import Point, LineString
from gistools.utils.xml_handler import import_xml_to_memcollection
from gistools.tools.combine_peilingen import combine_peilingen

inpeilingen = os.path.join(os.path.dirname(__file__), 'data', 'Inpeiling.met')
uitpeilingen = os.path.join(os.path.dirname(__file__), 'data', 'Uitpeiling.met')

link_table = os.path.join(os.path.dirname(__file__), 'data', 'linkTable.csv')

vals = combine_peilingen(inpeilingen, uitpeilingen, link_table)

vals