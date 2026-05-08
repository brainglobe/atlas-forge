
from brainglobe_template_builder.preprocess import preprocess
from brainglobe_template_builder.utils.preproc_config import PreprocConfig, MaskConfig
from pathlib import Path

if __name__ == "__main__":
    output_dir = Path("/media/ceph/neuroinformatics/neuroinformatics/atlas-forge/ZebraFinch/")
    # default mask config works great for all samples except 8755 and 8686
    config = PreprocConfig(output_dir=output_dir, mask=MaskConfig(), pad_pixels=30)
    preprocess(output_dir/"standardised/standardised_images.csv", config=config)