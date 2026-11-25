# Turtles and Hare

A complete PICO-8 puzzle game with 48 layouts transcribed from the photographed
book. The four difficulty choices start at Easy 1, Medium 13, Hard 25, and
Expert 37. Finishing a level advances through the remaining puzzles and then
into the next difficulty. The last puzzle ends with a celebration and returns
to the menu. Completing a puzzle makes the arena's border cycle through the
six animal colors; the same moving rainbow surrounds the final Game Over scene.
The level card stays up briefly between puzzles; X or Z skips it.

Use the arrow keys or D-pad to move the cursor. On the menu, move it to a
difficulty or Tutorial and press X (the handheld's A button) to choose. During
a puzzle, X selects or releases an animal. With one selected, the arrows move it
one space at a time. The orange hare can jump over an adjacent turtle when its
landing space is free; fences block both steps of a jump. Each animal wins by
reaching its matching colored edge. During a puzzle, Z (handheld B) opens a
Quit confirmation with No selected. Press Z again to continue, or press Down
then X to return to the menu. Hold X and press Z to reset the current puzzle.
On the menu, Z is a shortcut to the animated tutorial.

Run `python3 build.py` here to regenerate `TurtlesAndHare.p8` and the PICO-8
cartridge at `../../ROMS/PICO-8/TurtlesAndHare.p8.png`. Run
`python3 validate_levels.py` to verify that all 48 boards are solvable and
that each shortest solution matches the move count printed in the book.

The game is split into editable `game.lua`, `levels.json`, and `animals.png`.
The build packs these with five sound effects into the cartridge. `art.png`
is a screenshot used for the game library and website.

## Board art and sprite sheet

`concept-128.png` and `concept-black-128.png` are pixel-accurate 128×128 PICO-8
screen concepts with light-green and black terrain. Their `-4x.png` copies use
nearest-neighbor scaling for inspection. `concept-cursor-128.png` and its 4×
copy show the selected animal. Run `python3 concept.py` to regenerate the board
previews from the editable animal sheet.

## Edit the animals

Open **`animals.png`** in a pixel-art editor. It is a 192×32 transparent PNG:
six 32×32 slots ordered green, blue, red, yellow, purple, bunny. Zoom in, use
a one-pixel pencil or eraser, and keep the image dimensions unchanged. Save as
PNG, then run `python3 concept.py` in this folder to refresh the previews.
Use the color picker to reuse existing colors so the board stays within its
16-color palette. The preview script reads `animals.png` and does not overwrite
it.

`extract_reference.py` is the one-time importer from the large `image.png`
reference. Running it refreshes `reference-sprites.png`, not `animals.png`.
This preserves any manual edits in the editable sheet. One example: the extra
green front-leg pixel at sheet coordinate (11, 22) has been erased there.

The reference photo shows a **3×3 board (nine spaces)**. A four-pixel food edge
leaves 120×120 pixels inside, or 40×40 per space. The green terrain uses PICO-8
extended color 138 (lime). Solid sections of the four-pixel rim mark the six
food colors: green, orange, purple, red, blue, and yellow. Rim sections without
food stay dark blue. The purple and red food edges use the lightest shades
from their matching turtles.

The five turtles and orange hare were downsized directly from `image.png` by
`extract_reference.py` before copying to `animals.png`. The original turtle eyes measure about 28 source pixels
across, against about 317 pixels for a complete turtle. At 30 pixels wide, the
eyes become roughly 3×3 pixels. Each turtle is 30×25 pixels within a 32×32
sprite slot; the bunny is 21×30 pixels. The source art's fourth shell shade is
merged into the shell's main shade, leaving three body shades per animal plus
the shared dark eye color. Each turtle has a straight three-pixel-high lower
shell band in its brightest shade and a four-pixel-wide middle leg. The
complete board uses 16 colors.

The animals' positions demonstrate the look of a puzzle; they do not encode a
starting position from the photo. Every fence is six pixels thick, 36 pixels
long, symmetrical in both directions, and solid dark blue. The turtles leave
two pixels of visual clearance beside a fence.

The selection cursor is a 32×32 square of four dark-blue corners. Each corner
has two-pixel-thick, five-pixel-long arms; the rest of the edge is open. It sits
four pixels inside the 40×40 board space, leaving green visible around it.
