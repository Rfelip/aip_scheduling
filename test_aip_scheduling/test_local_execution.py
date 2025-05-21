import unittest
from pathlib import Path

from mwcommons import ticdat_utils as utils

import aip_scheduling


cwd = Path(__file__).parent.resolve()

class TestLocalExecution(unittest.TestCase):
    """
    THIS IS NOT UNIT TESTING! Unit testing are implemented in other scripts.

    This class only serves the purpose of conveniently (with one click) executing solve engines locally during
    development.

    In addition, the methods in this class mimic the execution flow that a user typically experience on a Mip Hub app.
    """

    def test_1_action_data_ingestion(self):
        dat = utils.read_data(f'{cwd}/data/testing_data/testing_data.json', aip_scheduling.input_schema)
        utils.check_data(dat, aip_scheduling.input_schema)
        utils.write_data(dat, f'{cwd}/data/inputs', aip_scheduling.input_schema)

    def test_2_action_data_prep(self):
        dat = utils.read_data(f'{cwd}/data/inputs', aip_scheduling.input_schema)
        dat = aip_scheduling.data_prep_solve(dat)
        utils.write_data(dat, f'{cwd}/data/inputs', aip_scheduling.input_schema)

    def test_3_main_solve(self):
        dat = utils.read_data(f'{cwd}/data/inputs', aip_scheduling.input_schema)
        sln = aip_scheduling.solve(dat)
        utils.write_data(sln, f'{cwd}/data/outputs', aip_scheduling.output_schema)

    def test_4_action_report_builder(self):
        dat = utils.read_data(f'{cwd}/data/inputs', aip_scheduling.input_schema)
        sln = utils.read_data(f'{cwd}/data/outputs', aip_scheduling.output_schema)
        sln = aip_scheduling.report_builder_solve(dat, sln, f'{cwd}/app/output')
        utils.write_data(sln, f'{cwd}/data/outputs', aip_scheduling.output_schema)

    def test_5_solve_with_sample_data(self):
        """
        Tests the main solve function with a minimal, consistent sample dataset.
        """
        from aip_scheduling.schemas import input_schema, output_schema # Ensure schemas are loaded
        from aip_scheduling.main import solve # Import the solve function

        sample_data_path = Path(cwd, "sample_test_data")

        # Verify that all necessary CSV files exist before trying to load
        required_files = [
            "minissimposios.csv", "pessoas.csv", "minissimposio_exclusions.csv",
            "pesos_sessoes_absolutos.csv", "pesos_sessoes.csv", 
            "pesos_paralelas.csv", "parameters.csv"
        ]
        for f_name in required_files:
            self.assertTrue((sample_data_path / f_name).exists(), f"{f_name} not found in sample_test_data")

        # Load data using input_schema
        dat = input_schema.csv.create_tic_dat(str(sample_data_path))
        
        # Perform data integrity checks (optional, but good practice)
        # utils.check_data(dat, input_schema) # Might be too strict if some tables are allowed to be empty

        # Call the solve function
        sln = solve(dat)

        # Assertions
        self.assertIsNotNone(sln, "The solution object should not be None.")

        # Check solution_summary table
        self.assertTrue(hasattr(sln, 'solution_summary'), "sln object missing solution_summary table")
        summary_table = sln.solution_summary
        
        self.assertIsInstance(summary_table, list, "solution_summary should be a list of dicts")
        self.assertGreater(len(summary_table), 0, "solution_summary should not be empty")

        status_row = next((row for row in summary_table if row.get('Metric') == 'Status'), None)
        self.assertIsNotNone(status_row, "Status metric not found in solution_summary")
        
        solution_status = status_row.get('Value')
        self.assertIn(solution_status, ['Optimal', 'Feasible'], 
                      f"Solution status was '{solution_status}', expected 'Optimal' or 'Feasible'.")

        if solution_status in ['Optimal', 'Feasible']:
            self.assertTrue(hasattr(sln, 'minisymposium_assignments'), 
                            "sln object missing minisymposium_assignments table")
            assignments_table = sln.minisymposium_assignments
            self.assertIsInstance(assignments_table, list, "minisymposium_assignments should be a list of dicts")
            self.assertGreater(len(assignments_table), 0, 
                               "minisymposium_assignments should not be empty for an Optimal/Feasible solution.")
            
            # Check for expected columns in minisymposium_assignments
            if len(assignments_table) > 0:
                expected_columns = ['MS_ID', 'Bloco_ID', 'Sessao_ID', 'Paralela_ID']
                for col in expected_columns:
                    self.assertIn(col, assignments_table[0], f"Column '{col}' missing in minisymposium_assignments")


if __name__ == '__main__':
    unittest.main()
