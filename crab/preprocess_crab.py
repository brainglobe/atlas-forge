
from brainglobe_template_builder.preproc.preprocess import preprocess
from brainglobe_template_builder.preproc.preproc_config import PreprocConfig, MaskConfig
from pathlib import Path

if __name__ == "__main__":
    output_dir = Path("/media/ceph/neuroinformatics/neuroinformatics/atlas-forge/Crab/")
    config = PreprocConfig(output_dir=output_dir, mask=MaskConfig()) # default mask, will use manual ones anyway
    preprocess(output_dir/"raw/raw_images.csv", config=config)