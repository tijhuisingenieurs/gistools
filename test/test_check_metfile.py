import unittest
import os.path
import pandas as pd
import numpy as np

from gistools.tools.check_metfile import check_metfile

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Create dataframeresult of the test, that should be the result
headers = ['Profielnaam', 'Missende afsluiting profiel', 'Fout in profielinformatie', 'Fout in afsluiting meting',
           'Fout in metinginformatie']

df_original_metingen = pd.DataFrame([['fout_in_meting_1','-','-','-','ja'],['fout_in_meting_2','-','-','-','ja'],
                            ['fout_in_meting_3','-','-','-','ja'],['fout_in_meting_afsluiting','-','-','ja','-'],
                            ['fout_in_meting_4','-','-','-','ja']], columns = headers)

df_original_profielen = pd.DataFrame([['fout_in_afsluiting','ja','-','-','-'],[np.nan,'ja','ja','-','-'],
                            ['fout_in_profiel_info P3','-','ja','-','-']], columns = headers)

df_original_correct = pd.DataFrame([], columns = headers)

class TestCheckMetfile(unittest.TestCase):
    def setUp(self):
        pass

    def test_checkmetfile_metingen(self):
        path_input = os.path.join(test_data_dir, 'check_metfile_tool/Test_metfile_metingen.met')
        path_output = os.path.join(test_data_dir, 'check_metfile_tool/Test_output_metfile_metingen.xlsx')

        # do the function
        check_metfile(path_input,path_output)

        # Read the created xslx output and check the values
        df_testoutput = pd.read_excel(path_output)

        # Check of the testoutput gelijk is aan de originele
        self.assertEqual(df_testoutput.equals(df_original_metingen),True)


    def test_checkmetfile_profielen(self):
        path_input = os.path.join(test_data_dir, 'check_metfile_tool/Test_metfile_profielen.met')
        path_output = os.path.join(test_data_dir, 'check_metfile_tool/Test_output_metfile_profielen.xlsx')

        # do the function
        check_metfile(path_input,path_output)

        # Read the created xslx output and check the values
        df_testoutput = pd.read_excel(path_output)

        # Check of the testoutput gelijk is aan de originele
        self.assertEqual(df_testoutput.equals(df_original_profielen),True)


    def test_checkmetfile_correct(self):
        path_input = os.path.join(test_data_dir, 'check_metfile_tool/Test_metfile_correct.met')
        path_output = os.path.join(test_data_dir, 'check_metfile_tool/Test_output_metfile_correct.xlsx')

        # do the function
        check_metfile(path_input,path_output)

        # Read the created xslx output and check the values
        df_testoutput = pd.read_excel(path_output)

        # Check of the testoutput gelijk is aan de originele
        self.assertEqual(df_testoutput.equals(df_original_correct),True)
