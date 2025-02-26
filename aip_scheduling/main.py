from mwcommons.exceptions import ParameterError
from mwcommons.ticdat_utils import set_data_types, set_parameters_datatypes

from aip_scheduling.schemas import input_schema, output_schema


def solve(dat):
    """Sample solve engine."""
    dat = set_data_types(dat=dat, schema=input_schema)
    params = input_schema.create_full_parameters_dict(dat)
    params = set_parameters_datatypes(params=params, schema=input_schema)
    sample_input_table_df = dat.sample_input_table.copy()
    if params['Sample Two Values Parameter'] == 'Value 1':
        sample_output_table_df = sample_input_table_df[['Primary Key One', 'Data Field One']]
    elif params['Sample Two Values Parameter'] == 'Value 2':
        sample_output_table_df = sample_input_table_df[['Primary Key Two', 'Data Field Two']]
    else:
        raise ParameterError(f"bad value for 'Sample Two Values Parameter': {params['Sample Two Values Parameter']}")
    sample_output_table_df.rename(
        columns={'Primary Key One': 'Primary Key', 'Data Field One': 'Data Field'}, inplace=True)
    sln = output_schema.PanDat()
    sln.sample_output_table = sample_output_table_df
    return sln
