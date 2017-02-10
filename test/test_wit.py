import unittest
from shapely.geometry import Point
from utils.geometry import TLine, TMultiLineString
from utils.wit import  *
from math import sqrt

class TestWit(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_create_leggerpunten(self):
        """test create points of theoretical profiel"""
        
        line = TLine([(0, 0), (0, 10)])
        TI_waterbr = 10
        TI_talulbr = 3
        TI_bodembr = 5

        profiel_dict = create_leggerpunten(line,TI_waterbr, TI_talulbr, TI_bodembr)

        self.assertDictEqual(profiel_dict,{'22L': (-5.0, 5.0),'22L_peil': 0.00,
                    'knik_l': (-2.0, 5.0), 'knik_l_dpt': 0.00,
                    'knik_r': (3.0, 5.0), 'knik_r_dpt': 0.00,
                    '22R': (5.0, 5.0), '22R_peil': 0.00})
        
        
    def test_update_leggerpunten_diepten(self):
        """test update of profiel_dict with depths of theoretical profiel"""
        
        profiel_dict = {'22L': (-5.0, 5.0), '22L_peil': 0.00,
                    'knik_l': (-2.0, 5.0), 'knik_l_dpt': 0.00,
                    'knik_r': (3.0, 5.0), 'knik_r_dpt': 0.00,
                    '22R': (5.0, 5.0), '22R_peil': 0.00}
        leggerdiepten = (-1.0, -3.5, -3.5, -1.0)
        
        profiel_dict = update_leggerpunten_diepten(profiel_dict, leggerdiepten)

        self.assertDictEqual(profiel_dict,
                             {'22L': (-5.0, 5.0), '22L_peil': -1.00,
                              'knik_l': (-2.0, 5.0), 'knik_l_dpt': -3.50,
                              'knik_r': (3.0, 5.0), 'knik_r_dpt': -3.50,
                              '22R': (5.0, 5.0), '22R_peil': -1.0})
        
        