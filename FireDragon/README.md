# Dragon Fury: automatic tour

Open `dragon_fury.tic` in TIC-80. Press Z or X to begin. Hold Z to breathe fire;
tap X to shoot fireballs. The dragon flies and aims automatically, and each pass
leads to a new landscape. Enemy attacks remain visual only.

The arrow keys are optional. Hold left to slow down or right to speed up. Hold
up to fly higher or down to fly lower. Releasing the arrows returns the dragon
to its usual speed and terrain-following height.

`dragon_fury.lua` is the editable game code. Run `python3 build.py` in this folder
to rebuild the cartridge. The build uses `dragon_fury-original.tic` for the
original graphics, audio, and metadata; keep that file alongside the source.
