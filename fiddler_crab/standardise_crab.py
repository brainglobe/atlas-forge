from brainglobe_template_builder.standardise import standardise

from pathlib import Path
if __name__ == "__main__":
    source_csv = Path("/home/alessandro/crab_test/3um/template-building-crab-3um-april-2026.csv")
    output_dir = Path("/home/alessandro/crab_atlas_forge")
    output_vox_size = None # already at 3 micron, no downsampling needed
    standardise(source_csv=source_csv, output_dir=output_dir, output_vox_size=output_vox_size)
 