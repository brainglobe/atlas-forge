
from brainglobe_template_builder.preproc.preprocess import preprocess
from brainglobe_template_builder.preproc.preproc_config import PreprocConfig, MaskConfig
from pathlib import Path
import yaml

if __name__ == "__main__":
    output_dir = Path("/media/ceph/neuroinformatics/neuroinformatics/atlas-forge/Crab/")
    config = PreprocConfig(output_dir=output_dir, mask=MaskConfig()) # default mask, will use manual ones anyway
    config_path = output_dir / "preproc_config.yaml"
    with open(config_path, "w") as outfile:
        yaml.dump(config.model_dump(mode="json"), outfile, default_flow_style=False)

    preprocess(output_dir/"raw/raw_images.csv", config_file=config_path)