import unittest
from gistools.utils.collection import MemCollection
import os.path

import fiona

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestMemCollection(unittest.TestCase):

    def setUp(self):
        self.collection = MemCollection()

        self.collection.write({'geometry': {'type': 'Point', 'coordinates': (4, 4)},
                          'properties': {'name': 'test 1'}})
        self.collection.write({'geometry': {'type': 'Point', 'coordinates': (2, 4)},
                          'properties': {'name': 'test 2'}})

    def test_len(self):
        self.assertEqual(len(self.collection), 2)

    def test_empty_filter(self):

        feature = next(self.collection.filter())
        self.assertEqual(feature['geometry']['coordinates'], (4, 4))
        self.assertEqual(feature['id'], 0)
        self.assertDictContainsSubset({'name': 'test 1'},
                                      feature['properties'])

    def test_save_collection(self):
        self.collection.save('c:/tmp/test.shp', schema={
            'geometry': 'Point',
            'properties': {
                'name': 'str'
            }
        })

        f = fiona.open('c:/tmp/test.shp')

        self.assertEqual(len(f), 2)
