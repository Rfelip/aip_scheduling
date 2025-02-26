import unittest
from math import isclose
from pathlib import Path

from mwcommons import ticdat_utils as utils

import aip_scheduling


cwd = Path(__file__).parent.resolve()

class TestMipMe(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        dat = utils.read_data(f'{cwd}/data/testing_data/testing_data.json', aip_scheduling.input_schema)
        cls.params = aip_scheduling.input_schema.create_full_parameters_dict(dat)
        cls.dat = dat

    def test_1_action_data_ingestion(self):
        utils.check_data(self.dat, aip_scheduling.input_schema)

    def test_2_action_data_prep(self):
        old_sum = self.dat.sample_input_table['Data Field Two'].sum()
        dat = aip_scheduling.data_prep_solve(self.dat)
        new_sum = dat.sample_input_table['Data Field Two'].sum()
        close_enough = isclose(new_sum, self.params['Sample Float Parameter'] * old_sum, rel_tol=1e-2)
        self.assertTrue(close_enough, "Data prep check")

    def test_3_main_solve(self):
        sln = aip_scheduling.solve(self.dat)
        self.assertSetEqual(set(sln.sample_output_table['Data Field']), {'Option 1', 'Option 2'}, 'Main solve check')

    def test_4_action_report_builder(self):
        sln = aip_scheduling.solve(self.dat)
        sln = aip_scheduling.report_builder_solve(self.dat, sln, f'{cwd}/app/output')
        self.assertSetEqual(set(sln.sample_output_table['Data Field']), {'Option 1.0', 'Option 2.0'}, "Report check")


if __name__ == '__main__':
    unittest.main()
