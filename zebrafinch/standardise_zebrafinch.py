from brainglobe_template_builder.standardise import standardise

from pathlib import Path
if __name__ == "__main__":
    source_csv = Path("/media/ceph/margrie/sweiler/RawData/Tracing_Imaging/serial2p/Bird_brains/zebra_finch_atlas/2026-05-26_zebrafinch.csv")
    output_dir = Path("/media/ceph/neuroinformatics/neuroinformatics/atlas-forge/ZebraFinch/")
    output_vox_size = 25
    standardise(source_csv=source_csv, output_dir=output_dir, output_vox_size=output_vox_size)
