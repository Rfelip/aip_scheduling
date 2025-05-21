"""
Defines the input and output schemas of the problem.
For more details on how to implement and configure data schemas see:
https://github.com/mipwise/mip-go/tree/main/5_develop/4_data_schema
"""
from mwcommons.ticdat_types import positive_integer, non_negative_integer, string_types, numeric_types, integer_types
from ticdat import PanDatFactory

# region INPUT SCHEMA
input_schema = PanDatFactory(
    parameters=[['Name'], ['Value']],  # Standard parameters table, can be populated later if needed.
    pessoas=[['ID'], ['Nome', 'Palestra_MS_ID_Bloco_1', 'Palestra_MS_ID_Bloco_2', 'Organiza_MS_ID_1', 'Organiza_MS_ID_2']],
    minissimposios=[['MS_ID'], ['Nome_MS', 'Blocos']],
    minissimposio_exclusions=[['MS_ID_Origem', 'Bloco_Origem', 'MS_ID_Excluido', 'Bloco_Excluido'], []],
    pesos_sessoes=[['Sessao_Origem_ID', 'Sessao_Destino_ID'], ['Peso']],
    pesos_paralelas=[['Paralela_Origem_ID', 'Paralela_Destino_ID'], ['Peso']],
    pesos_sessoes_absolutos=[['Sessao_ID'], ['Peso']]
)

# --- Data types and constraints for input_schema ---

# Pessoas table
table = 'pessoas'
input_schema.set_data_type(table=table, field='ID', **integer_types(min=0, inclusive_min=True)) # Assuming ID is an integer
input_schema.set_data_type(table=table, field='Nome', **string_types())
input_schema.set_data_type(table=table, field='Palestra_MS_ID_Bloco_1', **string_types(allow_null=True)) # e.g., "MS1 B1"
input_schema.set_data_type(table=table, field='Palestra_MS_ID_Bloco_2', **string_types(allow_null=True)) # e.g., "MS2 B1"
input_schema.set_data_type(table=table, field='Organiza_MS_ID_1', **string_types(allow_null=True)) # e.g., "MS3"
input_schema.set_data_type(table=table, field='Organiza_MS_ID_2', **string_types(allow_null=True)) # e.g., "MS4"

# Minissimposios table
table = 'minissimposios'
input_schema.set_data_type(table=table, field='MS_ID', **string_types()) # e.g., "MS1"
input_schema.set_data_type(table=table, field='Nome_MS', **string_types())
input_schema.set_data_type(table=table, field='Blocos', **positive_integer(min=1, inclusive_min=True))

# Minissimposio_exclusions table
table = 'minissimposio_exclusions'
input_schema.set_data_type(table=table, field='MS_ID_Origem', **string_types())
input_schema.set_data_type(table=table, field='Bloco_Origem', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='MS_ID_Excluido', **string_types())
input_schema.set_data_type(table=table, field='Bloco_Excluido', **positive_integer(min=1, inclusive_min=True))
input_schema.add_foreign_key(native_table=table, foreign_table='minissimposios',
                             mappings=[('MS_ID_Origem', 'MS_ID')])
# Consider adding a foreign key for MS_ID_Excluido to minissimposios.MS_ID as well, if appropriate.
# input_schema.add_foreign_key(native_table=table, foreign_table='minissimposios',
# mappings=[('MS_ID_Excluido', 'MS_ID')])

# Pesos_sessoes table
table = 'pesos_sessoes'
input_schema.set_data_type(table=table, field='Sessao_Origem_ID', **string_types()) # e.g., "S1"
input_schema.set_data_type(table=table, field='Sessao_Destino_ID', **string_types()) # e.g., "S2"
input_schema.set_data_type(table=table, field='Peso', **numeric_types())

# Pesos_paralelas table
table = 'pesos_paralelas'
input_schema.set_data_type(table=table, field='Paralela_Origem_ID', **string_types()) # e.g., "P1"
input_schema.set_data_type(table=table, field='Paralela_Destino_ID', **string_types()) # e.g., "P2"
input_schema.set_data_type(table=table, field='Peso', **numeric_types())

# Pesos_sessoes_absolutos table
table = 'pesos_sessoes_absolutos'
input_schema.set_data_type(table=table, field='Sessao_ID', **string_types()) # e.g., "S1"
input_schema.set_data_type(table=table, field='Peso', **numeric_types())

# Remove default parameters if any were auto-generated for the old schema
# (PanDatFactory typically creates an empty 'parameters' table by default if not specified otherwise)
# For example, clearing any default parameters or ensuring only specific ones exist:
input_schema.parameters.columns = [['Name'], ['Value']] # Resets to standard empty
# Or, if you want to explicitly define some parameters (example):
# input_schema.add_parameter("TimeLimit", default_value=3600, **numeric_types(min=0))
# input_schema.add_parameter("SolverName", default_value="CBC", **string_types())

# endregion

# region OUTPUT SCHEMA
output_schema = PanDatFactory(
    solution_summary=[['Metric'], ['Value']], 
    minisymposium_assignments=[['MS_ID', 'Bloco_ID'], ['Sessao_ID', 'Paralela_ID']],
    # Add other output tables as needed based on how solution should be presented
)
# endregion

# region DATA TYPES AND PREDICATES - OUTPUT SCHEMA
table = 'solution_summary'
output_schema.set_data_type(table=table, field='Metric', **string_types())
output_schema.set_data_type(table=table, field='Value', **string_types())

table = 'minisymposium_assignments'
output_schema.set_data_type(table=table, field='MS_ID', **string_types())
output_schema.set_data_type(table=table, field='Bloco_ID', **positive_integer()) # Assuming 1-indexed block ID
output_schema.set_data_type(table=table, field='Sessao_ID', **string_types())
output_schema.set_data_type(table=table, field='Paralela_ID', **string_types())

# Remove the old sample_output_table if it exists and is not wanted
if 'sample_output_table' in output_schema.all_tables:
    # This part is tricky with PanDatFactory as direct table removal is not standard.
    # Usually, you define the factory with only the tables you want.
    # For this case, I've redefined output_schema above without sample_output_table.
    pass

# endregion

