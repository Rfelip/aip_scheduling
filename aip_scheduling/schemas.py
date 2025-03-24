"""
Defines the input and output schemas of the problem.
For more details on how to implement and configure data schemas see:
https://github.com/mipwise/mip-go/tree/main/5_develop/4_data_schema
"""
from mwcommons.ticdat_types import positive_integer, text, binary
from ticdat import PanDatFactory

from aip_scheduling.constants import SampleConstants


# region INPUT SCHEMA
input_schema = PanDatFactory(
    parameters   = [['Name'], ['Value']],  # Do not change the column names of the parameters table!
    minisymposiums = [['ID'],['Nome', 'Blocks']],
    person = [["Nome"], ['Universidade', 'País', 'Palestra 1','Palestra 2', 'Organiza 1', 'Organiza 2']],
    session_weights = [],
    paralelas_weights = []
)

## Restrições de integridade das tabelas
table = 'minisymposiums'
input_schema.set_data_type(table=table, field='Participant_Name', **text())
input_schema.set_data_type(table=table, field='Symposium_ID', **positive_integer(min=0))
input_schema.set_data_type(table=table, field='Is_Organizer', **binary())


table = 'symposiums'
input_schema.set_data_type(table=table, field='Symposium_ID', **positive_integer(min=0))
input_schema.set_data_type(table=table, field='Organizer', **text())
input_schema.set_data_type(table=table, field='Blocks', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='Title', **text()) 

# region OUTPUT SCHEMA
output_schema = PanDatFactory(
    sample_output_table=[['Primary Key'], ['Data Field']],
)
# endregion

# region DATA TYPES AND PREDICATES - OUTPUT SCHEMA
# region sample_output_table
table = 'sample_output_table'
output_schema.set_data_type(table=table, field='Primary Key', **text())
output_schema.set_data_type(table=table, field='Data Field', **text())
# endregion

