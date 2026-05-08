
from brainglobe_template_builder.preprocess import preprocess
from brainglobe_template_builder.utils.preproc_config import PreprocConfig, MaskConfig
from pathlib import Path

if __name__ == "__main__":
    output_dir = Path("/home/alessandro/crab_atlas_forge")
    config = PreprocConfig(output_dir=output_dir, mask=MaskConfig(gaussian_sigma=6, closing_size=10))  # couble defaults for double-resolution
    preprocess(output_dir/"standardised/standardised_images.csv", config=config)