import unittest
from gistools.utils.wit import *


class TestWit(unittest.TestCase):

    def setUp(self):
        pass

    def test_vul_leggerwaarden(self):
        """test create values of theoretical profiel"""
        pass

    def test_create_leggerpunten(self):
        """test create points of theoretical profiel"""
        
        line = TLine([(0, 0), (0, 10)])
        line_id = 1
        name = 'test lijn'
        ti_waterbr = 10
        ti_talulbr = 3
        ti_knkbodr = 8

        profiel_dict = create_leggerpunten(line, line_id, name, ti_waterbr, ti_talulbr, ti_knkbodr)

    def test_update_leggerpunten_diepten(self):
        """test update of profiel_dict with depths of theoretical profiel"""

        profiel_dict = {'id': 1, 'name': 'test lijn',
                        'L22': (-5.0, 5.0), 'L22_peil': 0.00,
                        'knik_l': (-2.0, 5.0), 'knik_l_dpt': 0.00,
                        'knik_r': (3.0, 5.0), 'knik_r_dpt': 0.00,
                        'R22': (5.0, 5.0), 'R22_peil': 0.00}

        ti_velden_dict = {'ti_waterp': -1.0,
                          'ti_diepte': 2.0,
                          'ti_waterbr': 9.0,
                          'ti_bodemh': -3.0,
                          'ti_bodembr': 5.0,
                          'ti_talulbr': 2.0,
                          'ti_talurbr': 2.0,
                          'ti_knkbodr': 7.0}

        profiel_dict = update_leggerpunten_diepten(profiel_dict, ti_velden_dict)

        self.assertDictEqual(profiel_dict,
                             {'id': 1, 'name': 'test lijn',
                              'L22': (-5.0, 5.0), 'L22_peil': -1.00,
                              'knik_l': (-2.0, 5.0), 'knik_l_dpt': -3.0,
                              'knik_r': (3.0, 5.0), 'knik_r_dpt': -3.0,
                              'R22': (5.0, 5.0), 'R22_peil': -1.0})
        # not in output:
        # 'ti_talulbr': 2.0,
        # 'ti_knkbodr': 7.0,
        # 'ti_waterbr': 9.0
