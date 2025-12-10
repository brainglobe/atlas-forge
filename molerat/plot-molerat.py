from brainglobe_template_builder.plots import plot_orthographic, _auto_adjust_contrast, _save_and_close_figure
from brainglobe_atlasapi import BrainGlobeAtlas
from brainglobe_utils.IO.image import load_any
from brainglobe_space import AnatomicalSpace
from pathlib import Path
import numpy as np

if __name__ == "__main__":
    template_image = BrainGlobeAtlas("african_molerat_20um").reference
    individual_image = load_any(Path.home()/"molerat/sub-d09_hemi-R_res-20um_orig-asr.nii.gz")
    
    range_1_99 = _auto_adjust_contrast(individual_image)
    vmin = range_1_99["vmin"]
    vmax = range_1_99["vmax"]
    print(vmin)
    print(vmax)
    
    #rescale template to range of individual
    template_image = template_image.astype(np.float64)
    template_image = ((template_image-np.min(template_image))/np.max(template_image)*(vmax-vmin))+vmin
    target_size = tuple([max(template_image.shape[i], individual_image.shape[i]) for i in range(3)])

    space = AnatomicalSpace("ASR", shape=template_image.shape)
    print(template_image.shape)
    show_slices = (350, 200, 300)
    slice_shift_due_to_padding = [(np.max(template_image.shape)-template_image.shape[i])//2 for i in range(3)]
    print(slice_shift_due_to_padding)
    
    figure, axes = plot_orthographic(
        template_image,
        show_slices=show_slices,
        vmin=1000,
        vmax=50000
    )
    for i in range(3):
        ax = axes[i]
        h, v = space.index_pairs[i]
        print(h,v)
        ax.axhline(show_slices[h]+slice_shift_due_to_padding[h], color="r", linestyle="--", alpha=0.5)
        ax.axvline(show_slices[v]+slice_shift_due_to_padding[v], color="r", linestyle="--", alpha=0.5)
    
    _save_and_close_figure(
        figure,
        Path.home()/"molerat/",
        "template"
    )
    
    figure, axes = plot_orthographic(
        individual_image, 
        show_slices=show_slices,
        vmin=1000,
        vmax=50000
    )
    for i in range(3):
        ax = axes[i]
        h, v = space.index_pairs[i]
        ax.axhline(show_slices[h]+slice_shift_due_to_padding[h], color="r", linestyle="--", alpha=0.5)
        ax.axvline(show_slices[v]+slice_shift_due_to_padding[v], color="r", linestyle="--", alpha=0.5)
    
    _save_and_close_figure(
        figure,
        Path.home()/"molerat/",
        "sub-d09_hemi-R"
    )
    
