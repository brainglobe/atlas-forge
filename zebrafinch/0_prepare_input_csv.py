"""
Prepare input CSV for template creation
==================================================
Reads specimen metadata, standardises columns, sets resolutions,
maps orientation codes, and cleans subject IDs for downstream processing.
"""

from pathlib import Path
import pandas as pd

# updated list Simon gave us
df_ZF = pd.read_csv(Path("zebrafinch/list_ZF_use.csv"))

# Read the 25um and 50um source-paths txt files in the zebrafinch folder as a dict
txt_files = {
    "25um": Path("zebrafinch/images-25um_source-paths.txt"),
    "50um": Path("zebrafinch/images-50um_source-paths.txt")
}

# Create dict with 25um and 25um source image paths
source_paths = {
    key: [l.strip() for l in file.read_text().splitlines() if l.strip()]
    if file.exists() else []
    for key, file in txt_files.items()
}

# Create dict with 25um and 25um source image names
file_names = {
    key: [Path(p).name for p in paths]
    for key, paths in source_paths.items()
}

# Map appropriate columns to new standardised columns in input_csv
input_csv = pd.DataFrame({
    "species": df_ZF['Common name'],
    "sex": df_ZF['Gender (M / F)'],
    "subject_id": df_ZF["Specimen ID"],
    "resolution_z": 50,
    "resolution_y": 50,
    "resolution_x": 50,
    "channel":"green",
    "origin": df_ZF["comments"],
})

# When no plane is mentioned in comments change to PSL
# if TRANSVERSE in origin than change to SAL 
# if SAGGITAL change to LIP TODO: check whether this is correct (!)
for idx, row in input_csv.iterrows():
    origin = str(row['origin']).upper().strip()
    if "TRANSVERSE" in origin:
        input_csv.at[idx, 'origin'] = "SAL"
    elif "SAGGITAL" in origin:
        input_csv.at[idx, 'origin'] = "LIP"
    else:
        input_csv.at[idx, 'origin'] = "PSL"

# Fix subject id of ZF_65
input_csv['subject_id'] = input_csv['subject_id'].str.replace("ZF 65", "ZF65")

# Remove spaces and everything after from subject_id for all rows
input_csv['subject_id'] = input_csv['subject_id'].astype(str).str.split(" ").str[0]

# Extract only the number from subject_id (subject_number)
input_csv['subject_number'] = input_csv['subject_id'].str.extract(r'(\d+)')

# Add ZF_ prefix and a suffix that is the _M or _F
input_csv['subject_id'] = (
    "ZF" +
    input_csv['subject_number'].astype(str) +
    input_csv['sex'].str.lower().str[0]
)

atlas_dir = Path("/ceph/neuroinformatics/neuroinformatics/atlas-forge")
data_dir = atlas_dir / "zebrafinch" / "sourcedata"
for idx, row in input_csv.iterrows():
    subject_number = row["subject_number"]
    file_names_50um = file_names["50um"]
    match = [subject_number in file_name for file_name in file_names_50um]
    if sum(match) > 1:
        print(f"Warning: Multiple filenames matching subject number '{subject_number}'",
              f"found: {[file_names_50um[i] for i, m in enumerate(match) if m]}. "
              "Picking the first one.")
    elif sum(match) == 0:
        print(f"Warning: No filename matching subject number '{subject_number}' found in 50um file names.")
        continue
    file_name = [file_names_50um[i] for i, m in enumerate(match) if m][0]

    # Find match within the data_dir 
    matches = list(data_dir.glob(f"**/{file_name}"))
    if matches:
        file_path = matches[0]
    else:
        print(f"Warning: No file found for '{file_name}' in '{data_dir}'.")
    
    # Add to source_file_path column in input_csv
    input_csv.at[idx, "source_file_path"] = file_path

# Drop subject_number column (only used to match subjects to filenames)
input_csv = input_csv.drop(columns=["subject_number"])

# save csv as template_data_50um.csv in zebrafinch folder
input_csv.to_csv("zebrafinch/template_data_50um.csv", index=False)
