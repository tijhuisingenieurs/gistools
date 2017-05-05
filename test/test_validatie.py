import unittest
import os.path

from gistools.utils.collection import MemCollection
from  gistools.tools.validatie import *

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestWit(unittest.TestCase):

    def setUp(self):
        pass

    
    
    def test_get_intersecting_segments(self):
        """test get line segments that intersect"""
         
        collection1 = MemCollection(geometry_type='MultiLinestring')
        collection2 = MemCollection(geometry_type='MultiLinestring')
  
        collection1.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (1.0, 1.0)),
                                              ((2.0, 2.0), (2.0, 3.0))]},
             'properties': {'id': 1L, 'name': 'testsegments line 1a'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(-25.0, 0.0), (0.0, 0.0), (-103.553, -250.0)]},
             'properties': {'id': 2L, 'name': 'testsegments line 2a'}}
        ])
          
        collection2.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.5, 0.0), (0.5, 100.0)]},
             'properties': {'id': 1L, 'name': 'testsegments line 1b'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 2.5), (500.0, 2.5)]},
             'properties': {'id': 2L, 'name': 'testsegments line 2b'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(-20.0, -1.0), (-20.0, 1.0)]},
             'properties': {'id': 3L, 'name': 'testsegments line 3b'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, -0.5), (-500.0, -0.5)]},
             'properties': {'id': 4L, 'name': 'testsegments line 4b'}}                                  
        ])
         
         
        line_parts_col1 = get_intersecting_segments(collection1, collection2)
        line_parts_col2 = get_intersecting_segments(collection2, collection1)
         
        pass

    def test_get_local_intersect_angles(self):
        """test calculate angles of intersection of lines at segment"""   
              
        collection1 = MemCollection(geometry_type='MultiLinestring')
        collection2 = MemCollection(geometry_type='MultiLinestring')
 
        collection1.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (1.0, 1.0)),
                                              ((2.0, 2.0), (2.0, 3.0))]},
             'properties': {'id': 1L, 'name': 'testlocal line 1a'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(-25.0, 0.0), (0.0, 0.0), (-103.553, -250.0)]},
             'properties': {'id': 2L, 'name': 'testlocal line 2a'}}
        ])
         
        collection2.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.5, 0.0), (0.5, 100.0)]},
             'properties': {'id': 1L, 'name': 'testlocal line 1b'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 2.5), (500.0, 2.5)]},
             'properties': {'id': 2L, 'name': 'testlocal line 2b'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(-20.0, -1.0), (-20.0, 1.0)]},
             'properties': {'id': 3L, 'name': 'testlocal line 3b'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, -0.5), (-500.0, -0.5)]},
             'properties': {'id': 4L, 'name': 'testlocal line 4b'}}                                  
        ])
         
        angle_col = get_local_intersect_angles(collection1, collection2)
         
        self.assertDictEqual(angle_col[0]['properties'],
                             {'crossangle': 45.0 })
        self.assertDictEqual(angle_col[1]['properties'],
                             {'crossangle': 90.0 })
        self.assertDictEqual(angle_col[2]['properties'],
                             {'crossangle': 90.0 })
        self.assertDictEqual(angle_col[3]['properties'],
                             {'crossangle': 67.5 })
    
    def test_get_global_intersect_angles(self):
        """test calculate angles of intersection of lines"""   
               
        collection1 = MemCollection(geometry_type='MultiLinestring')
        collection2 = MemCollection(geometry_type='MultiLinestring')
  
        collection1.writerecords([
            {'geometry': {'type': 'MultiLineString',
                          'coordinates': [((0.0, 0.0), (1.0, 1.0)),
                                              ((2.0, 2.0), (3.0, 3.0))]},
             'properties': {'id': 1L, 'name': 'testglobal line 1a'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (103.553, 250.0)]},
             'properties': {'id': 2L, 'name': 'testglobal line 2a'}}
        ])
          
        collection2.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.5, 0.0), (0.5, 100.0)]},
             'properties': {'id': 1L, 'name': 'testglobal line 1b'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.5), (500.0, 0.5)]},
             'properties': {'id': 2L, 'name': 'testglobal line 2b'}}
        ])
          
        angle_col = get_global_intersect_angles(collection1, collection2)
          
        self.assertDictEqual(angle_col[0]['properties'],
                             {'crossangle': 45.0 })
        self.assertDictEqual(angle_col[1]['properties'],
                             {'crossangle': 45.0 })
        self.assertDictEqual(angle_col[2]['properties'],
                             {'crossangle': 22.5 })
        self.assertDictEqual(angle_col[3]['properties'],
                             {'crossangle': 67.5 })
    