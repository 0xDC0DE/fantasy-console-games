# CountNumbers

Read a large number, then press up to add one object or down to remove one.
Objects fill a two-row counting pattern: top, bottom, then the next column.
Press X when the count matches the number. A correct count animates the objects
and starts another exercise automatically. A wrong count can be retried. After
four incorrect checks in one exercise, outlines mark the positions to fill;
the hint stays visible until the exercise is solved.

The menu offers maximum numbers of 5 and 9. The 5 setting uses larger objects
in three columns; the 9 setting uses smaller objects in five columns. Each
exercise uses one of six pixel-art objects: stars, hearts, bones, mushrooms,
smileys, or music notes. The number typeface uses larger 7×9 source glyphs.
The burst, float, melt, and shrink celebrations each have their own sound.

## Controls

- Menu: right/up chooses 9, left/down chooses 5; X starts a new game.
- Exercise: up/right adds an object, down/left removes one; X checks; O returns
  to the menu.

## Build

From the Gameboy folder:

```sh
python3 fantasy-console-games/CountNumbers/build.py
python3 fantasy-console-games/CountNumbers/build_tic.py
```

The first command builds `ROMS/PICO-8/CountNumbers.p8.png` and matching 384×384
box and 120×120 grid artwork in `boxart/PICO-8/`. The second builds
`fantasy-console-games/CountNumbers/CountNumbers.tic` using the existing MathSplit TIC-80
compatibility layer. Both use the editable `CountNumbers.p8` source and sounds.
The builders package the game but do not play-test it.

To play the PICO-8 source on this Mac:

```sh
open -a "$HOME/Downloads/pico-8/PICO-8.app" --args \
  -run "$PWD/fantasy-console-games/CountNumbers/CountNumbers.p8"
```

Double-click `fantasy-console-games/launchers/Play CountNumbers.command` to play the built
PICO-8 cartridge. The PICO-8 source uses cartridge version 41 for compatibility.

The sound effects are adapted from MathSplit, which uses sounds from
[Rekenspelletje by Mathieu (mazieus)](https://www.lexaloffle.com/bbs/?pid=diwitorimu),
marked CC BY-NC-SA. Keep that attribution and license in mind when sharing
CountNumbers.
