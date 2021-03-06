import unittest
import os.path
import tempfile
import shutil

from gistools.utils.collection import MemCollection
from gistools.utils.csv_handler import export_memcollection_to_csv, import_csv_to_memcollection

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestCsvHandler(unittest.TestCase):
    def setUp(self):
        pass

    def test_export_memcollection_to_csv(self):
        """test export to metfile of point data"""

        point_col = MemCollection(geometry_type='MultiPoint')

        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '123', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '1', 'x_coord': '0.00', 'y_coord': '0.00',
                            'upperlevel': '1.00', 'lowerlevel': '1.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '123', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '22L', 'x_coord': '0.5', 'y_coord': '0.0',
                            'upperlevel': '0.00', 'lowerlevel': '0.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '123', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '99', 'x_coord': '1.0', 'y_coord': '0.0',
                            'upperlevel': '-0.40', 'lowerlevel': '-0.60'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(2.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '123', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '99', 'x_coord': '2.0', 'y_coord': '0.0',
                            'upperlevel': '-1.00', 'lowerlevel': '-1.25'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '123', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '99', 'x_coord': '3.0', 'y_coord': '0.0',
                            'upperlevel': '-0.40', 'lowerlevel': '-0.75'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '123', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '22R', 'x_coord': '3.5', 'y_coord': '0.0',
                            'upperlevel': '0.00', 'lowerlevel': '0.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(4.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '123', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '2', 'x_coord': '4.00', 'y_coord': '0.00',
                            'upperlevel': '1.0', 'lowerlevel': '1.0'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '456', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '1', 'x_coord': '0.00', 'y_coord': '0.00',
                            'upperlevel': '2.00', 'lowerlevel': '2.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '456', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '22L', 'x_coord': '0.5', 'y_coord': '0.0',
                            'upperlevel': '1.00', 'lowerlevel': '1.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '456', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '99', 'x_coord': '1.0', 'y_coord': '0.0',
                            'upperlevel': '-1.40', 'lowerlevel': '-1.60'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(2.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '456', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '99', 'x_coord': '2.0', 'y_coord': '0.0',
                            'upperlevel': '-2.00', 'lowerlevel': '-2.25'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '456', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '99', 'x_coord': '3.0', 'y_coord': '0.0',
                            'upperlevel': '-1.40', 'lowerlevel': '-1.75'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '456', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '22R', 'x_coord': '3.5', 'y_coord': '0.0',
                            'upperlevel': '1.00', 'lowerlevel': '1.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(4.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'profiel': '456', 'datetime': '2017-06-14T06:57:36.027Z',
                            'code': '2', 'x_coord': '4.00', 'y_coord': '0.00',
                            'upperlevel': '2.0', 'lowerlevel': '2.0'}}
        ])

        test_dir = os.path.join(tempfile.gettempdir(), 'csv_test')
        if os.path.exists(test_dir):
            # empty test directory
            shutil.rmtree(test_dir)
        os.mkdir(test_dir)
        csv_file_name = os.path.join(test_dir, 'csv_test.csv')

        csv_file = export_memcollection_to_csv(point_col, csv_file_name)

        pass
    
    def test_import_csv_to_memcollection(self):
        """test import csv with metingen to Memcollection"""
        
        csv_file = os.path.join(os.path.dirname(__file__), 'data', 'test_import_csv.csv')

        point_col = import_csv_to_memcollection(csv_file)
        
        self.assertEqual(len(point_col), 2)
        
        self.assertDictEqual(point_col[0]['properties'],
                             {'veld1': 'a',
                              'veld2': 'b',
                              'veld3': 'c'})
        self.assertDictEqual(point_col[1]['properties'],
                             {'veld1': '1',
                              'veld2': '2',
                              'veld3': '3'})        

        
        pass
