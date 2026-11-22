# Dino Snacks

A tiny PICO-8 D-pad game for a beginning player. Choose a stegosaur, T-rex, or
triceratops, then guide it around rocks and water to find three snacks. The five spaces
repeat forever. There are no hazards, timers, or scores. The dinosaurs use
your 24×24 pixel art from `dino-sprites-24.png`.

## Controls

- Menu: left/right chooses a dinosaur; X starts.
- Game: the D-pad moves one square at a time. Hold a direction to keep walking.
  O returns to the dinosaur menu.

The stegosaur and triceratops eat leaves. The T-rex eats steaks. The three food
outlines at the top fill as snacks are found. A small heart rises and bursts
into sparkles after each snack. After the third, the next space starts
automatically.

## Build

From the Gameboy folder:

```sh
python3 fantasy-console-games/DinoSnacks/build.py
```

This builds `ROMS/PICO-8/DinoSnacks.p8.png` and matching 384×384 box and 120×120
grid images under `boxart/PICO-8/`. Each artwork folder gets both
`DinoSnacks.p8.png` and `DinoSnacks.png` for MustardOS filename matching. The
builder needs only Python 3. The editable source is `DinoSnacks.p8`; edit its
sprites and sounds directly in PICO-8, then rebuild.

To launch the built cartridge in the PICO-8 app on this Mac:

```sh
open -a "$HOME/Downloads/pico-8/PICO-8.app" --args \
  -run "$PWD/ROMS/PICO-8/DinoSnacks.p8.png"
```

The source is marked as cartridge version 41 for broad PICO-8 compatibility.

## Tweak the sprites

Open the **source cartridge** in the PICO-8 editor:

```sh
open -a "$HOME/Downloads/pico-8/PICO-8.app" --args \
  "$PWD/fantasy-console-games/DinoSnacks/DinoSnacks.p8"
```

Choose the sprite editor tab. Each dinosaur pose is a 24×24 area covering nine
of PICO-8's 8×8 sprite slots. The numbers below identify the top-left slot of
each area; the first number is the resting pose and the second is its walking
pose. Left-facing sprites mirror the right-facing ones automatically.

| Dinosaur | Right | Front | Back |
| --- | --- | --- | --- |
| Stegosaur | 0, 3 | 6, 9 | 12, 48 |
| T-rex | 51, 54 | 57, 60 | 96, 99 |
| Triceratops | 102, 105 | 108, 144 | 147, 150 |

The leaf starts at slot 192, the steak at 194, and their progress outlines at
196 and 198. The rounded rock starts at 200, pointed rock at 202, and water pool
at 204. Each covers a 16×16 area. The heart at 206 is 8×8. Food appears at full
size in the playfield and smaller in the top progress bar.
Save changes with Ctrl-S, then run the builder again to refresh the playable
ROM and box art. Some sprite colors are remapped at runtime to make the new
dinosaurs and ground look softer, so a color may look different in the sprite
editor than it does in the game.

To import a revised version of your external PNG, run:

```sh
python3 fantasy-console-games/DinoSnacks/import_sprites.py
python3 fantasy-console-games/DinoSnacks/build.py
```

The importer reads the five-row, labeled `dino-sprites-24.png` sheet plus
`leaf.png` and `steak.png`. It copies their pixels and maps their colors to the
game palette. It uses the Pillow copy under `boxart/.deps`. Reimporting replaces
the dinosaur and food frames in `DinoSnacks.p8`, including edits made to those
frames in PICO-8; it keeps edits to the rocks, pool, and heart. The older
`dino-sprites.png` and `sprites.png` are not used.

## Tweak the sounds

The cartridge stores its sounds in the `__sfx__` section of `DinoSnacks.p8`,
not as WAV or MP3 files. PICO-8 has 64 SFX slots; each slot is a short sequence
of up to 32 notes with pitch, instrument, volume, and effect settings. The game
plays slot 0 for the heart pickup, slot 1 when entering a space, slot 2 when
returning to the menu, and slot 3 for the selection buzz.

In PICO-8's editor, click the SFX tab at the top right, select slot 0, and
press Space to hear it. Save with Ctrl-S and rebuild the ROM after making
changes. The rising heart pickup is an original PICO-8 chime.

## Artwork

The dinosaur and food sprites come from your PNGs. The rocks, pool, heart, and
sound effects were made for this cartridge. The cute, compact Game Boy style was
inspired by
[Dinosaur Sprites (GB Studio Compatible) by teaceratops](https://teaceratops.itch.io/dinosgbs).
The paid pack's files are not included or required.
