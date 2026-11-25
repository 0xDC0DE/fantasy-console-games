# ColorMix

A PICO-8 color mixing game for a young player. Two circles at the top show the
colors to combine. Three circles at the bottom offer possible results. Move the
small V with left/right and press A to choose. The game uses the three primary
color combinations: yellow + blue = green, yellow + red = orange, and red +
blue = purple. The top color order and answer positions change between puzzles.

ColorMix follows MathSplit's visual layout and ShapeSum's score flow. Each
correct answer earns one coin; wrong answers can be retried without penalty.
Starting a new game resets the coins. The coin stack routine, coin sprite, and
other sound effects come from [Rekenspelletje by Mathieu (mazieus)](https://www.lexaloffle.com/bbs/?pid=diwitorimu),
whose cartridge is marked CC BY-NC-SA. The selection buzz is original. Keep
that attribution and license in mind when sharing ColorMix.

## Controls

- Menu: A starts a new game.
- Puzzle: left/right moves the V between the three color choices; A checks;
  B returns to the menu.
- Correct answer: A advances to another puzzle.

## Build

From the Gameboy folder:

```sh
python3 fantasy-console-games/ColorMix/build.py
```

This writes `ROMS/PICO-8/ColorMix.p8.png` plus matching 384×384 box and
120×120 grid images under `boxart/PICO-8/`. Each artwork folder gets both
`ColorMix.p8.png` and `ColorMix.png` for MustardOS filename matching. The
builder needs only Python 3 and packs the editable `ColorMix.p8` source into
a PICO-8 cartridge image.

Use PICO-8 or the handheld's PICO-8 runtime to play-test after changing the
source; the Python builder packages the code but does not execute it.

## Test on this Mac

Run this from the Gameboy folder to launch the built cartridge in the PICO-8
app currently in Downloads:

```sh
open -a "$HOME/Downloads/pico-8/PICO-8.app" --args \
  -run "$PWD/ROMS/PICO-8/ColorMix.p8.png"
```

To test source edits before rebuilding, change the path after `-run` to
`$PWD/fantasy-console-games/ColorMix/ColorMix.p8`. The source is marked as cartridge
version 41 for broad PICO-8 compatibility.

## TIC-80 port

After converting `ColorMix.p8` to `ColorMix.tic`, run
`python3 fantasy-console-games/repair_tic80_audio.py ColorMix` from the Gameboy folder.
This repairs the converted sound effects in this source folder. The
`Play ColorMix.command` launcher uses PICO-8; load `ColorMix.tic` in TIC-80
separately to compare the port.
