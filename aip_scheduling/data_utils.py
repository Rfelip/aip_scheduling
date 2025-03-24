import pandas as pd
import re

def split_at_first_number_regex(text):
    """Splits a string into two parts at the first number (sequence of digits) using regex.

    Args:
        text: The input string.

    Returns:
        A tuple containing the two parts of the string, or (text, "") if no number is found.
    """
    if type(text) != str:
        return ""
    name_list = []
    match = re.search(r"\d+", text)
    while match or text != "":
        split_index = match.start()
        name_list.append((text[:split_index].split(",")[0], text[match.start():match.end()]))
        text = text[match.end():]
        match = re.search(r"\d+", text) 
    return name_list

def build_dataframe_from_organizers(organizers_info):
    data = []
    for (idx, info) in enumerate(organizers_info):
        row = {}
        row['Nome'] = info[0] # First element is always the name
        if len(info) == 4:
            row['Universidade'] = info[1]
            row['País'] = info[2]
        elif len(info) == 3:
            row['Universidade'] = info[1]
            row['País'] = None
        else:
            row['Universidade'] = None
            row['País'] = None
            
        row['Organiza 1'] = info[-1]
        data.append(row)
    df = pd.DataFrame(data)
    return df

def merge_duplicate_organizers_rows(df):

    df_copy = df.copy()
    duplicate_mask = df_copy.duplicated(subset=["Nome"], keep=False)
    duplicate_rows = df_copy[duplicate_mask].sort_values(by=["Nome"])
    non_duplicate_rows = df_copy[~duplicate_mask]

    merged_rows = []
    processed_names = set()

    for index, row in duplicate_rows.iterrows():
        name = row["Nome"]

        if name in processed_names:
            continue

        # Find all rows with the same "Nome"
        matching_rows = duplicate_rows[duplicate_rows["Nome"] == name]

        if len(matching_rows) == 2:
            first_row = matching_rows.iloc[0]
            merged_row = {
                "Nome": first_row["Nome"],
                "Universidade": first_row["Universidade"],
                "País": first_row["País"],
                'Organiza 1': first_row['Organiza 1'],
                'Organiza 2': matching_rows.iloc[1]['Organiza 1']
            }
            merged_rows.append(merged_row)
            processed_names.add(name)

    # Create a DataFrame from the merged rows
    if merged_rows:
        merged_df = pd.DataFrame(merged_rows)
    else:
        merged_df = pd.DataFrame(columns=df.columns.tolist() + ['Organiza 2'])

    # Concatenate the merged rows with the non-duplicate rows
    result_df = pd.concat([non_duplicate_rows, merged_df], ignore_index=True)

    # Reorder columns to match the original order, with MS_ID_2 at the end
    original_columns = df.columns.tolist()
    if 'Organiza 2' in result_df.columns:
        result_df = result_df[original_columns + ['Organiza 2']]
    else:
        result_df = result_df[original_columns]
    result_df.fillna(value = "", inplace=True)
    return result_df

def build_speaker_df(organizers_info):
    data = []
    for info in organizers_info:
        row = {}
        row['Nome'] = info[0] # First element is always the name
        row['Palestra 1'] = info[-1]
        data.append(row)
    df = pd.DataFrame(data)
    return df

def merge_duplicate_speark_rows(df):

    df_copy = df.copy()
    duplicate_mask = df_copy.duplicated(subset=["Nome"], keep=False)
    duplicate_rows = df_copy[duplicate_mask].sort_values(by=["Nome"])
    non_duplicate_rows = df_copy[~duplicate_mask]

    merged_rows = []
    processed_names = set()

    for index, row in duplicate_rows.iterrows():
        name = row["Nome"]

        if name in processed_names:
            continue

        # Find all rows with the same "Nome"
        matching_rows = duplicate_rows[duplicate_rows["Nome"] == name]

        if len(matching_rows) == 2:
            first_row = matching_rows.iloc[0]
            merged_row = {
                "Nome": first_row["Nome"],
                'Palestra 1': first_row['Palestra 1'],
                'Palestra 2': matching_rows.iloc[1]['Palestra 1']
            }
            merged_rows.append(merged_row)
            processed_names.add(name)
        else:
            print(f"Alguém está em {len(matching_rows)} palestras.")

    # Create a DataFrame from the merged rows
    if merged_rows:
        merged_df = pd.DataFrame(merged_rows)
    else:
        merged_df = pd.DataFrame(columns=df.columns.tolist() + ['Palestra 2'])

    # Concatenate the merged rows with the non-duplicate rows
    result_df = pd.concat([non_duplicate_rows, merged_df], ignore_index=True)

    # Reorder columns to match the original order, with MS_ID_2 at the end
    original_columns = df.columns.tolist()
    if 'Palestra 2' in result_df.columns:
        result_df = result_df[original_columns + ['Palestra 2']]
    else:
        result_df = result_df[original_columns]
    result_df.fillna(value = "", inplace=True)
    return result_df

def create_person_sheet(path_to_ms_proposals):
    MS = pd.read_excel(path_to_ms_proposals)

    organizers = MS["ORGANIZERS"].str.split(";")
    flattened_list = [item+f", "+str(id_ms + 1) for (id_ms, sublist) in enumerate(organizers) if isinstance(sublist, list) for item in sublist]
    name_list = [name.strip().split(",") for name  in flattened_list]
    organizers_information = [name for name in name_list if name[0] != ""]
    df = build_dataframe_from_organizers(organizers_information)
    result_df = merge_duplicate_organizers_rows(df)

    speakers = MS["SPEAKERS"].to_list()
    speaker_name_list = []
    for (idx,ms) in enumerate(speakers):
        speaker_name_list += split_at_first_number_regex(ms)
    speaker_df = build_speaker_df(speaker_name_list)
    result_speakers_df = merge_duplicate_speark_rows(speaker_df)

    pessoas_df = pd.merge(result_speakers_df, result_df, on = "Nome", how = "outer").fillna("")
    desired_column_order = [
        "Nome","Universidade","País", "Palestra 1","Palestra 2","Organiza 1","Organiza 2"]
    pessoas_df = pessoas_df[desired_column_order]
    
    return pessoas_df