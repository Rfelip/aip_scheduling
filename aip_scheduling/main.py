import collections
import re
from mwcommons.exceptions import ParameterError
from mwcommons.ticdat_utils import set_data_types, set_parameters_datatypes
import pulp as pl

from aip_scheduling.schemas import input_schema, output_schema


def parse_ms_block_string(s: str) -> tuple[str, int] | None:
    """
    Parses a string like "MSx By" into ("MSx", y-1) or "MSx" into ("MSx", -1 if no block).
    Returns None if parsing fails or input is None/empty.
    Block index is returned as 0-indexed.
    """
    if not s:
        return None
    s = s.strip()
    # Try to match "MSx By" pattern
    match_with_block = re.fullmatch(r"(MS\d+)\s+B(\d+)", s, re.IGNORECASE)
    if match_with_block:
        ms_id = match_with_block.group(1).upper()
        block_num = int(match_with_block.group(2))
        return ms_id, block_num - 1  # 0-indexed block

    # Try to match "MSx" pattern (no block specified)
    match_no_block = re.fullmatch(r"(MS\d+)", s, re.IGNORECASE)
    if match_no_block:
        ms_id = match_no_block.group(1).upper()
        return ms_id, -1 # Indicates no specific block, or to apply to all blocks
    
    print(f"Warning: Could not parse MS/Block string: {s}")
    return None

def solve(dat):
    """Solves the AIP Scheduling problem."""

    # --- 1. Data Validation and Parameter Setup ---
    dat = set_data_types(dat=dat, schema=input_schema)
    # Parameters are not used in this version of the model structure, but this is standard practice
    params = input_schema.create_full_parameters_dict(dat)
    params = set_parameters_datatypes(params=params, schema=input_schema)

    # --- 2. Create the LP Problem ---
    prob = pl.LpProblem("AIP_Scheduling", pl.LpMinimize)

    # --- 3. Determine Dimensions and Populate Data Structures from TicDat ---

    # Minisymposia
    ALL_MINISYMPOSIA = sorted(list(dat.minissimposios.keys()))
    minisymposium_n_blocks = {minisymposium_id: data['Blocos'] for minisymposium_id, data in dat.minissimposios.items()}
    max_blocks_per_ms = max(minisymposium_n_blocks.values()) if minisymposium_n_blocks else 0
    
    # Sessions
    ALL_SESSIONS = sorted(list(dat.pesos_sessoes_absolutos.keys()))

    # Parallel Tracks
    track_keys = set()
    if hasattr(dat, 'pesos_paralelas') and dat.pesos_paralelas:
        track_keys.update(k.Paralela_Origem_ID for k in dat.pesos_paralelas)
        track_keys.update(k.Paralela_Destino_ID for k in dat.pesos_paralelas)
    ALL_PARALLEL_TRACKS = sorted(list(track_keys))
    if not ALL_PARALLEL_TRACKS and max_blocks_per_ms > 0 : # Ensure at least one track if there are MSs
        ALL_PARALLEL_TRACKS = ["P1"]


    # For PuLP variable indexing
    minisymposia_ids_range = ALL_MINISYMPOSIA # Renamed for clarity, content is the same
    block_indices_range = range(max_blocks_per_ms) 
    session_ids_range = ALL_SESSIONS # Renamed for clarity
    parallel_track_ids_range = ALL_PARALLEL_TRACKS # Renamed for clarity
    
    # Detailed Minisymposium Info
    # lista_ms_details[minisymposium_id] = {'id': minisymposium_id, 'num_blocks': count}
    lista_ms_details = {minisymposium_id: {'id': minisymposium_id, 'num_blocks': data['Blocos']}
                        for minisymposium_id, data in dat.minissimposios.items()}

    # Gmini: Minisymposium Exclusions
    # Gmini_data[(minisymposium_id_origem, block_index_origem)] = list of (minisymposium_id_excluido, block_index_excluido)
    Gmini_data = collections.defaultdict(list)
    if hasattr(dat, 'minissimposio_exclusions') and dat.minissimposio_exclusions:
        for key_tuple, _ in dat.minissimposio_exclusions.items():
            # key_tuple is (MS_ID_Origem, Bloco_Origem, MS_ID_Excluido, Bloco_Excluido)
            minisymposium_id_origem = key_tuple[0]
            bloco_origem_1_indexed = key_tuple[1]
            minisymposium_id_excluido = key_tuple[2]
            bloco_excluido_1_indexed = key_tuple[3]
            
            # Ensure the MS and their blocks are valid before adding
            if minisymposium_id_origem in minisymposium_n_blocks and \
               1 <= bloco_origem_1_indexed <= minisymposium_n_blocks[minisymposium_id_origem] and \
               minisymposium_id_excluido in minisymposium_n_blocks and \
               1 <= bloco_excluido_1_indexed <= minisymposium_n_blocks[minisymposium_id_excluido]:
                Gmini_data[(minisymposium_id_origem, bloco_origem_1_indexed - 1)].append(
                    (minisymposium_id_excluido, bloco_excluido_1_indexed - 1) # Store as 0-indexed
                )


    # Gspeaker and Gorganizer
    speaker_activities = collections.defaultdict(list)
    organizer_activities = collections.defaultdict(list)
    if hasattr(dat, 'pessoas') and dat.pessoas:
        for person_id, person_data in dat.pessoas.items():
            # Palestras (Speaker activities)
            for palestra_field in ['Palestra_MS_ID_Bloco_1', 'Palestra_MS_ID_Bloco_2']:
                parsed_info = parse_ms_block_string(person_data[palestra_field])
                if parsed_info:
                    minisymposium_id, block_index = parsed_info
                    if minisymposium_id in minisymposium_n_blocks:
                        if block_index != -1: # Specific block given
                             if 0 <= block_index < minisymposium_n_blocks[minisymposium_id]:
                                speaker_activities[person_id].append((minisymposium_id, block_index))
                        else: # No specific block, implies all blocks of that MS for the speaker (unlikely for speaker, but handling)
                            for b_idx_loopvar in range(minisymposium_n_blocks[minisymposium_id]): # Renamed loop var to avoid conflict
                                speaker_activities[person_id].append((minisymposium_id, b_idx_loopvar))
            
            # Organizacao (Organizer activities)
            for organiza_field in ['Organiza_MS_ID_1', 'Organiza_MS_ID_2']:
                parsed_info = parse_ms_block_string(person_data[organiza_field]) # Block info usually not in Organiza fields
                if parsed_info:
                    minisymposium_id, _ = parsed_info # block_index from parse_ms_block_string is ignored for organizers
                    if minisymposium_id in minisymposium_n_blocks:
                        for b_idx_loopvar in range(minisymposium_n_blocks[minisymposium_id]): # Organizer organizes all blocks of the MS
                            organizer_activities[person_id].append((minisymposium_id, b_idx_loopvar))
                            
    Gspeaker_list = [sorted(list(set(activities))) for activities in speaker_activities.values() if activities]
    Gorganizer_list = [sorted(list(set(activities))) for activities in organizer_activities.values() if activities]


    # Gspecial: Pre-assignments (assumed empty as not in schema)
    Gspecial_list = []

    # Weight Dictionaries
    session_transition_costs = {}
    if hasattr(dat, 'pesos_sessoes') and dat.pesos_sessoes:
        for key_tuple, data_row in dat.pesos_sessoes.items():
            # key_tuple is (Sessao_Origem_ID, Sessao_Destino_ID)
            session_transition_costs[(key_tuple[0], key_tuple[1])] = data_row['Peso']

    parallel_track_transition_costs = {}
    if hasattr(dat, 'pesos_paralelas') and dat.pesos_paralelas:
        for key_tuple, data_row in dat.pesos_paralelas.items():
            # key_tuple is (Paralela_Origem_ID, Paralela_Destino_ID)
            parallel_track_transition_costs[(key_tuple[0], key_tuple[1])] = data_row['Peso']
            
    absolute_session_weights = {}
    if hasattr(dat, 'pesos_sessoes_absolutos') and dat.pesos_sessoes_absolutos:
        for key_tuple, data_row in dat.pesos_sessoes_absolutos.items():
            # key_tuple is (Sessao_ID,)
            absolute_session_weights[key_tuple[0]] = data_row['Peso']


    # --- 4. Define PuLP Decision Variables ---
    # x[minisymposium_id, block_index, session_id, parallel_track_id]
    x = pl.LpVariable.dicts("X",
        (minisymposia_ids_range, block_indices_range, session_ids_range, parallel_track_ids_range),
        cat=pl.LpBinary)

    # y[minisymposium_id, block_index_1, block_index_2, session_id_1, session_id_2]
    y = pl.LpVariable.dicts("Y",
        (minisymposia_ids_range, block_indices_range, block_indices_range, session_ids_range, session_ids_range),
        cat=pl.LpBinary)

    # z[minisymposium_id, block_index_1, block_index_2, parallel_track_id_1, parallel_track_id_2]
    z = pl.LpVariable.dicts("Z",
        (minisymposia_ids_range, block_indices_range, block_indices_range, parallel_track_ids_range, parallel_track_ids_range),
        cat=pl.LpBinary)

    minisymposium_block_allocation = x 
    minisymposium_block_session_connection = y
    minisymposium_block_parallel_track_connection = z

    # --- 5. Define Constraints ---
    
    # C1: Each session slot (session_id, parallel_track_id) can host at most one minisymposium block
    for session_id in session_ids_range:
        for parallel_track_id in parallel_track_ids_range:
            prob += pl.lpSum(x[minisymposium_id][block_index][session_id][parallel_track_id] 
                             for minisymposium_id in minisymposia_ids_range 
                             for block_index in range(minisymposium_n_blocks[minisymposium_id])) <= 1, \
                             f"C1_s{session_id}_p{parallel_track_id}"

    # C2: All blocks of a minisymposium must be allocated
    for minisymposium_id in minisymposia_ids_range:
        for block_index in range(minisymposium_n_blocks[minisymposium_id]):
            prob += pl.lpSum(x[minisymposium_id][block_index][session_id][parallel_track_id] 
                             for session_id in session_ids_range 
                             for parallel_track_id in parallel_track_ids_range) == 1, \
                             f"C2_ms{minisymposium_id}_b{block_index}"

    # C3: Minisymposia with mutual exclusion constraints (Gmini_data) cannot be in the same session
    for (minisymposium_id_orig, block_index_orig), excluded_pairs_list in Gmini_data.items():
        for (minisymposium_id_excl, block_index_excl) in excluded_pairs_list:
            for session_id in session_ids_range:
                sum_orig_in_s = pl.lpSum(x[minisymposium_id_orig][block_index_orig][session_id][parallel_track_id] 
                                         for parallel_track_id in parallel_track_ids_range)
                sum_excl_in_s = pl.lpSum(x[minisymposium_id_excl][block_index_excl][session_id][parallel_track_id] 
                                         for parallel_track_id in parallel_track_ids_range)
                prob += sum_orig_in_s + sum_excl_in_s <= 1, \
                        f"C3_ms{minisymposium_id_orig}_b{block_index_orig}_excl_ms{minisymposium_id_excl}_b{block_index_excl}_s{session_id}"
    
    # C4: Speakers cannot present more than one block in the same session
    for speaker_idx, activity_list in enumerate(Gspeaker_list):
        for session_id in session_ids_range:
            prob += pl.lpSum(x[minisymposium_id][block_index][session_id][parallel_track_id] 
                             for minisymposium_id, block_index in activity_list 
                             for parallel_track_id in parallel_track_ids_range
                             if minisymposium_id in x and \
                                block_index < block_indices_range.stop and \
                                session_id in x[minisymposium_id][block_index] and \
                                parallel_track_id in x[minisymposium_id][block_index][session_id]
                             ) <= 1, f"C4_speaker{speaker_idx}_s{session_id}"

    # C5: Organizers cannot have their minisymposia blocks in the same session if they organize multiple
    for organizer_idx, activity_list in enumerate(Gorganizer_list):
        for session_id in session_ids_range:
            prob += pl.lpSum(x[minisymposium_id][block_index][session_id][parallel_track_id] 
                             for minisymposium_id, block_index in activity_list
                             for parallel_track_id in parallel_track_ids_range
                             if minisymposium_id in x and \
                                block_index < block_indices_range.stop and \
                                session_id in x[minisymposium_id][block_index] and \
                                parallel_track_id in x[minisymposium_id][block_index][session_id]
                            ) <= 1, f"C5_organizer{organizer_idx}_s{session_id}"

    # C6: Special assignments (Gspecial_list) must be respected
    for minisymposium_id, block_index, session_id, parallel_track_id in Gspecial_list: 
        if minisymposium_id in ALL_MINISYMPOSIA and \
           0 <= block_index < minisymposium_n_blocks[minisymposium_id] and \
           session_id in ALL_SESSIONS and \
           parallel_track_id in ALL_PARALLEL_TRACKS:
            prob += x[minisymposium_id][block_index][session_id][parallel_track_id] == 1, \
                    f"C6_ms{minisymposium_id}_b{block_index}_s{session_id}_p{parallel_track_id}"

    # C7: Linking minisymposium_block_allocation (x) with minisymposium_block_session_connection (y)
    for minisymposium_id in minisymposia_ids_range:
        num_blocks_for_ms = minisymposium_n_blocks[minisymposium_id]
        if num_blocks_for_ms > 1:
            for block_index_1 in range(num_blocks_for_ms -1):
                for block_index_2 in range(block_index_1 + 1, num_blocks_for_ms): 
                    for session_id_1 in session_ids_range:
                        for session_id_2 in session_ids_range:
                            sum_x_b1_s1 = pl.lpSum(x[minisymposium_id][block_index_1][session_id_1][parallel_track_id] 
                                                   for parallel_track_id in parallel_track_ids_range)
                            sum_x_b2_s2 = pl.lpSum(x[minisymposium_id][block_index_2][session_id_2][parallel_track_id] 
                                                   for parallel_track_id in parallel_track_ids_range)
                            
                            prob += y[minisymposium_id][block_index_1][block_index_2][session_id_1][session_id_2] <= sum_x_b1_s1, \
                                    f"C7a_ms{minisymposium_id}_b1{block_index_1}_b2{block_index_2}_s1{session_id_1}_s2{session_id_2}"
                            prob += y[minisymposium_id][block_index_1][block_index_2][session_id_1][session_id_2] <= sum_x_b2_s2, \
                                    f"C7b_ms{minisymposium_id}_b1{block_index_1}_b2{block_index_2}_s1{session_id_1}_s2{session_id_2}"
                            prob += y[minisymposium_id][block_index_1][block_index_2][session_id_1][session_id_2] >= sum_x_b1_s1 + sum_x_b2_s2 - 1, \
                                    f"C7c_ms{minisymposium_id}_b1{block_index_1}_b2{block_index_2}_s1{session_id_1}_s2{session_id_2}"

    # C8: Linking minisymposium_block_allocation (x) with minisymposium_block_parallel_track_connection (z)
    for minisymposium_id in minisymposia_ids_range:
        num_blocks_for_ms = minisymposium_n_blocks[minisymposium_id]
        if num_blocks_for_ms > 1:
            for block_index_1 in range(num_blocks_for_ms - 1):
                for block_index_2 in range(block_index_1 + 1, num_blocks_for_ms): 
                    for parallel_track_id_1 in parallel_track_ids_range:
                        for parallel_track_id_2 in parallel_track_ids_range:
                            sum_x_b1_p1 = pl.lpSum(x[minisymposium_id][block_index_1][session_id][parallel_track_id_1] 
                                                   for session_id in session_ids_range)
                            sum_x_b2_p2 = pl.lpSum(x[minisymposium_id][block_index_2][session_id][parallel_track_id_2] 
                                                   for session_id in session_ids_range)

                            prob += z[minisymposium_id][block_index_1][block_index_2][parallel_track_id_1][parallel_track_id_2] <= sum_x_b1_p1, \
                                    f"C8a_ms{minisymposium_id}_b1{block_index_1}_b2{block_index_2}_p1{parallel_track_id_1}_p2{parallel_track_id_2}"
                            prob += z[minisymposium_id][block_index_1][block_index_2][parallel_track_id_1][parallel_track_id_2] <= sum_x_b2_p2, \
                                    f"C8b_ms{minisymposium_id}_b1{block_index_1}_b2{block_index_2}_p1{parallel_track_id_1}_p2{parallel_track_id_2}"
                            prob += z[minisymposium_id][block_index_1][block_index_2][parallel_track_id_1][parallel_track_id_2] >= sum_x_b1_p1 + sum_x_b2_p2 - 1, \
                                    f"C8c_ms{minisymposium_id}_b1{block_index_1}_b2{block_index_2}_p1{parallel_track_id_1}_p2{parallel_track_id_2}"


    # --- 6. Define Objective Function ---
    DEFAULT_PENALTY = 0 

    # Part 1: Minimize costs related to session transitions
    session_transition_cost_objective = pl.lpSum(
        y[minisymposium_id][block_index_1][block_index_2][session_id_1][session_id_2] * 
        session_transition_costs.get((session_id_1, session_id_2), DEFAULT_PENALTY)
        for minisymposium_id in minisymposia_ids_range
        if minisymposium_n_blocks[minisymposium_id] > 1
        for block_index_1 in range(minisymposium_n_blocks[minisymposium_id] -1)
        for block_index_2 in range(block_index_1 + 1, minisymposium_n_blocks[minisymposium_id])
        for session_id_1 in session_ids_range
        for session_id_2 in session_ids_range
    )
    
    # Part 2: Minimize costs related to parallel track transitions
    parallel_track_transition_cost_objective = pl.lpSum(
        z[minisymposium_id][block_index_1][block_index_2][parallel_track_id_1][parallel_track_id_2] * 
        parallel_track_transition_costs.get((parallel_track_id_1, parallel_track_id_2), DEFAULT_PENALTY)
        for minisymposium_id in minisymposia_ids_range
        if minisymposium_n_blocks[minisymposium_id] > 1
        for block_index_1 in range(minisymposium_n_blocks[minisymposium_id] - 1)
        for block_index_2 in range(block_index_1 + 1, minisymposium_n_blocks[minisymposium_id])
        for parallel_track_id_1 in parallel_track_ids_range
        for parallel_track_id_2 in parallel_track_ids_range
    )

    # Part 3: Minimize costs related to absolute session assignments
    absolute_session_weight_objective = pl.lpSum(
        x[minisymposium_id][block_index][session_id][parallel_track_id] * 
        absolute_session_weights.get(session_id, DEFAULT_PENALTY)
        for minisymposium_id in minisymposia_ids_range
        for block_index in range(minisymposium_n_blocks[minisymposium_id])
        for session_id in session_ids_range
        for parallel_track_id in parallel_track_ids_range
    )

    # Total objective function
    objective = session_transition_cost_objective + parallel_track_transition_cost_objective + absolute_session_weight_objective
    prob += objective, "MinimizeSchedulingCosts"

    # --- 7. Solve the Problem ---
    prob.solve() 
    print(f"Solution Status: {pl.LpStatus[prob.status]}")

    # --- 8. Populate Output Schema ---
    sln = output_schema.PanDat()
    
    solution_summary_data = []
    minisymposium_assignments_data = []

    if prob.status == pl.LpStatusOptimal or prob.status == pl.LpStatusFeasible:
        solution_summary_data.append({'Metric': 'Objective Value', 'Value': str(pl.value(prob.objective))})
        solution_summary_data.append({'Metric': 'Status', 'Value': pl.LpStatus[prob.status]})

        for minisymposium_id in minisymposia_ids_range:
            for block_index in range(minisymposium_n_blocks[minisymposium_id]):
                for session_id in session_ids_range:
                    for parallel_track_id in parallel_track_ids_range:
                        # Check if the variable exists before accessing varValue, due to sparse definition if some indices are invalid
                        current_var = minisymposium_block_allocation.get((minisymposium_id, block_index, session_id, parallel_track_id))
                        if current_var and current_var.varValue is not None and current_var.varValue > 0.99:
                            minisymposium_assignments_data.append({
                                'MS_ID': minisymposium_id,
                                'Bloco_ID': block_index + 1,  # 1-indexed for output
                                'Sessao_ID': session_id,
                                'Paralela_ID': parallel_track_id
                            })
    else:
        solution_summary_data.append({'Metric': 'Status', 'Value': pl.LpStatus[prob.status]})
        solution_summary_data.append({'Metric': 'Objective Value', 'Value': 'N/A'})


    if hasattr(sln, 'solution_summary') and hasattr(sln, 'minisymposium_assignments'):
        sln.solution_summary = solution_summary_data
        sln.minisymposium_assignments = minisymposium_assignments_data
    else:
        # This case should ideally not happen if output_schema is defined correctly
        print("Warning: output_schema.solution_summary or output_schema.minisymposium_assignments not found.")
        # Fallback: try to create them if they are missing (though PanDatFactory usually defines them)
        if not hasattr(sln, 'solution_summary'):
             sln.solution_summary = solution_summary_data
        if not hasattr(sln, 'minisymposium_assignments'):
             sln.minisymposium_assignments = minisymposium_assignments_data
             
    return sln
