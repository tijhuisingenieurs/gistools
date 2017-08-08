import unittest
import os.path
import tempfile
import shutil

from gistools.utils.collection import MemCollection
from gistools.utils.wdb_generator import export_points_to_wdb

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestWit(unittest.TestCase):

    def setUp(self):
        pass
    
        
    def test_export_points_to_wdb(self):
        """test export to metfile of point data"""
        
        point_col = MemCollection(geometry_type='MultiPoint')
        line_col = MemCollection(geometry_type='MultiLinestring')
        
        afstand = 50
        
        line_col.writerecords([
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 0.0), (5.0, 0.0)]},
             'properties': {'id': 1L,'ids': '123', 
                            'datum': '2017-06-14',
                            'project_id': '1', 'project': 'p1',
                            'wpeil': '0.00',
                            'xb_prof': '0.0', 'yb_prof': '0.0', 
                            'xe_prof': '5.0', 'ye_prof': '0.0'}},
            {'geometry': {'type': 'LineString',
                          'coordinates': [(0.0, 1.0), (5.0, 1.0)]},
             'properties': {'id': 1L,'ids': '456', 
                            'project_id': '1', 'project': 'p1', 
                            'wpeil': '0.00',                            
                            'datum': '2017-06-14',
                            'xb_prof': '0.0', 'yb_prof': '1.0', 
                            'xe_prof': '5.0', 'ye_prof': '1.0'}}                          
        ])
        
        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'afstand': '0', 'wpeil' : '0.0',
                            'code': '1', 'x_coord': '0.00', 'y_coord': '0.00', 
                            '_bk_nap': '1.00', '_ok_nap': '1.00'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '123','datum': '2017-06-14',
                            'afstand': '0.5', 'wpeil' : '0.0',                             
                            'code': '22L', 'x_coord': '0.5', 'y_coord': '0.0', 
                            '_bk_nap': '0.00', '_ok_nap': '0.00'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'afstand': '1.0', 'wpeil' : '0.0',                             
                            'code': '99', 'x_coord': '1.0', 'y_coord': '0.0', 
                            '_bk_nap': '-0.40', '_ok_nap': '-0.60'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(2.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'afstand': '2.0', 'wpeil' : '0.0',                             
                            'code': '99', 'x_coord': '2.0', 'y_coord': '0.0', 
                            '_bk_nap': '-1.00', '_ok_nap': '-1.25'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'afstand': '3.0', 'wpeil' : '0.0',                             
                            'code': '99', 'x_coord': '3.0', 'y_coord': '0.0', 
                            '_bk_nap': '-0.40', '_ok_nap': '-0.75'  }},   
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'afstand': '3.5', 'wpeil' : '0.0',                             
                            'code': '22R', 'x_coord': '3.5', 'y_coord': '0.0', 
                            '_bk_nap': '0.00', '_ok_nap': '0.00'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(4.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'afstand': '4.0', 'wpeil' : '0.0',                             
                            'code': '2', 'x_coord': '0.70', 'y_coord': '0.70', 
                            '_bk_nap': '1.0', '_ok_nap': '1.0'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'afstand': '0', 'wpeil' : '0.0',                             
                            'code': '1', 'x_coord': '0.00', 'y_coord': '0.00', 
                            '_bk_nap': '2.00', '_ok_nap': '2.00'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'afstand': '0.5', 'wpeil' : '0.0',                             
                            'code': '22L', 'x_coord': '0.5', 'y_coord': '0.0', 
                            '_bk_nap': '0.00', '_ok_nap': '0.00'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '456','datum': '2017-06-14',
                            'afstand': '1.0', 'wpeil' : '0.0',                             
                            'code': '99', 'x_coord': '1.0', 'y_coord': '0.0', 
                            '_bk_nap': '-1.40', '_ok_nap': '-1.60'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(2.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'afstand': '2.0', 'wpeil' : '0.0',                             
                            'code': '99', 'x_coord': '2.0', 'y_coord': '0.0', 
                            '_bk_nap': '-2.00', '_ok_nap': '-2.25'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'afstand': '3.0', 'wpeil' : '0.0',                             
                            'code': '99', 'x_coord': '3.0', 'y_coord': '0.0', 
                            '_bk_nap': '-1.40', '_ok_nap': '-1.75'  }},   
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'afstand': '3.5', 'wpeil' : '0.0',                             
                            'code': '22R', 'x_coord': '3.5', 'y_coord': '0.0', 
                            '_bk_nap': '0.00', '_ok_nap': '0.00'  }},
            {'geometry': {'type': 'Point',
                          'coordinates': [(4.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1', 
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'afstand': '4.0', 'wpeil' : '0.0',                             
                            'code': '2', 'x_coord': '0.70', 'y_coord': '0.70', 
                            '_bk_nap': '2.0', '_ok_nap': '2.0'  }}                                
            ])
        
        test_dir = os.path.join(tempfile.gettempdir(), 'wdb_test')
        if os.path.exists(test_dir):
            # empty test directory
            shutil.rmtree(test_dir)
        os.mkdir(test_dir)
        
        metfile = export_points_to_wdb(point_col, line_col, test_dir, afstand, 'p1')
        
        pass