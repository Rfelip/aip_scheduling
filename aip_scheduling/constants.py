from enum import StrEnum

APP_OUTPUT_DIR = '/app/output'

class SolverTypes(StrEnum):
    GUROBI = 'Gurobi'
    SCIP = 'SCIP'

class SampleConstants(StrEnum):
    FIRST_VALUE = 'Value 1'
    SECOND_VALUE = 'Value 2'
