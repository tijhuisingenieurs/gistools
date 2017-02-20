import unittest
from gistools.utils.collection import MemCollection
import os.path

import fiona

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestMemCollection(unittest.TestCase):

    def setUp(self):
        self.collection = MemCollection()

        self.rec_one = {'geometry': {'type': 'Point', 'coordinates': (4, 4)},
                          'properties': {'name': 'test 1'}}
        self.rec_two = {'geometry': {'type': 'Point', 'coordinates': (2, 2)},
                          'properties': {'name': 'test 2'}}

        self.collection.write(self.rec_one)
        self.collection.write(self.rec_two)

    def test_len(self):
        self.assertEqual(len(self.collection), 2)

    def test_first_element(self):

        feature = self.collection[0]
        self.assertEqual(feature['geometry']['coordinates'], (4, 4))
        self.assertEqual(feature['id'], 0)
        self.assertDictContainsSubset({'name': 'test 1'},
                                      feature['properties'])

    def test_iterate_collection(self):
        self.assertListEqual([c['properties']['name'] for c in self.collection], ['test 1', 'test 2'])

    def test_keys_no_args(self):
        self.assertSetEqual(self.collection.keys(), set([0, 1]))

    def test_keys_start_stop(self):
        # self.assertSetEqual(self.collection.keys(start=1), set([1]))
        # self.assertSetEqual(self.collection.keys(start=0), set([0, 1]))
        self.assertSetEqual(self.collection.keys(start=-1), set([1]))
        self.assertSetEqual(self.collection.keys(stop=0), set([]))
        self.assertSetEqual(self.collection.keys(stop=1), set([0]))
        self.assertSetEqual(self.collection.keys(stop=2), set([0, 1]))
        self.assertSetEqual(self.collection.keys(stop=-1), set([0]))

    def test_keys_bounds(self):
        self.assertSetEqual(self.collection.keys(bbox=[3, 3, 5, 5]), set([0]))
        self.assertSetEqual(self.collection.keys(bbox=[1, 1, 3, 3]), set([1]))
        self.assertSetEqual(self.collection.keys(bbox=[1, 1, 5, 5]), set([0, 1]))
        self.assertSetEqual(self.collection.keys(bbox=[2, 2, 4, 4]), set([0, 1]))
        self.assertSetEqual(self.collection.keys(bbox=[2.01, 2, 4, 3.99]), set([]))

    def test_keys_mask(self):
        # todo: mask is not yet supported
        pass

    def test_keys_combined(self):
        self.assertSetEqual(self.collection.keys(stop=1, bbox=[3, 3, 5, 5]), set([0]))
        self.assertSetEqual(self.collection.keys(start=1, bbox=[3, 3, 5, 5]), set([]))
        self.assertSetEqual(self.collection.keys(start=-1, bbox=[2, 2, 4, 4]), set([1]))
        self.assertSetEqual(self.collection.keys(start=0, bbox=[2.01, 2, 4, 3.99]), set([]))

    def test_filter(self):
        self.assertDictEqual(next(self.collection.filter(stop=1, bbox=[3, 3, 5, 5])), self.rec_one)
        self.assertDictEqual(next(self.collection.filter(start=-1, bbox=[2, 2, 4, 4])), self.rec_two)

    def test_items(self):
        self.assertTupleEqual(next(self.collection.items(stop=1, bbox=[3, 3, 5, 5])), (0, self.rec_one))
        self.assertTupleEqual(next(self.collection.items(start=-1, bbox=[2, 2, 4, 4])), (1, self.rec_two))

    def test_bounds(self):
        self.assertListEqual(self.collection.bounds, [2.0, 2.0, 4.0, 4.0])

    def test_get_item(self):
        self.assertDictEqual(self.collection[0], self.rec_one)
        self.assertDictEqual(self.collection[1], self.rec_two)

    def test_empty_collection(self):
        collection = MemCollection()

        self.assertEqual(len(collection), 0)
        self.assertListEqual(list(collection.keys()), [])
        self.assertListEqual(list(collection.keys(bbox=(0, 0, 5, 5))), [])
        self.assertListEqual(list(collection.keys(0, 10)), [])
        self.assertListEqual(list(collection.items()), [])

    # def test_save_collection(self):
    #     self.collection.save('c:/tmp/test.shp', schema={
    #         'geometry': 'Point',
    #         'properties': {
    #             'name': 'str'
    #         }
    #     })
    #
    #     f = fiona.open('c:/tmp/test.shp')
    #
    #     self.assertEqual(len(f), 2)
