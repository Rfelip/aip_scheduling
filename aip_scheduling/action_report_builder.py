import os

import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.graph_objs import Figure

from aip_scheduling.constants import APP_OUTPUT_DIR


def _save_plot(fig: Figure, plot_name: str, path: str=APP_OUTPUT_DIR):
    """Save plots, as HTML, to the default directory of Mip Hub.

    When executed locally, saves the HTML file to app/output/ (default directory of Mip Hub), or to the specified path.

    :param fig: A figure generated with plotly, using plotly.express or plotly.graph_objects, for instance.
    :param plot_name: Name of the plot to be saved as an HTML file and to be displayed on Mip Hub.
    :param path: Path to the output
    """
    file_path = os.path.join(f'{path}/{plot_name}.html')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    fig.write_html(file_path)


def report_builder_solve(dat, sln, path=APP_OUTPUT_DIR):
    """Sample output action."""
    sample_input_table_df = dat.sample_input_table.copy()
    sample_output_table_df = sln.sample_output_table.copy()
    sample_output_table_df['Data Field'] = sample_input_table_df['Data Field One'] + '.0'
    # region build plots
    kpis_df = sample_input_table_df.copy()
    kpis_values = list(zip(kpis_df['Primary Key One'], kpis_df['Data Field Two']))
    fig = go.Figure(go.Bar(
        x=[value for kpi, value in kpis_values],
        y=[kpi for kpi, value in kpis_values],
        orientation='h'))
    fig.update_layout(title='Costs Breakdown')
    _save_plot(fig, 'KPISummary', path)
    fig = ff.create_table(sample_output_table_df)
    _save_plot(fig, 'TablePlot', path)
    # endregion
    sln.sample_output_table = sample_output_table_df
    return sln
