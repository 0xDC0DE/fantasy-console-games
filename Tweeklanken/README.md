# Tweeklanken

A PICO-8 picture and spelling game. It starts immediately. The child sees a
picture and a word with its two-letter sound missing, then chooses one of three
letter pairs. Left/right moves the small V; A or B checks. A wrong answer gets
a gentle retry. A correct answer fills the gap, sends a pink heart upward,
bursts into rainbow sparkles, and then sends three more sparkles jumping up one
after another. Each success adds a band to the rainbow counter on the right.
The number above the counter keeps the total score. A rainbow fills after 15
answers; the next one starts with shifted colors.

All game text uses a hand-drawn lowercase pixel font. The missing-letter word
and the answer pairs use 2× letters; the title and short hints use 1× letters.
The `j` in `ij` descends two pixels below the other letters' baseline.
The build script regenerates the gameplay thumbnail and catalogue artwork from
the same font and the current sprites.

The 15 pictures use the family's chosen words. The deck shuffles, uses each
picture once per cycle, and never repeats the same picture immediately between
cycles. No choice row contains **ij with ei** or **ou with au**, since those
pairs sound alike and would turn the puzzle into a spelling test.

## Words and sprite slots

Each sprite is **32×32 pixels** in the game. Edit the family's
`sprites-v2.png`: it is a **5×3 grid of 256×256 cells**, each drawn at 8× native
size. `make_sprites.py` reduces and packs those cells into the generated
**128×128** `sprites.png` cartridge sheet, four columns by four rows. Slots run
left to right, top to bottom; the final slot is spare. Keep the background
PICO-8 dark blue (`#1d2b53`).
The `neus` and `blauw` cells were adapted from the original `image.png`; that
reference file is kept unchanged.

Each pixel in a sprite has one of **16 color slots** (0–15). PICO-8 provides 16
default colors plus 16 extended colors (128–143) to choose from. The display
palette lets you assign any of those 32 colors to each slot, but the ordinary
screen still shows at most **16 colors at once**. Here slot 1 is the dark blue
background, leaving up to **15 colors for a pictured object**. The UI uses
slots 6, 7, 8, 10, 13, and 14, so changing those also changes UI colors.

To use an extended color, edit `PALETTE_IDS` in `make_sprites.py` and recolor
the matching pixels in `sprites-v2.png` to that color's RGB value. For example,
change slot 5 from `5` to `134` and replace its dark gray `#5f574f` pixels
with extended medium gray `#a28879`. Then run the importer and builder below.
The importer checks colors exactly and writes the needed display palette calls
into the cartridge. All pictures share the chosen 16-slot palette.

| Pair | Words in the game | Sprite slots |
| --- | --- | --- |
| eu | neus, deur | 0, 1 |
| au | pauw, auto, blauw | 2, 3, 4 |
| ei | kei, geit, trein | 5, 6, 7 |
| ou | touw, kous, koud | 8, 9, 10 |
| oe | boek, poes | 11, 12 |
| ij | bijl, ijs | 13, 14 |

## Edit and build

Paint over the pictures in `sprites-v2.png` without moving their cells. Keep
the pixels crisp at 8× scale. Then run:

```sh
python3 fantasy-console-games/Tweeklanken/make_sprites.py
python3 fantasy-console-games/Tweeklanken/build.py
```

This updates the editable `.p8` and builds
`ROMS/PICO-8/Tweeklanken.p8.png`. The sprite importer needs Pillow; the build
script uses the workspace's existing Pillow copy if it is not installed
globally. `sprites.png` is generated from your sheet on every import.

Double-click `fantasy-console-games/launchers/Play Tweeklanken.command` to
play the built cartridge on this Mac.
