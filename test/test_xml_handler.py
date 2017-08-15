import unittest
import os.path
import tempfile
import shutil

from gistools.utils.collection import MemCollection
from gistools.utils.xml_handler import import_xml_to_memcollection

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestXMLHandler(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_import_xml_to_memcollection(self):
        """test import xml metfile with metingen to Memcollection"""
        
        xml_file = os.path.join(os.path.dirname(__file__), 'data', 'Metfile_profielen_generiek.met')

        point_col, line_col, ttlr_col, records_errors = import_xml_to_memcollection(xml_file, 'z1z2')
        
#         self.assertEqual(len(point_col), 2)
#         
#         self.assertDictEqual(point_col[0]['properties'],
#                              {'veld1': 'a',
#                               'veld2': 'b',
#                               'veld3': 'c'})
#         self.assertDictEqual(point_col[1]['properties'],
#                              {'veld1': '1',
#                               'veld2': '2',
#                               'veld3': '3'})        

        
        pass
