import os

import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.graph_objs import Figure

from aip_scheduling.constants import APP_OUTPUT_DIR
from aip_scheduling.visualizer import visualize_schedule_for_minisymposium, visualize_schedule_for_session, visualize_schedule_for_participant


def _save_plot(fig: Figure, plot_name: str, path: str=APP_OUTPUT_DIR):
    """Save plots, as HTML, to the default directory of Mip Hub.

    When executed locally, saves the HTML file to app/output/ (default directory of Mip Hub), or to the specified path.

    :param fig: A figure generated with plotly, using plotly.express or plotly.graph_objects, for instance.
    :param plot_name: Name of the plot to be saved as an HTML file and to be displayed on Mip Hub.
    :param path: Path to the output
    """
    # Ensure the directory exists
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f'{plot_name}.html')
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

    # Call new visualization functions
    if hasattr(sln, 'minisymposium_assignments') and sln.minisymposium_assignments:
        if hasattr(dat, 'minissimposios') and dat.minissimposios:
            # try:
            #     sample_ms_id = next(iter(dat.minissimposios.keys()))
            #     print(f"Generating minisymposium schedule for {sample_ms_id}...")
            #     visualize_schedule_for_minisymposium(dat, sln, sample_ms_id, path)
            # except StopIteration:
            #     print("Warning: dat.minissimposios is not empty but could not get a key.")
            pass # Placeholder for potential future non-sample calls
        else:
            print("Skipping minisymposium schedule: dat.minissimposios is empty or missing.")

        # sample_session_id = "S1" # Assuming S1 is a valid session ID
        # print(f"Generating session schedule for {sample_session_id}...")
        # visualize_schedule_for_session(sln, sample_session_id, path)

        if hasattr(dat, 'pessoas') and dat.pessoas:
            # try:
            #     sample_participant_id = next(iter(dat.pessoas.keys()))
            #     print(f"Generating participant schedule for participant {sample_participant_id}...")
            #     visualize_schedule_for_participant(dat, sln, sample_participant_id, path)
            # except StopIteration:
            #     print("Warning: dat.pessoas is not empty but could not get a key.")
            pass # Placeholder for potential future non-sample calls
        else:
            print("Skipping participant schedule: dat.pessoas is empty or missing.")
    else:
        print("Skipping all new schedule visualizations: sln.minisymposium_assignments is empty or missing.")

    sln.sample_output_table = sample_output_table_df # This line seems to be from the original template
    return sln
