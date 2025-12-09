from brainglobe_template_builder.preproc.source_to_raw import source_to_raw

from pathlib import Path
if __name__ == "__main__":
    source_csv = Path("/media/ceph/zoo/raw/CrabLab/Anatomy/crab_atlas/atlas-generation-Afruca-tangeri-metadata-AF.csv")
    output_dir = Path("/media/ceph/neuroinformatics/neuroinformatics/atlas-forge/Crab/")
    output_vox_size = None # already at 6 micron, no downsampling needed
    source_to_raw(source_csv=source_csv, output_dir=output_dir, output_vox_size=output_vox_size)
 