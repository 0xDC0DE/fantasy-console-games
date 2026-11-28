# Tweeklanken

A PICO-8 reading game with two modes. The menu starts on **plaatjes**, the
original picture game. **Woorden** hides the picture and uses the word itself
as the clue. The first eight exercises use three-letter words and two answer
pairs. Starting with exercise nine, it draws from all word lengths, including
the three-letter words, and shows three pairs. Its patterns come from
`tweeklank-woordenlijst.md`, with
the eight pairs `au`, `eu`, `ou`, `oe`, `ei`, `ij`, `ui`, and `ie`. When several
familiar words fit one pattern, every displayed valid completion is accepted.
Difficulty words and verb forms are kept out of the choices. If a word appears
in both columns, the difficulty column takes precedence.
When a listed word uses `ei`/`ij` or `au`/`ou`, its other spelling is also
blocked unless that spelling makes a valid word in the same puzzle.
The `__t` puzzle has only two safe answer pairs, so it appears only during
the first eight exercises.

Left/right moves the small V. A checks an answer; B returns to the mode menu.
A wrong answer gets a gentle retry. A correct answer fills the gap, sends a
pink heart upward, bursts into rainbow sparkles, and then sends three more
sparkles jumping up one after another. In word mode, the pair glows in changing
colors and a rainbow underline grows beneath the word. Each success adds a
band to the rainbow counter: the right side fills after 15 answers, then the
left side fills over the next 15. Both reset on answer 31. The number above
the right rainbow keeps the total score.

All game text uses a hand-drawn lowercase pixel font. The missing-letter word
and the answer pairs use 2× letters; the title and short hints use 1× letters.
The lowercase `g`, `j`, and `p` descend two pixels below the baseline.
The build script regenerates the gameplay thumbnail and catalogue artwork from
the same font and the current sprites.

The picture mode uses the family's 15 chosen words. Each mode shuffles its own
bank, uses every picture or pattern once per cycle, and avoids an immediate
repeat between cycles. No choice row contains **ij with ei** or **ou with au**,
since those pairs sound alike and would turn the puzzle into a spelling test.
For word mode, the builder validates the Markdown list and regenerates
`word_words` in `Tweeklanken.p8`.

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
