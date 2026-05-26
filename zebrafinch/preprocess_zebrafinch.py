
from brainglobe_template_builder.preprocess import preprocess
from brainglobe_template_builder.utils.preproc_config import PreprocConfig, MaskConfig
from pathlib import Path

if __name__ == "__main__":
    output_dir = Path("/media/ceph/neuroinformatics/neuroinformatics/atlas-forge/ZebraFinch/")
    # used a mask first, then normalise version of preprocess
    # then, default mask config works great for all samples except 8686, 8838 and maybe 8786, 8843
    # because it gave fewer over-generous masks (otherwise also 0065 and 8913 over-generous)
    # excluded 8761m as worst male image, to create balanced sex template (ten each)
    # initial template will be a manually aligned 8222f sample, with 60 extra pixels padding on top of the default 30.
    config = PreprocConfig(output_dir=output_dir, mask=MaskConfig(), pad_pixels=30)
    preprocess(output_dir/"standardised/standardised_images.csv", config=config)