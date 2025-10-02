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

import ants
import pandas as pd
from loguru import logger

from brainglobe_space import AnatomicalSpace
from brainglobe_template_builder.io import (
    load_tiff,
    save_as_asr_nii,
)

# TODO: check whether similar functions already exist elsewhere, 
# if so use those, if not add below functions to template-builder

def species_name_to_id(species_name: str) -> str:
    """Return species ID as uppercase string with no spaces."""
    return "".join(e.upper() for e in species_name.split())

from typing import Dict

def info_to_filename(image_info: Dict) -> str:
    """
    Generate a standardized filename from dictionary with keys:
        - 'subject_id'
        - 'channel'
        - 'resolution_z'
        - 'resolution_y'
        - 'resolution_x'

    Raises:
    - KeyError if any required key is missing.
    """
    zyx_res = res_from_info(image_info)
    filename =  (
            f"sub-{image_info['subject_id']}_"
            f"channel-{image_info['channel']}_"
            f"res-{zyx_res[0]}x{zyx_res[1]}x{zyx_res[2]}um_"
            "origin-asr"
        )
    return filename

def res_from_info(image_info: Dict) -> list[float]:
        return [
            image_info["resolution_z"],
            image_info["resolution_y"],
            image_info["resolution_x"]
        ]

# %%
# Define input file path, atlas-forge directory, and species for which to create template
# --------------------------------------------------------------------------------------
input_csv_path = Path("zebrafinch/template_data_25um.csv")
atlas_dir = Path("/ceph/neuroinformatics/neuroinformatics/atlas-forge")
species = "Zebra finch"

# %%
# Create template directories, load input data, and set up logs
# -------------------------------------------

for res in [25,50]:
    input_csv_path = Path(f"zebrafinch/template_data_{res}um.csv")
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
    nii_paths = []
    for idx, image_info in df.iterrows():
        source_path = Path(image_info.source_filepath)

        # Reorient the image to ASR
        image = load_tiff(source_path)
        logger.debug(f"Loaded image {source_path.name} with shape: {image.shape}.")
        source_origin = [str(letter).upper() for letter in image_info.origin]
        target_origin = ["A", "S", "R"]
        source_space = AnatomicalSpace(source_origin, shape=image.shape)
        image_asr = source_space.map_stack_to(target_origin, image)
        logger.debug(f"Reoriented image from {source_origin} to {target_origin}.")
        logger.debug(f"Reoriented image shape: {image_asr.shape}.")

        # Create rawdata / subject folder
        rawdata_subject_folder = species_dir / "rawdata" / f"sub-{image_info['subject_id']}"
        rawdata_subject_folder.mkdir(exist_ok=True)

        # Save reoriented images in NIfTI format 
        df.at[idx, "brainglobe_image_name"] = info_to_filename(image_info)
        nii_path = rawdata_subject_folder / f"{info_to_filename(image_info)}.nii.gz"
        df.at[idx, "rawdata_filepath"] = nii_path
        save_as_asr_nii(image_asr, res_from_info(image_info),nii_path)
        logger.debug(f"Saved reoriented image as {nii_path.name}.")

    # Save csv with input data and standardised image names for included subjects
    # -------------------------------------
    df.to_csv(species_dir / "rawdata" / f"{today}_{res}um_subjects.csv", index=False)

    for idx, image_info in df.iterrows():
        rawdata_path = Path(image_info.rawdata_filepath)

        # Create derivatives / subject folder
        derivatives_subject_folder = species_dir / "derivatives" / f"sub-{image_info['subject_id']}"
        derivatives_subject_folder.mkdir(exist_ok=True)

        # Bias field correction (to homogenise intensities)
        image_ants = ants.image_read(rawdata_path.as_posix())
        image_n4 = ants.n4_bias_field_correction(image_ants)
        image_n4_path =  derivatives_subject_folder / f"{info_to_filename(image_info)}_N4.nii.gz"
        ants.image_write(image_n4, image_n4_path.as_posix())
        logger.debug(
            f"Created N4 bias field corrected image as {image_n4_path.name}."
        )

