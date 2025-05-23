"""
Defines the input and output schemas of the problem.
For more details on how to implement and configure data schemas see:
https://github.com/mipwise/mip-go/tree/main/5_develop/4_data_schema
"""
from mwcommons.ticdat_types import positive_integer, text, binary
from ticdat import PanDatFactory
input_schema = PanDatFactory(
    parameters   = [['Name'], ['Value']],  # Do not change the column names of the parameters table!
    minisymposiums = [['Minisymposium ID'],['Nome', 'Quantidade de Blocos']],
    participants = [['Participante ID'], ['Nome', 'Universidade', 'País']],
    lectures = [['Palestra ID'], ['Minisymposium ID']],
    participants_minisymposums = [['Participante ID', 'Minisymposium ID'], ['Função']],
    sessions = [['Sessão ID'], ['Description', 'Dia', 'Horário', 'Quantidade de Salas']],# Salas == Paralelas
    session_weights = [["Sessão Precedente", "Sessão Sequente"], ["Peso"]],
    rooms_weights = [['Sala Precedente', 'Sala Sequente'], ['Peso']],
)

from aip_scheduling.constants import SampleConstants


# region INPUT SCHEMA

## Restrições de integridade das tabelas
table = 'minisymposiums'
input_schema.set_data_type(table=table, field='Minisymposium ID', **text())
input_schema.set_data_type(table=table, field='Nome', **text())
input_schema.set_data_type(table=table, field='Quantidade de Blocos', **positive_integer(min=1, inclusive_min=True))

table = "participants"
input_schema.set_data_type(table=table, field='Participante ID', **text())
input_schema.set_data_type(table=table, field='Nome', **text())
input_schema.set_data_type(table=table, field='Universidade', **text())
input_schema.set_data_type(table=table, field='País', **text())

table = "lectures"
input_schema.set_data_type(table=table, field='Palestra ID', **text())
input_schema.set_data_type(table=table, field='Minisymposium ID', **text())
input_schema.add_foreign_key(native_table=table, foreign_table='minisymposiums', mappings=['Minisymposium ID', 'Minisymposium ID'])


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

