import unittest

from gistools.utils.collection import MemCollection
from gistools.tools.number_points import number_points_on_line


class TestNumberPoints(unittest.TestCase):

    def test_renumber(self):
        lines = MemCollection()

        lines.writerecords([{
            'geometry': {'type': 'LineString', 'coordinates': [(0, 0), (0, 10)]},
            'properties': {'lid': 1, 'name': 'line 3', 'nr': 2, 'direction': 1}
        }, {
            'geometry': {'type': 'LineString', 'coordinates': [(5, 0), (5, 10)]},
            'properties': {'lid': 2, 'name': 'line 4', 'nr': 1, 'direction': -1}
        }])

        points = MemCollection()

        points.writerecords([{
            'geometry': {'type': 'Point', 'coordinates': (0, 1)},
            'properties': {'pid': 1, 'nr': 1, 'correct': 2},
            'selected': {True}
        }, {
            'geometry': {'type': 'Point', 'coordinates': (0, 4)},
            'properties': {'pid': 2, 'nr': 1, 'correct': 3},
            'selected': {True}
        }, {
            'geometry': {'type': 'Point', 'coordinates': (1, 4)},
            'properties': {'pid': 3, 'nr': 1, 'correct': 1},
            'selected': {True}
        }, {
            'geometry': {'type': 'Point', 'coordinates': (5, 2)},
            'properties': {'pid': 4, 'nr': 1, 'correct': 1},
            'selected': {True}
        }, {
            'geometry': {'type': 'Point', 'coordinates': (5, 6)},
            'properties': {'pid': 5, 'nr': 1, 'correct': 0},
            'selected': {True}
        }])

        number_points_on_line(lines, points, line_direction_field='direction', start_number=0)

        nrs = {p['properties']['pid']: p['properties']['nr'] for p in points}
        correct_nrs = {p['properties']['pid']: p['properties']['correct'] for p in points}

        self.assertDictEqual(nrs, correct_nrs)
