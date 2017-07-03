import unittest
import os.path

from gistools.utils.collection import MemCollection
from gistools.tools.create_veldwerk_output_shapes import create_fieldwork_output_shapes

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestCreateFieldworkOutputShapes(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_fieldwork_output_shapes(self):
        """test fill MemCollection with json data from file"""

        input_line_col = MemCollection(geometry_type='MultiLineString')
        input_point_col = MemCollection(geometry_type='MultiPoint')        

        input_point_col.writerecords([
        {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '1',
                'afstand': '-1.5',
                'bk_wp': '-80',
                'ok_wp': '-80'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '1',
                'afstand': '-0.5',
                'bk_wp': '-20',
                'ok_wp': '-20'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(1.5, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '22L',
                'afstand': '0',
                'bk_wp': '0',
                'ok_wp': '0'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(2.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '99',
                'afstand': '-0.5',
                'bk_wp': '10',
                'ok_wp': '30'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(3.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '99',
                'afstand': '1.5',
                'bk_wp': '20',
                'ok_wp': '35'}},                                                                          
        {'geometry': {'type': 'Point',
                          'coordinates': [(4.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '99',
                'afstand': '2.5',
                'bk_wp': '15',
                'ok_wp': '25'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(4.5, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '22R',
                'afstand': '3.0',
                'bk_wp': '0',
                'ok_wp': '0'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(5.5, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '2',
                'afstand': '-1.5',
                'bk_wp': '-30',
                'ok_wp': '-30'}},
        {'geometry': {'type': 'Point',
                          'coordinates': [(6.0, 0.0)]},
         'properties': {'prof_ids': 'test123',
                'code': '2',
                'afstand': '-1.5',
                'bk_wp': '-90',
                'ok_wp': '-90'}}   
        ])                             
        
        input_line_col.writerecords([
        {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (6.0, 0.0)]},
         'properties': {'pk': '1',
            'ids': 'test123',
            'project_id': 'p1',
            'opm': 'Handmatig ingevoerd door begroeiing. 1 en 2 is beschoeiing ',
            'wpeil': '-5.36',
            'datum': '20/06/2017',
            'breedte': '8.0'}}
        ])
        
        
        line_col, point_col = create_fieldwork_output_shapes(input_line_col, input_point_col)
        
        pass