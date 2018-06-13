import os.path
import unittest

from gistools.tools.combine_peilingen import combine_peilingen, combine_profiles

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'combineer_tool')


class TestCombineerTool(unittest.TestCase):
    def setUp(self):
        self.profile_a = [
            {'properties': {'code': '1', 'afstand': -1, '_bk_nap': -1, '_ok_nap': -1}},
            {'properties': {'code': '22L', 'afstand': 0, '_bk_nap': -2, '_ok_nap': -2}},
            {'properties': {'code': '99', 'afstand': 1, '_bk_nap': -3, '_ok_nap': -4}},
            {'properties': {'code': '99', 'afstand': 9, '_bk_nap': -3, '_ok_nap': -4}},
            {'properties': {'code': '22R', 'afstand': 10, '_bk_nap': -2, '_ok_nap': -2}},
            {'properties': {'code': '2', 'afstand': 11, '_bk_nap': -1, '_ok_nap': -1}},
        ]

    def test_width_adjustment(self):
        profile_b = [
            {'properties': {'code': '22L', 'afstand': 0, '_bk_nap': -2, '_ok_nap': -2}},
            {'properties': {'code': '99', 'afstand': 1, '_bk_nap': -3, '_ok_nap': -4}},
            {'properties': {'code': '99', 'afstand': 9, '_bk_nap': -3, '_ok_nap': -4}},
            {'properties': {'code': '22R', 'afstand': 11, '_bk_nap': -2, '_ok_nap': -2}},
        ]

        profile_matched = combine_profiles(profile_b, self.profile_a, scale_factor=10.0 / 11.0)

        self.assertEqual(0.0, profile_matched[1]['properties']['afstand'])
        self.assertEqual(1.0, profile_matched[2]['properties']['afstand'])
        self.assertEqual(9.0, profile_matched[3]['properties']['afstand'])
        self.assertEqual(10.0, profile_matched[4]['properties']['afstand'])

        self.assertIsNone(profile_matched[0]['properties'].get('uit_ok_nap'))
        self.assertIsNone(profile_matched[-1]['properties'].get('uit_ok_nap'))

    def test_width_bank_no_adjustment(self):
        profile_b = [
            {'properties': {'code': '1', 'afstand': -1, '_bk_nap': -1, '_ok_nap': -1}},
            {'properties': {'code': '22L', 'afstand': 0, '_bk_nap': -2, '_ok_nap': -2}},
            {'properties': {'code': '99', 'afstand': 1, '_bk_nap': -3, '_ok_nap': -4}},
            {'properties': {'code': '99', 'afstand': 9, '_bk_nap': -3, '_ok_nap': -4}},
            {'properties': {'code': '22R', 'afstand': 11, '_bk_nap': -2, '_ok_nap': -2}},
            {'properties': {'code': '2', 'afstand': 13, '_bk_nap': -1, '_ok_nap': -1}},
        ]

        profile_matched = combine_profiles(profile_b, self.profile_a, scale_factor=10.0 / 11.0)

        self.assertIsNotNone(profile_matched[0]['properties'].get('uit_ok_nap'))
        self.assertIsNotNone(profile_matched[-1]['properties'].get('uit_ok_nap'))

    def test_width_bank_adjustment(self):
        profile_b = [
            {'properties': {'code': '1', 'afstand': -1, '_bk_nap': -1, '_ok_nap': -1}},
            {'properties': {'code': '22L', 'afstand': 0, '_bk_nap': -2, '_ok_nap': -2}},
            {'properties': {'code': '99', 'afstand': 1, '_bk_nap': -3, '_ok_nap': -4}},
            {'properties': {'code': '99', 'afstand': 9, '_bk_nap': -3, '_ok_nap': -4}},
            {'properties': {'code': '22R', 'afstand': 11, '_bk_nap': -2, '_ok_nap': -2}},
            {'properties': {'code': '2', 'afstand': 13, '_bk_nap': -1, '_ok_nap': -1}},
        ]

        profile_matched = combine_profiles(profile_b, self.profile_a, scale_factor=10.0 / 11.0,
                                           scale_bank_distance=True)

        self.assertIsNone(profile_matched[0]['properties'].get('uit_ok_nap'))
        self.assertIsNotNone(profile_matched[-1]['properties'].get('uit_ok_nap'))

    def test_with_read_write(self):
        inpeilingen = os.path.join(os.path.dirname(__file__), 'data', 'Inpeiling.met')
        uitpeilingen = os.path.join(os.path.dirname(__file__), 'data', 'Uitpeiling.met')
        link_table = os.path.join(os.path.dirname(__file__), 'data', 'linkTable.csv')

        vals = combine_peilingen(inpeilingen, uitpeilingen, "z2z1", "z2z1", "Eerste plaats", "Tweede plaats",
                                 link_table, scale_threshold=0.05, scale_bank_distance=False)

        vals
