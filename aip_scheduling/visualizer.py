# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Visualizer for AIP scheduling."""

import os
import re # For _parse_ms_block
import plotly.graph_objects as go
from collections import defaultdict # For scheduled_participant_activities

from aip_scheduling.constants import APP_OUTPUT_DIR
from . import SESSION_TO_DAY_MAPPING, DAYS_ORDER, SESSIONS_PER_DAY

SESSION_TO_DAY_MAPPING = {
    "S1": "Monday",
    "S2": "Monday",
    "S3": "Tuesday",
    "S4": "Tuesday",
    "S5": "Thursday",
    "S6": "Thursday",
    "S7": "Friday",
    "S8": "Friday",
    "S9": "Friday",
}

DAYS_ORDER = ["Monday", "Tuesday", "Thursday", "Friday"]

SESSIONS_PER_DAY = {
    "Monday": ["S1", "S2"],
    "Tuesday": ["S3", "S4"],
    "Thursday": ["S5", "S6"],
    "Friday": ["S7", "S8", "S9"],
}


def _save_plot(fig: go.Figure, plot_name: str, path: str):
    # Saves plots as HTML to the specified path.
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, f'{plot_name}.html')
    fig.write_html(file_path)


def _prepare_minisymposium_schedule_data(dat, sln, ms_id: str):
    """
    Prepares the data required for visualizing a minisymposium schedule.

    Args:
        dat: Input TicDat object containing the minisymposia data.
        sln: Solution TicDat object containing the schedule assignments.
        ms_id: String, the ID of the minisymposium to visualize.

    Returns:
        A tuple (cells_values, plot_title):
            cells_values: List of lists for Plotly table cells.
            plot_title: String, the title for the plot.
    """
    scheduled_blocks_info = {}
    if hasattr(sln, 'minisymposium_assignments') and sln.minisymposium_assignments:
        for key, row in sln.minisymposium_assignments.items():
            if key[0] == ms_id: # key[0] is MS_ID, key[1] is Bloco_ID
                scheduled_blocks_info[row['Sessao_ID']] = {'bloco': key[1], 'paralela': row['Paralela_ID']}

    max_row_count = max(len(s) for s in SESSIONS_PER_DAY.values()) if SESSIONS_PER_DAY else 0

    cells_values = []

    # First column (Session Slot labels)
    session_slot_labels = [f"Slot {i+1}" for i in range(max_row_count)]
    cells_values.append(session_slot_labels)

    # Subsequent columns (Data for each day in DAYS_ORDER)
    for day in DAYS_ORDER:
        day_column_cells = []
        sessions_for_this_day = SESSIONS_PER_DAY.get(day, [])
        for i in range(max_row_count):
            cell_text = ""  # Default to empty
            if i < len(sessions_for_this_day):
                sess_id = sessions_for_this_day[i]
                if sess_id in scheduled_blocks_info:
                    details = scheduled_blocks_info[sess_id]
                    cell_text = f"Bloco {details['bloco']}<br>Paralela {details['paralela']}"
            day_column_cells.append(cell_text)
        cells_values.append(day_column_cells)

    ms_name = ""
    if hasattr(dat, 'minissimposios') and dat.minissimposios and ms_id in dat.minissimposios:
        ms_name = dat.minissimposios[ms_id].get('Nome_MS', '')

    plot_title = f"Schedule for Minisymposium {ms_id}{f': {ms_name}' if ms_name else ''}"
    
    return cells_values, plot_title


def visualize_schedule_for_minisymposium(dat, sln, ms_id: str, output_dir: str = None):
    """
    Visualizes the schedule for a given minisymposium as an HTML table.

    Args:
        dat: Input TicDat object containing the minisymposia data.
        sln: Solution TicDat object containing the schedule assignments.
        ms_id: String, the ID of the minisymposium to visualize (e.g., "MS1").
        output_dir: Optional string, the directory to save the plot.
                    Defaults to APP_OUTPUT_DIR.
    """
    if output_dir is None:
        output_dir = APP_OUTPUT_DIR
    
    cells_values, plot_title = _prepare_minisymposium_schedule_data(dat, sln, ms_id)

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>Session Slot</b>'] + [f'<b>{day}</b>' for day in DAYS_ORDER],
                    fill_color='paleturquoise',
                    align=['left', 'center'],
                    font=dict(size=14)),
        cells=dict(values=cells_values,
                   fill_color='lavender',
                   align=['left', 'center'],
                   font=dict(size=12),
                   height=30)
    )])

    fig.update_layout(title_text=plot_title, title_x=0.5)

    plot_name = f"schedule_ms_{ms_id}"
    _save_plot(fig, plot_name, output_dir)


def visualize_schedule_for_session(sln, session_id: str, output_dir: str = None):
    """
    Visualizes the minisymposia scheduled in a specific session as an HTML table.

    Args:
        sln: Solution TicDat object containing the schedule assignments.
        session_id: String, the ID of the session to visualize (e.g., "S1").
        output_dir: Optional string, the directory to save the plot.
                    Defaults to APP_OUTPUT_DIR.
    """
    if output_dir is None:
        output_dir = APP_OUTPUT_DIR

    assignments_in_session = {}
    if hasattr(sln, 'minisymposium_assignments') and sln.minisymposium_assignments:
        assignments_in_session = {key: row for key, row in sln.minisymposium_assignments.items() 
                                  if row['Sessao_ID'] == session_id}

    day = SESSION_TO_DAY_MAPPING.get(session_id, 'Unknown Day')

    table_data = []
    if assignments_in_session:
        for ms_key, assignment_details in assignments_in_session.items():
            table_data.append([ms_key[0], ms_key[1], assignment_details['Paralela_ID']])

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>Minisymposium ID</b>', '<b>Bloco ID</b>', '<b>Paralela ID</b>'],
                    fill_color='paleturquoise',
                    align='left',
                    font=dict(size=14)),
        cells=dict(values=list(zip(*table_data)) if table_data else [[]]*3, 
                   fill_color='lavender',
                   align='left',
                   font=dict(size=12),
                   height=30)
    )])

    plot_title = f"Minisymposia Scheduled in Session {session_id} ({day})"
    fig.update_layout(title_text=plot_title, title_x=0.5)

    plot_name = f"schedule_session_{session_id}"
    _save_plot(fig, plot_name, output_dir)


def visualize_schedule_for_participant(dat, sln, participant_id, output_dir: str = None):
    """
    Visualizes the schedule for a given participant as an HTML table.

    Args:
        dat: Input TicDat object.
        sln: Solution TicDat object.
        participant_id: ID of the participant.
        output_dir: Optional directory to save the plot. Defaults to APP_OUTPUT_DIR.
    """
    if output_dir is None:
        output_dir = APP_OUTPUT_DIR

    if not (hasattr(dat, 'pessoas') and participant_id in dat.pessoas):
        print(f"Warning: Participant ID {participant_id} not found in input data.")
        return

    person_data = dat.pessoas[participant_id]
    participant_name = person_data['Nome']

    def _parse_ms_block(ms_block_str: str):
        if not ms_block_str or not isinstance(ms_block_str, str):
            return None, None
        parts = ms_block_str.strip().split()
        ms_id = parts[0]
        bloco_id_str = None
        if len(parts) > 1 and parts[1].startswith('B') and parts[1][1:].isdigit():
            bloco_id_str = parts[1]
        elif len(parts) > 1 : # Could be just MS_ID and then some other text not representing block
            # check if the second part is B<number>
            match = re.match(r"(B\d+)", parts[1])
            if match:
                bloco_id_str = match.group(1)
            # If not, it might be just the MS_ID, so bloco_id_str remains None
        return ms_id, bloco_id_str

    involved_ms_blocks = []
    speaker_fields = ['Palestra_MS_ID_Bloco_1', 'Palestra_MS_ID_Bloco_2']
    for field in speaker_fields:
        if person_data.get(field): # Use .get for safety if field might be missing
            ms_id, bloco_str = _parse_ms_block(person_data[field])
            if ms_id: # Ensure ms_id was parsed
                involved_ms_blocks.append((ms_id, bloco_str, "Speaker"))

    organizer_fields = ['Organiza_MS_ID_1', 'Organiza_MS_ID_2']
    for field in organizer_fields:
        if person_data.get(field):
            ms_id, _ = _parse_ms_block(person_data[field]) # Block is not relevant for organizers here
            if ms_id:
                involved_ms_blocks.append((ms_id, None, "Organizer"))
    
    scheduled_participant_activities = defaultdict(list)
    if hasattr(sln, 'minisymposium_assignments') and sln.minisymposium_assignments:
        for (assigned_ms_id, assigned_bloco_num), assignment_row in sln.minisymposium_assignments.items():
            for ms_id, bloco_id_str, role in involved_ms_blocks:
                if assigned_ms_id == ms_id:
                    activity_key = (assignment_row['Sessao_ID'], assignment_row['Paralela_ID'])
                    if role == "Organizer":
                        activity_text = f"{ms_id} ({role})"
                        if activity_text not in scheduled_participant_activities[activity_key]:
                            scheduled_participant_activities[activity_key].append(activity_text)
                    elif role == "Speaker":
                        parsed_bloco_num = None
                        if bloco_id_str and bloco_id_str.startswith('B') and bloco_id_str[1:].isdigit():
                            parsed_bloco_num = int(bloco_id_str[1:])
                        
                        if parsed_bloco_num == assigned_bloco_num:
                            activity_text = f"{ms_id} ({role}, Bloco {assigned_bloco_num})"
                            if activity_text not in scheduled_participant_activities[activity_key]:
                                scheduled_participant_activities[activity_key].append(activity_text)

    max_row_count = max(len(s) for s in SESSIONS_PER_DAY.values()) if SESSIONS_PER_DAY else 0
    cells_values = []

    session_slot_labels = [f"Slot {i+1}" for i in range(max_row_count)]
    cells_values.append(session_slot_labels)

    for day in DAYS_ORDER:
        day_column_cells = []
        sessions_for_this_day = SESSIONS_PER_DAY.get(day, [])
        for i in range(max_row_count):
            cell_text_parts = []
            if i < len(sessions_for_this_day):
                sess_id = sessions_for_this_day[i]
                # Iterate through scheduled activities for this session_id, grouped by paralela
                activities_by_paralela_in_session = defaultdict(list)
                for (act_sess_id, act_paralela_id), activities in scheduled_participant_activities.items():
                    if act_sess_id == sess_id:
                        activities_by_paralela_in_session[act_paralela_id].extend(activities)
                
                for paralela_id, activities in sorted(activities_by_paralela_in_session.items()):
                    # Remove duplicates from activities list just in case, though earlier logic should prevent it
                    unique_activities = sorted(list(set(activities))) 
                    cell_text_parts.append(f"P{paralela_id}: {', '.join(unique_activities)}")
            
            day_column_cells.append("<br>".join(cell_text_parts))
        cells_values.append(day_column_cells)

    fig = go.Figure(data=[go.Table(
        header=dict(values=['<b>Session Slot</b>'] + [f'<b>{day}</b>' for day in DAYS_ORDER],
                    fill_color='paleturquoise',
                    align=['left', 'center'],
                    font=dict(size=14)),
        cells=dict(values=cells_values,
                   fill_color='lavender',
                   align=['left', 'center'],
                   font=dict(size=12),
                   height=40) # Increased height for potentially more text
    )])

    plot_title = f"Schedule for {participant_name} (ID: {participant_id})"
    fig.update_layout(title_text=plot_title, title_x=0.5)

    plot_name = f"schedule_participant_{participant_id}"
    _save_plot(fig, plot_name, output_dir)
