from ticdat import standard_main

from aip_scheduling.main import solve
from aip_scheduling.schemas import input_schema, output_schema


# When run from the command line, will read/write json/xls/csv/db/sql/mdb files
# For example, the next command will read from a model stored in input.xlsx and write solution.xlsx.
#   python -m mip_template -i input.xlsx -o solution.xlsx
if __name__ == "__main__":
    standard_main(input_schema, output_schema, solve)
