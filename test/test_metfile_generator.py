import unittest
import os.path
import tempfile
import shutil

from gistools.utils.collection import MemCollection
from gistools.utils.metfile_generator import export_points_to_metfile

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestMetfileGenerator(unittest.TestCase):
    def setUp(self):
        pass

    def test_export_points_to_metfile(self):
        """test export to metfile of point data"""

        point_col = MemCollection(geometry_type='MultiPoint')

        point_col.writerecords([
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'code': '1', 'x_coord': '0.00', 'y_coord': '0.00',
                            '_bk_nap': '1.00', '_ok_nap': '1.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'code': '22L', 'x_coord': '0.5', 'y_coord': '0.0',
                            '_bk_nap': '0.00', '_ok_nap': '0.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'code': '99', 'x_coord': '1.0', 'y_coord': '0.0',
                            '_bk_nap': '-0.40', '_ok_nap': '-0.60'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(2.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'code': '99', 'x_coord': '2.0', 'y_coord': '0.0',
                            '_bk_nap': '-1.00', '_ok_nap': '-1.25'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'code': '99', 'x_coord': '3.0', 'y_coord': '0.0',
                            '_bk_nap': '-0.40', '_ok_nap': '-0.75'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'code': '22R', 'x_coord': '3.5', 'y_coord': '0.0',
                            '_bk_nap': '0.00', '_ok_nap': '0.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(4.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '123', 'datum': '2017-06-14',
                            'code': '2', 'x_coord': '4.00', 'y_coord': '0.00',
                            '_bk_nap': '1.0', '_ok_nap': '1.0'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'code': '1', 'x_coord': '0.00', 'y_coord': '0.00',
                            '_bk_nap': '2.00', '_ok_nap': '2.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(0.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'code': '22L', 'x_coord': '0.5', 'y_coord': '0.0',
                            '_bk_nap': '1.00', '_ok_nap': '1.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(1.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'code': '99', 'x_coord': '1.0', 'y_coord': '0.0',
                            '_bk_nap': '-1.40', '_ok_nap': '-1.60'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(2.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'code': '99', 'x_coord': '2.0', 'y_coord': '0.0',
                            '_bk_nap': '-2.00', '_ok_nap': '-2.25'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'code': '99', 'x_coord': '3.0', 'y_coord': '0.0',
                            '_bk_nap': '-1.40', '_ok_nap': '-1.75'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(3.5, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'code': '22R', 'x_coord': '3.5', 'y_coord': '0.0',
                            '_bk_nap': '1.00', '_ok_nap': '1.00'}},
            {'geometry': {'type': 'Point',
                          'coordinates': [(4.0, 0.0)]},
             'properties': {'project_id': 1, 'project': 'p1',
                            'prof_ids': '456', 'datum': '2017-06-14',
                            'code': '2', 'x_coord': '4.00', 'y_coord': '0.00',
                            '_bk_nap': '2.0', '_ok_nap': '2.0'}}
        ])

        test_dir = os.path.join(tempfile.gettempdir(), 'metfile_test')
        if os.path.exists(test_dir):
            # empty test directory
            shutil.rmtree(test_dir)
        os.mkdir(test_dir)
        metfile_name = os.path.join(test_dir, 'metfile_test.csv')

        metfile = export_points_to_metfile(point_col, 'p1', metfile_name)

        pass
