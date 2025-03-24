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
    session_weights = [["origem"],["sessão 1","sessão 2","sessão 3","sessão 4","sessão 5","sessão 6",
                       "sessão 7","sessão 8","sessão 9"]],
    paralelas_weights = [["origem"],["paralela 1","paralela 2","paralela 3","paralela 4","paralela 5",
                               	"paralela 6","paralela 7","paralela 8","paralela 9","paralela 10"]],
)

## Restrições de integridade das tabelas
table = 'minisymposiums'
input_schema.set_data_type(table=table, field='ID', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='Nome', **text())
input_schema.set_data_type(table=table, field='Blocks', **positive_integer(min=1, inclusive_min=True))

table = 'symposiums'
input_schema.set_data_type(table=table, field='Symposium_ID', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='Organizer', **text())
input_schema.set_data_type(table=table, field='Blocks', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='Title', **text()) 

table = "person"
input_schema.set_data_type(table=table, field='Nome', **text())
input_schema.set_data_type(table=table, field='Universidade', **text())
input_schema.set_data_type(table=table, field='País', **text())
input_schema.set_data_type(table=table, field='Palestra 1', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='Palestra 2', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='Organiza 1', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='Organiza 2', **positive_integer(min=1, inclusive_min=True))

table = "session_weights"
input_schema.set_data_type(table=table, field='origem', **text())
for i in range(1,9):
    input_schema.set_data_type(table=table, field=f"sessão {i}", **positive_integer(min=0, inclusive_min=True))

table = "paralelas_weights"
input_schema.set_data_type(table=table, field='origem', **text())
for i in range(1,10):
    input_schema.set_data_type(table=table, field=f"paralela {i}", **positive_integer(min=0, inclusive_min=True))

# endregion

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

