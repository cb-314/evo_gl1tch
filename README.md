# evo_gl1tch

evolutionary glitch art creation via databending. you can do most stuff with
the sliders and buttons, the default values are sensible.  clicking on the
images will do several things:

* for evolution it selects the ones to be crossed and mutated, all others are
* for evolution it also selects the elite ones, which are kept
* for saving only the selected ones will be saved

## notes

works well only on jpeg files because other image formats are a lot less error
resistant

using the --autogen option, image selection is automated using various
criteria, making the image generation almost automated. an elitist approach is
used and the elite population is saved to jpegs every generation.

## requirements

* PIL + Tk interface
* TkInter
