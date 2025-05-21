# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper to load test data for visualization tests."""

import os
from ticdat import PanDatFactory
from aip_scheduling.schemas import input_schema, output_schema

# Define the directory containing the test CSV files
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_test_data", "visualization_tests")

# Define file paths
MINISSIMPOSIOS_CSV = os.path.join(TEST_DATA_DIR, "test_minissimposios.csv")
PESSOAS_CSV = os.path.join(TEST_DATA_DIR, "test_pessoas.csv")
ASSIGNMENTS_CSV = os.path.join(TEST_DATA_DIR, "test_minisymposium_assignments.csv")

def load_visualization_test_data():
    """
    Loads test data from CSV files into TicDat objects for visualization tests.

    Returns:
        A tuple (dat, sln) where:
            dat: An input_schema.TicDat object populated with data from
                 test_minissimposios.csv and test_pessoas.csv.
            sln: An output_schema.TicDat object populated with data from
                 test_minisymposium_assignments.csv.
    """
    # Create an input TicDat object
    dat = input_schema.TicDat()

    # Populate dat.minissimposios
    # Schema definition for minissimposios:
    #   Primary Key: MS_ID (string)
    #   Fields: Nome_MS (string), Blocos (number)
    # create_tic_dat_from_csv should handle types based on schema.
    # If schema types are 'string' for all, explicit conversion for 'Blocos' might be needed
    # after loading, or schema needs to be accurate. Assuming schema is accurate.
    minissimposios_dat = input_schema.csv.create_tic_dat_from_csv(
        TEST_DATA_DIR, freeze_datatypes=True
    )
    if hasattr(minissimposios_dat, 'test_minissimposios'):
         for pkey, row in minissimposios_dat.test_minissimposios.items():
            dat.minissimposios[pkey] = row

    # Populate dat.pessoas
    # Schema definition for pessoas:
    #   Primary Key: ID (typically string or number, schema dependent)
    #   Fields: Nome (string), Palestra_MS_ID_Bloco_1 (string), etc.
    pessoas_dat = input_schema.csv.create_tic_dat_from_csv(
        TEST_DATA_DIR, freeze_datatypes=True
    )
    if hasattr(pessoas_dat, 'test_pessoas'):
        for pkey, row in pessoas_dat.test_pessoas.items():
            dat.pessoas[pkey] = row
            
    # Create an output TicDat object
    sln = output_schema.TicDat()

    # Populate sln.minisymposium_assignments
    # Schema definition for minisymposium_assignments:
    #   Primary Key: (MS_ID (string), Bloco_ID (number))
    #   Fields: Sessao_ID (string), Paralela_ID (string)
    # create_tic_dat_from_csv should handle types based on schema.
    assignments_dat = output_schema.csv.create_tic_dat_from_csv(
        TEST_DATA_DIR, freeze_datatypes=True
    )
    if hasattr(assignments_dat, 'test_minisymposium_assignments'):
        for pkey, row in assignments_dat.test_minisymposium_assignments.items():
            sln.minisymposium_assignments[pkey] = row
            
    return dat, sln

if __name__ == '__main__':
    # Example of how to use the loader
    # This part is for testing the loader itself and won't run during pytest
    
    # Mock schemas if not running in the full project context for testing
    class MockSchema:
        def __init__(self):
            self.TicDat = PanDatFactory()
            self.csv = None # This would need more mocking for stand-alone execution
    
    # Check if the schemas are properly imported, otherwise use mocks (very basic)
    try:
        from aip_scheduling.schemas import input_schema, output_schema
        print("Real schemas loaded.")
    except ImportError:
        print("Failed to load real schemas, using basic mock (will likely fail for CSV loading).")
        input_schema = MockSchema()
        output_schema = MockSchema()
        # Further mocking input_schema.csv.create_tic_dat_from_csv would be needed

    # Create dummy CSV files for standalone testing if they don't exist
    if not os.path.exists(TEST_DATA_DIR):
        os.makedirs(TEST_DATA_DIR)

    if not os.path.exists(MINISSIMPOSIOS_CSV):
        with open(MINISSIMPOSIOS_CSV, "w") as f:
            f.write("MS_ID,Nome_MS,Blocos\nMS1,Test MS 1,2\nMS2,Test MS 2,1\n")
    
    if not os.path.exists(PESSOAS_CSV):
        with open(PESSOAS_CSV, "w") as f:
            f.write("ID,Nome,Palestra_MS_ID_Bloco_1,Palestra_MS_ID_Bloco_2,Organiza_MS_ID_1,Organiza_MS_ID_2\n"
                    "101,Organizer Alpha,MS1 B1,,MS1,\n"
                    "102,Speaker Beta,MS1 B2,MS2 B1,,\n"
                    "103,Multi Role Gamma,,MS2 B1,MS2,\n")

    if not os.path.exists(ASSIGNMENTS_CSV):
        with open(ASSIGNMENTS_CSV, "w") as f:
            f.write("MS_ID,Bloco_ID,Sessao_ID,Paralela_ID\n"
                    "MS1,1,S1,P1\nMS1,2,S2,P1\nMS2,1,S1,P2\n")

    # Attempt to load data
    # Note: This direct execution might fail if aip_scheduling.schemas cannot be resolved
    # or if ticdat is not installed.
    try:
        loaded_dat, loaded_sln = load_visualization_test_data()
        print("\n--- Loaded dat (Input Data) ---")
        if hasattr(loaded_dat, 'minissimposios') and loaded_dat.minissimposios:
            print("\nMinissimposios:")
            for r in loaded_dat.minissimposios.values():
                print(r)
        if hasattr(loaded_dat, 'pessoas') and loaded_dat.pessoas:
            print("\nPessoas:")
            for r in loaded_dat.pessoas.values():
                print(r)
        
        print("\n--- Loaded sln (Solution Data) ---")
        if hasattr(loaded_sln, 'minisymposium_assignments') and loaded_sln.minisymposium_assignments:
            print("\nMinisymposium Assignments:")
            for r in loaded_sln.minisymposium_assignments.values():
                print(r)
        
        print("\nData loading test complete.")

    except Exception as e:
        print(f"\nError during standalone test of data loader: {e}")
        print("This might be due to missing dependencies (ticdat, aip_scheduling.schemas) "
              "or incorrect paths if run from an unexpected directory.")
