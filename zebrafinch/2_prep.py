"""
Prepare low-resolution ZebraFinch images for template construction
================================================================
The following operations are performed on the lowest-resolution images to
prepare them for template construction:
- Generate brain mask based on N4-corrected image
- Split the image and mask into hemispheres and reflect each hemisphere
- Generate symmetric brains using either the left or right hemisphere
- Save all resulting images as nifti files to be used for template construction
"""

# %%
# Imports
# -------
import os
from datetime import date
from pathlib import Path

import ants
import numpy as np
import pandas as pd
from loguru import logger

from brainglobe_template_builder.io import (
    file_path_with_suffix,
)
from brainglobe_template_builder.preproc.masking import create_mask
from brainglobe_template_builder.preproc.splitting import (
    save_array_dict_to_nii,
)

from brainglobe_template_builder.preproc.splitting import (
    get_right_and_left_slices,
    save_array_dict_to_nii,
)

# %%
# Setup
# -----
# Define some global variables, including paths to input and output directories
# and set up logging.

os.environ["QT_QPA_PLATFORM"] = "offscreen"
# Define voxel size(in microns) of the lowest resolution image
lowres = 50 
# String to identify the resolution in filenames
res_str = f"res-{lowres}um"
# Define voxel sizes in mm (for Nifti saving)
vox_sizes = [lowres * 1e-3] * 3  # in mm

# Prepare directory structure
atlas_dir = Path("/ceph/neuroinformatics/neuroinformatics/atlas-forge")
species_id = "ZebraFinch"
species_dir = atlas_dir / species_id
rawdata_dir = species_dir / "rawdata"
deriv_dir = species_dir / "derivatives"
assert deriv_dir.exists(), f"Could not find derivatives directory {deriv_dir}."

# Set up logging
today = date.today()
current_script_name = os.path.basename(__file__).replace(".py", "")
logger.add(species_dir / "logs" / f"{today}_{current_script_name}.log")

# Load input data
lowres_df = pd.read_csv(Path(f"zebrafinch/template_data_{lowres}um.csv"))
lowres_template_df = lowres_df.iloc[0:3,:] # just first three for test


# %%
# Run the pipeline for each subject
# ---------------------------------
# Create a dictionary to store the paths to the use4template directories
# per subject. These will contain all necessary images for template building.
csv_files = [file for file in os.listdir(rawdata_dir) if ".csv" in file]
lowres_csv_file = [file for file in csv_files if f"{lowres}um" in file][0]

# Load input data
lowres_df = pd.read_csv(rawdata_dir / lowres_csv_file)

lowres_template_df = lowres_df.iloc[0:3,:] # just first three for test #TODO: add all brains (!)

use4template_dirs = {}
for idx, row in lowres_template_df.iterrows():
   
    row.brainglobe_image_name 
    image_path = deriv_dir / f"sub-{row.subject_id}" / f"{row.brainglobe_image_name}.nii.gz"
    
    # Save the image as nifti
    image_n4_path = file_path_with_suffix(image_path, "_N4")

    image_n4 = ants.image_read(image_n4_path.as_posix())
    # Generate a brain mask based on the N4-corrected image
    mask_data = create_mask(
        image_n4.numpy(),
        gauss_sigma=3,
        threshold_method="triangle",
        closing_size=5,
    )
    mask_path = file_path_with_suffix(image_path, "_N4_mask")
    mask = image_n4.new_image_like(mask_data.astype(np.uint8))
    ants.image_write(mask, mask_path.as_posix())
    logger.debug(
        f"Generated brain mask with shape: {mask.shape} "
        f"and saved as {mask_path.name}."
    )

    # Plot the mask over the image to check
    mask_plot_path = (
       deriv_dir / f"sub-{row.subject_id}" / f"{row.brainglobe_image_name}_N4_mask-overlay.png"
    )
    ants.plot(
        image_n4,
        mask,
        overlay_alpha=0.5,
        axis=1,
        title="Brain mask over image",
        filename=mask_plot_path.as_posix(),
    )
    logger.debug("Plotted overlay to visually check mask.")

    output_prefix = file_path_with_suffix(image_path, "_N4_aligned_", new_ext="")
    # Generate arrays for template construction and save as niftis
    use4template_dir = Path(output_prefix.as_posix() + "padded_use4template")
    # if it exists, delete existing files in it
    if use4template_dir.exists():
        logger.warning(f"Removing existing files in {use4template_dir}.")
        for file in use4template_dir.glob("*"):
            file.unlink()
    use4template_dir.mkdir(exist_ok=True)

    image_n4 = image_n4.numpy()
    mask = mask.numpy()
    right_hemi_slices, left_hemi_slices = get_right_and_left_slices(image_n4)

    array_dict = {
        f"{use4template_dir}/{row.brainglobe_image_name}_asym-brain": np.pad(
            image_n4, pad_width=2, mode="constant"
        ),
        f"{use4template_dir}/{row.brainglobe_image_name}_asym-mask": np.pad(
            mask, pad_width=2, mode="constant"
        ),
        f"{use4template_dir}/{row.brainglobe_image_name}_right-hemi-brain": np.pad(
            image_n4[right_hemi_slices], pad_width=2, mode="constant"
        ),
        f"{use4template_dir}/{row.brainglobe_image_name}_right-hemi-mask": np.pad(
            mask[right_hemi_slices], pad_width=2, mode="constant"
        ),       
        f"{use4template_dir}/{row.brainglobe_image_name}_left-hemi-brain": np.pad(
            image_n4[left_hemi_slices], pad_width=2, mode="constant"
        ),
        f"{use4template_dir}/{row.brainglobe_image_name}_left-hemi-mask": np.pad(
            mask[left_hemi_slices], pad_width=2, mode="constant")
    }
    save_array_dict_to_nii(array_dict, use4template_dir, vox_sizes)
    use4template_dirs[row.brainglobe_image_name] = use4template_dir
    logger.info(
        f"Saved images for template construction in {use4template_dir}."
    )
    logger.info(f"Finished processing {row.brainglobe_image_name}.")



# %%
# Generate lists of file paths for template construction
# -----------------------------------------------------
# Use the paths to the use4template directories to generate lists of file paths
# for the template construction pipeline. Three kinds of template will be
# generated, and each needs the corresponding brain image and mask files


filepath_lists: dict[str, list] = {
    "asym-brain": [],
    "asym-mask": [],
    "sym-brain": [],
    "sym-mask": [],
}

for _, row in lowres_template_df.iterrows():
    brainglobe_image_name = row.brainglobe_image_name
    use4template_dir = use4template_dirs[brainglobe_image_name]

    # Add paths for the asymmetric brain template
    for label in ["brain", "mask"]:
        filepath_lists[f"asym-{label}"].append(
            use4template_dir / f"{brainglobe_image_name}_asym-{label}.nii.gz"
        )
        # Add paths for the symmetric brain template
        filepath_lists[f"sym-{label}"].append(
            use4template_dir / f"{brainglobe_image_name}-_left-hemi-{label}.nii.gz"
        )
        filepath_lists[f"sym-{label}"].append(
            use4template_dir / f"{brainglobe_image_name}-_right-hemi-{label}.nii.gz"
        )

# %%
# Save the file paths to text files, each in a separate directory

for key, paths in filepath_lists.items():
    kind, label = key.split("-")  # e.g. "asym" and "brain"
    n_images = len(paths)
    template_name = f"template_{kind}_{res_str}_n-{n_images}"
    template_dir = species_dir / "templates" / template_name
    template_dir.mkdir(exist_ok=True)
    np.savetxt(template_dir / f"{label}_paths.txt", paths, fmt="%s")