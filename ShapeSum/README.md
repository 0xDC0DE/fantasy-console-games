# Shape Sum

A PICO-8 game about recognizing shapes, counting repeated pieces, and adding
their values. The cartridge is independent of the inspiration game. Counted
shapes never overlap. Each shape type gets a distinct muted outline color per
puzzle, and the same sculpture is never shown twice in a row.

The coin stack routine, coin sprite, and other sound effects come from [Rekenspelletje by Mathieu
(mazieus)](https://www.lexaloffle.com/bbs/?pid=diwitorimu), whose cartridge
is marked CC BY-NC-SA. The selection buzz is original. Keep that attribution
and license in mind when sharing Shape Sum.

## Build

From the Gameboy folder:

```sh
python3 fantasy-console-games/ShapeSum/build.py
```

This writes `ROMS/PICO-8/ShapeSum.p8.png` plus matching 384×384 box and
120×120 grid images under `boxart/PICO-8/`. Each artwork folder gets both
`ShapeSum.p8.png` and `ShapeSum.png` for MustardOS filename matching. The
builder needs only Python 3 and packs the editable `ShapeSum.p8` source into a
PICO-8 cartridge image. PICO-8 itself can also export the source:

```sh
pico8 fantasy-console-games/ShapeSum/ShapeSum.p8 -export ROMS/PICO-8/ShapeSum.p8.png
```

Use PICO-8 or the handheld's PICO-8 runtime to play-test after changing the
source; the Python builder packages the code but does not execute it.

## Test on this Mac

Run this from the Gameboy folder to launch the built cartridge in the PICO-8
app currently in Downloads:

```sh
open -a "$HOME/Downloads/pico-8/PICO-8.app" --args \
  -run "$PWD/ROMS/PICO-8/ShapeSum.p8.png"
```

To test source edits before rebuilding, change the path after `-run` to
`$PWD/fantasy-console-games/ShapeSum/ShapeSum.p8`. The source is marked as cartridge version
41 for broad PICO-8 compatibility.

## Add a sculpture

Edit the `templates` table near the top of `ShapeSum.p8`. Each entry has a
unique `name` and a `parts` list. A part is `{shape, x, y, size}`; a fifth
`true` turns a rectangle upright or flips the wide triangle downward. Shape
IDs, including the right triangle used by the slide, are listed immediately
above the table. Coordinates use PICO-8's 128×128 screen; keep parts within
roughly x=32–124 and y=35–94, and leave space between their outlines.

The existing snowman shows the format:

```lua
{name="snowman",parts={
 {2,64,43,10},{1,64,56,13},{1,64,74,19}}},
```

Use at most three distinct shape IDs because the top row shows three clues.
After adding an entry, put its one-based position in the appropriate row(s) of
`pools`, which correspond to maximum answers 9, 12, 15, 20, and 30. The
generator automatically assigns values, checks the answer cap, and avoids
showing the same template twice in succession. If your drawing needs thin
connector lines, add a case for its name in `draw_links()`; those lines are
drawn behind the counted shapes.

## Controls

- Menu: left/right chooses maximum answer (9, 12, 15, 20, 30); X starts.
- Puzzle: up/down changes the answer from 0 to the selected maximum; X checks,
  and O returns to the menu.
- Correct answer: X advances and earns one coin. Wrong answers can be retried
  without penalty.

## TIC-80 port

After converting `ShapeSum.p8` to `ShapeSum.tic`, run
`python3 fantasy-console-games/repair_tic80_audio.py ShapeSum` from the Gameboy folder.
This repairs the converted sound effects, adds the PICO-8 `deli` helper needed
for puzzle creation in the cartridge in this source folder. The
`Play ShapeSum.command` launcher uses PICO-8; load `ShapeSum.tic` in TIC-80
separately to compare the port.
