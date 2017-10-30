import unittest
import os.path

from gistools.tools.combine_manual_and_gps_points import CombineMeasurements, get_distance, get_projected_point

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'combineer_tool')


class TestCombineerTool(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_natte_profiel_data(self):
        cm = CombineMeasurements()

        prof_data = cm.read_natte_profiel_punten(
            os.path.join(test_data_dir, 'Natte_Profielen.xlsx')
        )

        self.assertEqual(len(prof_data), 12)
        self.assertEqual(prof_data[0]['id'], 487)
        self.assertEqual(prof_data[-1]['id'], 498)

        self.assertAlmostEquals(prof_data[0]['ref_level'], -1.80)
        self.assertAlmostEqual(prof_data[-1]['ref_level'], -1.80)

        self.assertEqual(len(prof_data[0]['wet_points']), 22)
        self.assertEqual(len(prof_data[0 - 1]['wet_points']), 23)

        self.assertDictEqual(prof_data[0]['wet_points'][17], {
            'distance': 7.50,
            'bk': 98,
            'ok': 100
        })

    def test_gps_punten(self):
        cm = CombineMeasurements()

        prof_data = cm.read_gps_punten(
            os.path.join(test_data_dir, 'GPS_Punten.xlsx')
        )

        self.assertEqual(len(prof_data), 99)
        self.assertDictEqual(prof_data[0], {
            'id': 487,
            'zijde': 'L',
            'pnt_soort': 1,
            'x': 84168.4542,
            'y': 423012.1353,
            'z': -0.4363,
            'code': 'Maaiveld',
        })

    def test_get_distance(self):
        dist = get_distance({
            'x': 1,
            'y': 1
        }, {
            'x': 4,
            'y': 4
        })

        self.assertAlmostEquals(dist, 3.0 * 1.4142, 2)

    def test_get_projected_point(self):
        point = get_projected_point({
            'x': 2,
            'y': 1
        }, {
            'x': 6,
            'y': 5
        },
            2.8284
        )

        self.assertAlmostEquals(point['x'], 4.0, 3)
        self.assertAlmostEquals(point['y'], 3.0, 3)

    def test_combine_punten(self):
        cm = CombineMeasurements()

        prof_point_output, messages = cm.run(
            os.path.join(test_data_dir, 'Natte_Profielen.xlsx'),
            os.path.join(test_data_dir, 'GPS_Punten.xlsx')
        )

        self.assertEqual(len(prof_point_output), 713)
