from typing import NamedTuple


# Example constants' class. It starts with an underscore to indicate it's not meant to be imported elsewhere.
# The reason is its CLASS attributes are not unmutable, but their instances' attributes are. So we instantiate it
# in the module, and this instance is supposed to be imported.
class _SolverTypes(NamedTuple):
    GUROBI: str = 'Gurobi'
    SCIP: str = 'SCIP'

class _SampleConstants(NamedTuple):
    FIRST_VALUE: str = 'Value 1'
    SECOND_VALUE: str = 'Value 2'

# e.g. SAMPLE_CONSTANTS.FIRST_VALUE returns the string 'Value 1'. It can be used elsewhere to check equality.
SAMPLE_CONSTANTS = _SampleConstants()
