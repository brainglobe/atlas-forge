from pathlib import Path
import nd2
from brainglobe_template_builder.utils.transform_utils import downsample_anisotropic_stack_to_isotropic
from brainglobe_utils.IO.image.save import save_any
import dask.array as da
import os
    
input_dir = Path("/media/ceph/microscopy/collaborative_projects/crab_atlas")
output_dir = Path("/media/ceph/zoo/raw/CrabLab/Anatomy/crab_atlas/downsampled/")
target_resolution_um = 3
    
for subfolder in input_dir.iterdir():
    print(f"Started {subfolder.name}")
    if not subfolder.is_dir():
        continue
    
    assert subfolder.name.startswith("Atl"), f"Subfolder name must start with 'Atl': {subfolder.name}"
    
    nd2_file = subfolder / f"{subfolder.name}-Stitched.nd2"

    if nd2_file.exists():
        data = nd2.imread(str(nd2_file))
        print(data.shape)
        for channel_index, channel_name in enumerate(["autofluorescence", "cytox", "WGA"]):
            channel_data = data[:, channel_index, :, :] 
            print(channel_data.shape)
            channel_data = da.from_array(channel_data, chunks={0: 1, 1: channel_data.shape[1], 2: channel_data.shape[2]})
            channel_data = downsample_anisotropic_stack_to_isotropic(channel_data,(3, 0.86, 0.86), target_resolution_um)
            save_any(channel_data, Path.home()/"crab_test"/f"{subfolder.name}_{target_resolution_um}um_{channel_name}.tif")
            Path.mkdir(output_dir/f"{subfolder.name}/{target_resolution_um}um/", exist_ok=True, parents=True)
            save_any(channel_data, output_dir/f"{subfolder.name}/{target_resolution_um}um/{subfolder.name}_{target_resolution_um}um_{channel_name}.tif")
            print(f"Saved {channel_name}")
        print(f"Finished {subfolder.name}")
    else:
        print(f"Skipping {nd2_file} because it does not exist")