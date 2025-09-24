"""
Identify source images for template and save in ASR NIfTI format
==============================================
Set up project directory with all relevant data and identify source images
to be used for building the ZebraFinch template.

The source images will be reoriented to ASR, their names standardised,
and they will be saved as NIfTI files in the rawdata folder.
"""
# %%
# Imports
# -------
import os
from datetime import date
from pathlib import Path

import pandas as pd
from loguru import logger

from brainglobe_space import AnatomicalSpace
from brainglobe_template_builder.io import (
    load_tiff,
    save_as_asr_nii,
)

def species_name_to_id(species_name: str) -> str:
    """Return species ID as uppercase string with no spaces."""
    return "".join(e.upper() for e in species_name.split())

# %%
# Define input file path, atlas-forge directory, and species for which to create template
# --------------------------------------------------------------------------------------
input_csv_path = Path("zebrafinch/template_data_50um.csv")
atlas_dir = Path("/ceph/neuroinformatics/neuroinformatics/atlas-forge")
species = "Zebra finch"

# %%
# Create template directories, load input data, and set up logs
# -------------------------------------------

# Load input data
input_df = pd.read_csv(input_csv_path)
assert isinstance(species, str), "species must be a string" #TODO: make into test
df = input_df[input_df["species"] == species]

# Make "rawdata", "derivatives", "templates", and "logs" directories inside a species folder
species_id = species_name_to_id(species)
species_dir = atlas_dir / species_id
species_dir.mkdir(parents=True, exist_ok=True)
for folder in ["rawdata", "derivatives", "templates", "logs"]:
    (species_dir / folder).mkdir(exist_ok=True)

# Set up logging
today = date.today()
current_script_name = os.path.basename(__file__).replace(".py", "")
logger.add(species_dir / "logs" / f"{today}_{current_script_name}.log")
logger.info(f"Will save outputs to {species_dir}.")

# %%
# Load source images and reorient them to ASR
# -------------------------------------------

for idx, image_info in df.iterrows():
    source_path = Path(image_info.source_file_path)
    if not source_path.exists():
        logger.error(f"Source image not found: {source_path}")
        raise FileNotFoundError(f"Source image not found: {source_path}")

    # Reorient the image to ASR
    image = load_tiff(source_path)
    logger.debug(f"Loaded image {source_path.name} with shape: {image.shape}.")
    source_origin = [str(letter).upper() for letter in image_info.origin]
    target_origin = ["A", "S", "R"]
    source_space = AnatomicalSpace(source_origin, shape=image.shape)
    image_asr = source_space.map_stack_to(target_origin, image)
    logger.debug(f"Reoriented image from {source_origin} to {target_origin}.")
    logger.debug(f"Reoriented image shape: {image_asr.shape}.")

    # Create standardised image name
    res_xyz = [image_info.resolution_z, image_info.resolution_y, image_info.resolution_x]
    brainglobe_image_name = (
        f"sub-{image_info['subject_id']}_"
        f"channel-{image_info['channel']}_"
        f"res-{res_xyz[0]}x{res_xyz[1]}x{res_xyz[2]}um_"
        "origin-asr"
    )
    df.at[idx, "brainglobe_image_name"] = brainglobe_image_name

    # Save reoriented images in NIfTI format 
    subject_folder = species_dir / "rawdata" / f"sub-{image_info['subject_id']}"
    subject_folder.mkdir(exist_ok=True)
    nii_path = subject_folder / f"{brainglobe_image_name}.nii.gz"
    save_as_asr_nii(image_asr, res_xyz, nii_path)
    logger.debug(f"Saved reoriented image as {nii_path.name}.")

# %%
# Save input data with standardised image names to species rawdata directory
# -------------------------------------
df.to_csv(species_dir / "sourcedata" / f"{today}_subjects.csv", index=False)
