from enum import StrEnum

APP_OUTPUT_DIR = '/app/output'

class SolverTypes(StrEnum):
    GUROBI = 'Gurobi'
    SCIP = 'SCIP'
 
APP_OUTPUT_DIR = '/app/output'

class SolverTypes(StrEnum):
    GUROBI = 'Gurobi'
    SCIP = 'SCIP'

# ** Timeslot Information **
TIMESLOT_IDS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"]

# ** Event Location Information **
EVENT_LOCATION_IDS = ["L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8", "L9", "L10"]

# ** Absolute Timeslot Penalties **
# Define these based on your preferences for each timeslot.
# Using a dictionary directly is fine here as it's not a matrix.
# Ensure all TIMESLOT_IDS are keys here.
ABSOLUTE_TIMESLOT_PENALTIES = {
    "S1": 0, "S2": 0, "S3": 5, "S4": 5, "S5": 0,
    "S6": 0, "S7": 10, "S8": 10, "S9": 20,
}
DEFAULT_ABSOLUTE_TIMESLOT_PENALTY = 0.0 # If a timeslot isn't in the dict above (should not happen if populated correctly)

# ** Timeslot Transition Penalty Matrix **
# Rows: Origin Timeslot, Columns: Destination Timeslot
# Order matches TIMESLOT_IDS
_timeslot_transition_penalty_matrix = [
#    S1,  S2,  S3,  S4,  S5,  S6,  S7,  S8,  S9  (To)
    [  0,   0,  11,  12,  23,  24,  35,  36,  37], # S1 (From)
    [100,   0,  10,  11,  22,  23,  34,  35,  36], # S2
    [100, 100,   0,   0,  11,  12,  23,  24,  25], # S3
    [100, 100, 100,   0,  10,  11,  22,  23,  24], # S4
    [100, 100, 100, 100,   0,   0,  11,  12,  13], # S5
    [100, 100, 100, 100, 100,   0,  10,  11,  12], # S6
    [100, 100, 100, 100, 100, 100,   0,   0,   1], # S7
    [100, 100, 100, 100, 100, 100, 100,   0,   0], # S8
    [100, 100, 100, 100, 100, 100, 100, 100,   0], # S9
]
DEFAULT_TIMESLOT_TRANSITION_PENALTY = 100.0 # Default for transitions not covered by the matrix size (e.g. S10 to S1)

# Convert matrix to dictionary: {(origin_ts, dest_ts): penalty}
TIMESLOT_TRANSITION_PENALTIES = {
    (TIMESLOT_IDS[r], TIMESLOT_IDS[c]): _timeslot_transition_penalty_matrix[r][c]
    for r in range(len(TIMESLOT_IDS))
    for c in range(len(TIMESLOT_IDS))
}

# ** Event Location Transition Penalty Matrix **
# Rows: Origin Event Location, Columns: Destination Event Location
# Order matches EVENT_LOCATION_IDS
_event_location_transition_penalty_matrix = [
#    L1,   L2,   L3,   L4,   L5,   L6,   L7,   L8,   L9,  L10 (To)
    [  0, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000], # L1 (From)
    [1000,   0, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000], # L2
    [1000, 1000,   0, 1000, 1000, 1000, 1000, 1000, 1000, 1000], # L3
    [1000, 1000, 1000,   0, 1000, 1000, 1000, 1000, 1000, 1000], # L4
    [1000, 1000, 1000, 1000,   0, 1000, 1000, 1000, 1000, 1000], # L5
    [1000, 1000, 1000, 1000, 1000,   0, 1000, 1000, 1000, 1000], # L6
    [1000, 1000, 1000, 1000, 1000, 1000,   0, 1000, 1000, 1000], # L7
    [1000, 1000, 1000, 1000, 1000, 1000, 1000,   0, 1000, 1000], # L8
    [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000,   0, 1000], # L9
    [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000,   0], # L10
]
DEFAULT_EVENT_LOCATION_TRANSITION_PENALTY = 2000.0 # Default for transitions not covered by matrix size

# Convert matrix to dictionary: {(origin_loc, dest_loc): penalty}
EVENT_LOCATION_TRANSITION_PENALTIES = {
    (EVENT_LOCATION_IDS[r], EVENT_LOCATION_IDS[c]): _event_location_transition_penalty_matrix[r][c]
    for r in range(len(EVENT_LOCATION_IDS))
    for c in range(len(EVENT_LOCATION_IDS))
}


# --- Visualizer Constants ---
# Ensure TIMESLOT_IDS here match those used in penalty definitions
SESSION_TO_DAY_MAPPING = {
    "S1": "Monday", "S2": "Monday",
    "S3": "Tuesday", "S4": "Tuesday",
    "S5": "Thursday", "S6": "Thursday",
    "S7": "Friday", "S8": "Friday", "S9": "Friday",
}
# Check if all TIMESLOT_IDS are covered in SESSION_TO_DAY_MAPPING
for ts_id in TIMESLOT_IDS:
    if ts_id not in SESSION_TO_DAY_MAPPING:
        print(f"Warning: Timeslot ID '{ts_id}' from TIMESLOT_IDS is not in SESSION_TO_DAY_MAPPING.")

DAYS_ORDER = ["Monday", "Tuesday", "Thursday", "Friday"] # This order will be used for display

SESSIONS_PER_DAY = {day: [] for day in DAYS_ORDER}
for session, day in SESSION_TO_DAY_MAPPING.items():
    if day in SESSIONS_PER_DAY:
        SESSIONS_PER_DAY[day].append(session)
    else: # Should not happen if DAYS_ORDER is comprehensive for days in SESSION_TO_DAY_MAPPING
        print(f"Warning: Day '{day}' for session '{session}' not in DAYS_ORDER.")

# Sort sessions within each day if needed (e.g., S1 before S2)
for day in SESSIONS_PER_DAY:
    SESSIONS_PER_DAY[day].sort() # Sorts alphabetically, e.g., "S1", "S2"