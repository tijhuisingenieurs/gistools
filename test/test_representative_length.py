import unittest

from gistools.utils.collection import MemCollection
from gistools.tools.representative_length import representative_length


class TestRepresentativeLength(unittest.TestCase):

    def setUp(self):
        self.lines = MemCollection()
        self.profiles = MemCollection()

        self.lines.writerecords([{
            'geometry': {'type': 'LineString', 'coordinates': [(0, 5), (20, 5)]},
            'properties': {'lid': 1, 'name': 'line a'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(4, 0), (14, 10)]},
            'properties': {'lid': 2, 'name': 'line b'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(19, 1), (14, 1), (12, 4), (13, 7), (6, 7)]},
            'properties': {'lid': 3, 'name': 'line c'}
        }])

        self.profiles.writerecords([{
            'geometry': {'type': 'LineString', 'coordinates': [(4, 8), (4, 2)]},
            'properties': {'ids': 1, 'name': 'profile 1'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(15, 8), (15, 2)]},
            'properties': {'ids': 2, 'name': 'profile 2'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(4, 4), (8, 0)]},
            'properties': {'ids': 3, 'name': 'profile 3'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(11, 10), (14, 7)]},
            'properties': {'ids': 4, 'name': 'profile 4'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(17, 3), (17, -1)]},
            'properties': {'ids': 5, 'name': 'profile 5'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(15, 2.85), (12.15, 1)]},
            'properties': {'ids': 6, 'name': 'profile 6'}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(7, 8), (7, 6)]},
            'properties': {'ids': 7, 'name': 'profile 7'}
        }])


    def test_repLength(self):

        rep_length_col, rep_lines_col = representative_length(self.lines, self.profiles, 'ids')
        profile_dict = {profile['properties']['ids']: profile for profile in rep_length_col}

        self.assertEqual(profile_dict[1]['properties']['voor_leng'], 4)
        self.assertEqual(profile_dict[1]['properties']['na_leng'], 6)
        self.assertEqual(profile_dict[2]['properties']['voor_leng'], 6)
        self.assertEqual(profile_dict[2]['properties']['na_leng'], 5)
        self.assertAlmostEqual(profile_dict[3]['properties']['voor_leng'], 3)
        self.assertAlmostEqual(profile_dict[3]['properties']['na_leng'], 5)
        self.assertAlmostEqual(profile_dict[4]['properties']['voor_leng'], 5)
        self.assertAlmostEqual(profile_dict[4]['properties']['na_leng'], 2)

        self.assertEqual(profile_dict[5]['properties']['voor_leng'], 2)
        self.assertAlmostEqual(profile_dict[5]['properties']['na_leng'], 2)
        self.assertAlmostEqual(profile_dict[6]['properties']['voor_leng'], 2)
        self.assertAlmostEqual(profile_dict[6]['properties']['na_leng'], 6)
        self.assertAlmostEqual(profile_dict[7]['properties']['voor_leng'], 6)
        self.assertEqual(profile_dict[7]['properties']['na_leng'], 1)

        self.assertEqual(profile_dict[1]['properties']['tot_leng'], 10)
        self.assertEqual(profile_dict[2]['properties']['tot_leng'], 11)
        self.assertAlmostEqual(profile_dict[3]['properties']['tot_leng'], 8)
        self.assertAlmostEqual(profile_dict[4]['properties']['tot_leng'], 7)
        self.assertAlmostEqual(profile_dict[5]['properties']['tot_leng'], 4)
        self.assertAlmostEqual(profile_dict[6]['properties']['tot_leng'], 8)
        self.assertAlmostEqual(profile_dict[7]['properties']['tot_leng'], 7)

        # TODO: Add tests for the split lines
