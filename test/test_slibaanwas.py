import os.path
import unittest

import numpy as np

# from generatepointsfromlines import percentage
from gistools.tools.calculate_slibaanwas_tool import get_profiel_middelpunt, create_buffer, \
    get_slibaanwas
# from calculate_slibaanwas import from_shape_to_memcollection_points
from gistools.utils.collection import MemCollection

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def from_shape_to_memcollection_points(input_shape):
    """Deze functie zet de shape met informatie om naar een punten collectie
    input: shapefile met meetpunten erin (het kan elke puntenshape zijn. De kolominfo wordt overgezet
    naar de properties en de coordinaten naar coordinates)
    output: memcollection met deze punten erin"""

    # ---------- Omzetten van shapefile input naar memcollection----------------
    import arcpy
    # --- Initialize point collection
    point_col = MemCollection(geometry_type='MultiPoint')
    records_in = []
    rows_in = arcpy.SearchCursor(input_shape)
    fields_in = arcpy.ListFields(input_shape)
    # Fill the point collection
    for row in rows_in:
        geom = row.getValue('SHAPE')
        properties = {}
        for field in fields_in:
            if field.name.lower() != 'shape':
                if isinstance(field.name, unicode):
                    key = field.name.encode('utf-8')
                else:
                    key = field.name
                if isinstance(row.getValue(field.name), unicode):
                    value = row.getValue(field.name).encode('utf-8')
                else:
                    value = row.getValue(field.name)
                properties[key] = value
        # Voeg per punt de coordinaten en properties toe
        records_in.append({'geometry': {'type': 'Point',
                                        'coordinates': (geom.firstPoint.X, geom.firstPoint.Y)},
                           'properties': properties})
    # Schrijf de gegegevens naar de collection
    point_col.writerecords(records_in)
    return point_col


class TestSlibaanwas(unittest.TestCase):

    def setUp(self):
        self.point_list_in = [{
            'properties': {
                'afstand': 0,
                '_bk_nap': 0,
                'code': '22'
            }
        }, {
            'properties': {
                'afstand': 1,
                '_bk_nap': -1,
                'code': '99'
            }
        }, {
            'properties': {
                'afstand': 9,
                '_bk_nap': -1,
                'code': '99'
            }
        }, {
            'properties': {
                'afstand': 10,
                '_bk_nap': 0,
                'code': '22'
            }
        }]

        self.point_list_uit = [{
            'properties': {
                'afstand': 0,
                '_bk_nap': 0,
                'code': '22'
            }
        }, {
            'properties': {
                'afstand': 1,
                '_bk_nap': -2,
                'code': '99'
            }
        }, {
            'properties': {
                'afstand': 9,
                '_bk_nap': -2,
                'code': '99'
            }
        }, {
            'properties': {
                'afstand': 10,
                '_bk_nap': 0,
                'code': '22'
            }
        }]

    # def test_simpel(self):
    #     """ Test die voor een profiel met paar punten de calc_slibaanwas test"""
    #     slibaanwas_lengte, box_lengte, meter_factor, \
    #     breedte_verschil, errorwaarde = calc_slibaanwas_polygons(
    #         point_list_in=self.point_list_in,
    #         point_list_uit=self.point_list_uit,
    #         tolerantie_breedte=0.7,
    #         tolerantie_wp=0.15,
    #         meter_factor=-1
    #     )
    #
    #     self.assertEqual(1, slibaanwas_lengte)
    #     self.assertEqual(8, box_lengte)
    #     self.assertIsNone(errorwaarde)

    def test_vanuit_shape(self):
        """Laat een shape in en bereken de verschillende errormeldingen en slibaanwas"""
        input_inpeil = os.path.join(test_data_dir, 'calc_slibaanwas/Inpeiling.shp')
        input_uitpeil = os.path.join(test_data_dir, 'calc_slibaanwas/Uitpeiling.shp')
        zoekafstand = 1
        tolerantie_breedte = 0.7
        tolerantie_wp = 0.15
        # Maak een memcollection van de shapes
        point_col_in = from_shape_to_memcollection_points(input_inpeil)
        point_col_uit = from_shape_to_memcollection_points(input_uitpeil)
        # Bepaal het middelpunt
        point_col_mid_in, point_col_mid_uit, profiel_namen_in, profiel_namen_uit = \
            get_profiel_middelpunt(point_col_in, point_col_uit)
        # Maak een buffer
        buffer_mid_in = create_buffer(point_col_mid_in, zoekafstand)
        # Bepaal ahv buffer welke in en uitpeilingen bij elkaar horen en bereken de slibaanwas
        in_uit_combi, info_list = get_slibaanwas(point_col_in, point_col_uit, point_col_mid_uit, buffer_mid_in,
                                                 tolerantie_breedte, tolerantie_wp)

        # Test dat het middelste punt juist is
        self.assertEqual(np.round(point_col_mid_in[0]['properties']['afstand'], 2), 5.00)
        # Test  dat de juiste combinatie worden gevonden
        not_in_uit_combi_expected = [['in_2_uitmidden', 'uit_2_uitmidden'], ['in_5_ver', 'uit_5_ver']]
        in_uit_combi_expected = [['in_4_korter', 'uit_4_langer'], ['in_6_goed', 'uit_6_goed'],
                                 ['in_7_goed', 'uit_7_goed'],
                                 ['in_1_goed', 'uit_1_goed'], ['in_3_langer', 'uit_3_korter']]
        for combi in in_uit_combi:
            self.assertTrue(combi in in_uit_combi_expected)
        # Test dat de juiste errorwaardes worden gegegevn
        errorwaarde_expected = [None, 'waterpeilverschil', None, None, 'breedteverschil']
        self.assertEqual(info_list['errorwaarde'], errorwaarde_expected)
        # Test dat de juiste slibaanwas wordt berekend (voor de normale case 1)
        self.assertEqual(np.round(info_list['slibaanwas'][3], 2), 0.75)
