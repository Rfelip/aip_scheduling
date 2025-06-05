from mwcommons.ticdat_types import positive_integer, text

# region INPUT SCHEMA
input_schema = PanDatFactory(
    # General parameters for the solver or model configuration
    parameters=[['Name'], ['Value']],

    # Information about people involved (speakers, organizers)
    pessoas=[
        ['ID'],  # Primary Key: Unique identifier for a person (e.g., name or specific ID)
        ['Nome',  # Full name of the person
         'Palestra_MS_ID_Bloco_1',  # Minisymposium and Block for first presentation (e.g., "MS1 B1")
         'Palestra_MS_ID_Bloco_2',  # Minisymposium and Block for second presentation
         'Organiza_MS_ID_1',        # First Minisymposium organized (e.g., "MS3")
         'Organiza_MS_ID_2']        # Second Minisymposium organized
    ],

    # Details about each minisymposium
    minissimposios=[
        ['MS_ID'],    # Primary Key: Unique identifier for the minisymposium (e.g., "MS1")
        ['Nome_MS',   # Full name/title of the minisymposium
         'Blocos']    # Number of blocks this minisymposium consists of
    ],

    # Rules for minisymposium blocks that cannot be scheduled in the same timeslot
    minissimposio_exclusions=[
        ['MS_ID_Origem', 'Bloco_Origem', 'MS_ID_Excluido', 'Bloco_Excluido'], # Composite Primary Key
        []  # No data fields, the existence of the row defines the exclusion
    ]
    # Note: Penalty tables (timeslot_transition_penalties, event_location_transition_penalties,
    # absolute_timeslot_penalties) have been removed from the input schema.
    # Their values are now defined in constants.py.
)

table = 'pessoas'
input_schema.set_data_type(table=table, field='ID', **text()) # Using text as ID, could be 'Nome' or a specific str ID
input_schema.set_data_type(table=table, field='Nome', **text())
input_schema.set_data_type(table=table, field='Palestra_MS_ID_Bloco_1', **text())
input_schema.set_data_type(table=table, field='Palestra_MS_ID_Bloco_2', **text())
input_schema.set_data_type(table=table, field='Organiza_MS_ID_1', **text())
input_schema.set_data_type(table=table, field='Organiza_MS_ID_2', **text())

table = 'minissimposios'
input_schema.set_data_type(table=table, field='MS_ID', **text())
input_schema.set_data_type(table=table, field='Nome_MS', **text())
input_schema.set_data_type(table=table, field='Blocos', **positive_integer(min=1, inclusive_min=True))

table = 'minissimposio_exclusions'
input_schema.set_data_type(table=table, field='MS_ID_Origem', **text())
input_schema.set_data_type(table=table, field='Bloco_Origem', **positive_integer(min=1, inclusive_min=True))
input_schema.set_data_type(table=table, field='MS_ID_Excluido', **text())
input_schema.set_data_type(table=table, field='Bloco_Excluido', **positive_integer(min=1, inclusive_min=True))

# Foreign keys for minissimposio_exclusions to ensure MS IDs are valid
input_schema.add_foreign_key(native_table=table, foreign_table='minissimposios',
                             mappings=[('MS_ID_Origem', 'MS_ID')])
input_schema.add_foreign_key(native_table=table, foreign_table='minissimposios',
                             mappings=[('MS_ID_Excluido', 'MS_ID')])

output_schema = PanDatFactory(
    solution_summary=[
        ['Metric'],  # Primary Key: Name of the metric (e.g., "Objective Value", "Status")
        ['Value']    # Value of the metric
    ],
    minisymposium_assignments=[
        ['MS_ID', 'Bloco_ID'],  # Composite Primary Key: Identifies the specific minisymposium block
        ['Timeslot_ID',         # The Timeslot ID where this block is scheduled
         'EventLocation_ID']    # The Event Location ID where this block is scheduled
    ]
)

table = 'solution_summary'
output_schema.set_data_type(table=table, field='Metric', **text())
output_schema.set_data_type(table=table, field='Value', **text())

table = 'minisymposium_assignments'
output_schema.set_data_type(table=table, field='MS_ID', **text())
output_schema.set_data_type(table=table, field='Bloco_ID', **positive_integer(min=1, inclusive_min=True)) # Output as 1-indexed
output_schema.set_data_type(table=table, field='Timeslot_ID', **text())
output_schema.set_data_type(table=table, field='EventLocation_ID', **text())