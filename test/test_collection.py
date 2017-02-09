import unittest
from utils.collection import Collection
import os.path

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestShapefile(unittest.TestCase):

    def test_shapefile_iteration(self):
        test_shape = os.path.join(test_data_dir, 'rd_line.shp')
        collection = Collection(test_shape)

        feature = next(collection.features)
        self.assertEqual(feature['geometry']['type'], 'LineString')
        self.assertEqual(feature['id'], '0')
        self.assertDictContainsSubset({'id': 1,
                                       'name': 'test name 1',
                                       'value': None},
                                      feature['properties'])
