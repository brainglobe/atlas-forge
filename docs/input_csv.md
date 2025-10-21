# Input CSV
To build a template, provide a CSV with information about the images you'd like to use. Each line in the CSV represents a stack of images.

### Required Columns
- `subject_id`: Unique identifier for the subject. Do not use spaces, hyphens (`-`) or underscores (`_`).
- `source_filepath`: Full path to the source image stack
- `resolution_z`: Voxel resolution in the Z axis (in μm)
- `resolution_y`: Voxel resolution in the Y axis (in μm)
- `resolution_x`: Voxel resolution in the X axis (in μm)
- `origin`: Three letters describing the anatomical orientation of the image (e.g., `PSL`, `LSP`, `RAS`)

### Optional Columns
- `species`: Species name
- `sex`: Biological sex of the subject (`M`, `F`)
- `age`: Age of the subject (e.g., `12 weeks`, `P30`)
- `channel`: Imaging channel (e.g., `green`)
- `use`: whether to include the image in the template building process (`true` or `false`)

> ℹ️ Additional columns can be included as needed.

### Example

```csv
species,sex,subject_id,resolution_z,resolution_y,resolution_x,origin,channel,source_filepath
Zebra finch,F,ZF1,25,25,25,PSL,green,/ceph/atlas-forge/zebrafinch/sourcedata/ZF1_25_25_ch03_green.tif
Zebra finch,M,ZF2,25,25,25,PSL,green,/ceph/atlas-forge/zebrafinch/sourcedata/ZF2_25_25_ch03_green.tif
Zebra finch,F,ZF3,25,25,25,PSL,green,/ceph/atlas-forge/zebrafinch/sourcedata/ZF3_25_25_ch03_chan_3_green.tif
Zebra finch,M,ZF4,25,25,25,PSL,green,/ceph/atlas-forge/zebrafinch/sourcedata/ZF4_25_25_ch03_chan_3_green.tif
```