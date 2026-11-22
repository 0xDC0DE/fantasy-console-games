# MathSplit

A PICO-8 subtraction game inspired by number-split homework. Each puzzle shows
one number at the top of a two-branch tree and a given number on the left. Fill
in the missing right number so the two bottom numbers add up to the top. The
menu offers maximum top numbers of 7 and 10. Zero is included, so a puzzle
such as 5 split into 5 and 0 can appear.

The game uses ShapeSum's visual style and score flow. Each correct answer earns
one coin. Wrong answers can be retried without penalty. Starting a new game
resets the coins. The coin stack routine, coin sprite, and other sound effects come
from [Rekenspelletje by Mathieu (mazieus)](https://www.lexaloffle.com/bbs/?pid=diwitorimu),
whose cartridge is marked CC BY-NC-SA. The selection buzz is original. Keep
that attribution and license in mind when sharing MathSplit.

## Controls

- Menu: left/right chooses the maximum number (7 or 10); X starts.
- Puzzle: up/down changes the answer from 0 to the selected maximum; X checks,
  and O returns to the menu.
- Correct answer: X advances to a new puzzle. The right branch remains filled
  while the result is shown.

## Build

From the Gameboy folder:

```sh
python3 fantasy-console-games/MathSplit/build.py
```

This writes `ROMS/PICO-8/MathSplit.p8.png` plus matching 384×384 box and
120×120 grid images under `boxart/PICO-8/`. Each artwork folder gets both
`MathSplit.p8.png` and `MathSplit.png` for MustardOS filename matching. The
builder needs only Python 3 and packs the editable `MathSplit.p8` source into
a PICO-8 cartridge image. PICO-8 itself can also export the source:

```sh
pico8 fantasy-console-games/MathSplit/MathSplit.p8 -export ROMS/PICO-8/MathSplit.p8.png
```

Use PICO-8 or the handheld's PICO-8 runtime to play-test after changing the
source; the Python builder packages the code but does not execute it.

## Test on this Mac

Run this from the Gameboy folder to launch the built cartridge in the PICO-8
app currently in Downloads:

```sh
open -a "$HOME/Downloads/pico-8/PICO-8.app" --args \
  -run "$PWD/ROMS/PICO-8/MathSplit.p8.png"
```

To test source edits before rebuilding, change the path after `-run` to
`$PWD/fantasy-console-games/MathSplit/MathSplit.p8`. The source is marked as cartridge
version 41 for broad PICO-8 compatibility.

## TIC-80 port

After converting `MathSplit.p8` to `MathSplit.tic`, run
`python3 fantasy-console-games/repair_tic80_audio.py MathSplit` from the Gameboy folder.
This repairs the converted sound effects in this source folder. The
`Play MathSplit.command` launcher uses PICO-8; load `MathSplit.tic` in TIC-80
separately to compare the port.
