__version__ = "0.1.0"
from aip_scheduling.action_data_prep import data_prep_solve
from aip_scheduling.action_report_builder import report_builder_solve
from aip_scheduling.main import solve
from aip_scheduling.schemas import input_schema, output_schema

# For a configured deployment on Mip Hub see:
# https://github.com/mipwise/mip-go/tree/main/6_deploy/4_configured_deployment
