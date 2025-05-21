import unittest
from math import isclose
from pathlib import Path
import os
import shutil

from mwcommons import ticdat_utils as utils

import aip_scheduling
from aip_scheduling.visualizer import (
    visualize_schedule_for_minisymposium,
    visualize_schedule_for_session,
    visualize_schedule_for_participant,
    _prepare_minisymposium_schedule_data  # Import the new private helper
)
from test_aip_scheduling.test_data_loader import load_visualization_test_data


cwd = Path(__file__).parent.resolve()
TEST_OUTPUT_DIR = os.path.join(cwd, "test_output_visualizations") 

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
        report_output_dir = os.path.join(cwd, "test_report_builder_output")
        if not os.path.exists(report_output_dir):
            os.makedirs(report_output_dir)
        
        sln = aip_scheduling.report_builder_solve(self.dat, sln, report_output_dir)
        self.assertSetEqual(set(sln.sample_output_table['Data Field']), {'Option 1.0', 'Option 2.0'}, "Report check")
        
        if os.path.exists(report_output_dir):
            shutil.rmtree(report_output_dir)


class TestVisualizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dat, cls.sln = load_visualization_test_data()
        if os.path.exists(TEST_OUTPUT_DIR):
            shutil.rmtree(TEST_OUTPUT_DIR)
        os.makedirs(TEST_OUTPUT_DIR)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_OUTPUT_DIR):
            shutil.rmtree(TEST_OUTPUT_DIR)

    def test_visualize_schedule_for_minisymposium_file_creation(self): # Renamed for clarity
        # Test with an existing minisymposium
        visualize_schedule_for_minisymposium(self.dat, self.sln, "MS1", TEST_OUTPUT_DIR)
        expected_file_ms1 = os.path.join(TEST_OUTPUT_DIR, "schedule_ms_MS1.html")
        self.assertTrue(os.path.exists(expected_file_ms1), f"File {expected_file_ms1} not created.")

        # Test with a non-existent minisymposium
        visualize_schedule_for_minisymposium(self.dat, self.sln, "MS99", TEST_OUTPUT_DIR)
        expected_file_ms99 = os.path.join(TEST_OUTPUT_DIR, "schedule_ms_MS99.html")
        self.assertTrue(os.path.exists(expected_file_ms99), f"File {expected_file_ms99} not created for non-existent MS.")

    def test_prepare_minisymposium_schedule_data_content(self):
        cells_values, title = _prepare_minisymposium_schedule_data(self.dat, self.sln, "MS1")

        # Assert title
        # From test_minissimposios.csv: MS1,Test MS 1,2
        self.assertEqual(title, "Schedule for Minisymposium MS1: Test MS 1")

        # Assert cells_values structure and content
        # cells_values[0] are slot labels: ["Slot 1", "Slot 2", "Slot 3"] (max_row_count is 3 due to Friday)
        self.assertListEqual(cells_values[0], ["Slot 1", "Slot 2", "Slot 3"])
        
        # cells_values[1] is Monday data
        # MS1 B1 is S1/P1, MS1 B2 is S2/P1
        # SESSIONS_PER_DAY = {"Monday": ["S1", "S2"], ...}
        # DAYS_ORDER = ["Monday", "Tuesday", "Thursday", "Friday"]
        # Monday is the first day, so its data is in cells_values[1] (index 0 is slot labels)
        self.assertEqual(cells_values[1][0], "Bloco 1<br>Paralela P1", "Cell for Monday, Slot 1 (S1) for MS1")
        self.assertEqual(cells_values[1][1], "Bloco 2<br>Paralela P1", "Cell for Monday, Slot 2 (S2) for MS1")
        self.assertEqual(cells_values[1][2], "", "Cell for Monday, Slot 3 (no session) for MS1")

        # cells_values[2] is Tuesday data
        # MS1 is not scheduled on Tuesday in test_minisymposium_assignments.csv
        # Tuesday is the second day, so its data is in cells_values[2]
        self.assertEqual(cells_values[2][0], "", "Cell for Tuesday, Slot 1 (S3) for MS1")
        self.assertEqual(cells_values[2][1], "", "Cell for Tuesday, Slot 2 (S4) for MS1")
        self.assertEqual(cells_values[2][2], "", "Cell for Tuesday, Slot 3 (no session) for MS1")

        # cells_values[3] is Thursday data
        self.assertEqual(cells_values[3][0], "", "Cell for Thursday, Slot 1 (S5) for MS1")
        self.assertEqual(cells_values[3][1], "", "Cell for Thursday, Slot 2 (S6) for MS1")
        self.assertEqual(cells_values[3][2], "", "Cell for Thursday, Slot 3 (no session) for MS1")
        
        # cells_values[4] is Friday data
        self.assertEqual(cells_values[4][0], "", "Cell for Friday, Slot 1 (S7) for MS1")
        self.assertEqual(cells_values[4][1], "", "Cell for Friday, Slot 2 (S8) for MS1")
        self.assertEqual(cells_values[4][2], "", "Cell for Friday, Slot 3 (S9) for MS1")


    def test_visualize_schedule_for_session(self):
        # Test with an existing session
        visualize_schedule_for_session(self.sln, "S1", TEST_OUTPUT_DIR)
        expected_file_s1 = os.path.join(TEST_OUTPUT_DIR, "schedule_session_S1.html")
        self.assertTrue(os.path.exists(expected_file_s1), f"File {expected_file_s1} not created.")

        # Test with a non-existent session
        visualize_schedule_for_session(self.sln, "S99", TEST_OUTPUT_DIR)
        expected_file_s99 = os.path.join(TEST_OUTPUT_DIR, "schedule_session_S99.html")
        self.assertTrue(os.path.exists(expected_file_s99), f"File {expected_file_s99} not created for non-existent Session.")

    def test_visualize_schedule_for_participant(self):
        # Test with an existing participant ID (integer, as per schema)
        visualize_schedule_for_participant(self.dat, self.sln, 101, TEST_OUTPUT_DIR)
        expected_file_p101 = os.path.join(TEST_OUTPUT_DIR, "schedule_participant_101.html")
        self.assertTrue(os.path.exists(expected_file_p101), f"File {expected_file_p101} not created.")

        # Test with a non-existent participant ID (integer, as per schema)
        visualize_schedule_for_participant(self.dat, self.sln, 999, TEST_OUTPUT_DIR)
        expected_file_p999 = os.path.join(TEST_OUTPUT_DIR, "schedule_participant_999.html")
        self.assertFalse(os.path.exists(expected_file_p999), f"File {expected_file_p999} was created for non-existent participant, but should not have been.")


if __name__ == '__main__':
    unittest.main()
