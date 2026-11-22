# MissingNumber

A PICO-8 game about completing addition and subtraction sums. Choose a maximum
number of 10, 15, or 20. The unicorn shows the target result; change the missing
number in the sum below it. Three different sums share that result, and each
round includes both addition and subtraction. All shown numbers and answers
are between zero and the chosen maximum. Wrong answers can be retried.

Each correct sum creates a full heart. It travels to the top of the rainbow
tower, pops into sparkles, and adds one band. The target and unicorn stay the
same for three sums, then change automatically. The single tower holds 55
bands, reaching just below the header. Its colors go up and back down the
rainbow; after it fills, the next heart starts a new tower with a shifted color
order. A small heart counter keeps the total score visible.

## Controls

- Menu: left/right chooses the maximum number; X starts a new game.
- Sum: up/down changes the missing number; X checks; O returns to the menu.

## Unicorn artwork

The five unicorns in `unicorn_sprites_v3/` are imported as 40×64 sprites.
Gameplay shows each unicorn at full size, with the target number beside it and
the sum lower on the screen. The menu shows the first sprite at full size. A new unicorn
appears after each heart, without an immediate repeat. The five individual
PNGs are the editable sources; the 200×64 sheet is a matching preview. Opaque
black outline pixels become dark blue so they stay visible against the game's
black background.

After changing the PNGs, reimport them before rebuilding:

```sh
python3 homemade/MissingNumber/import_unicorns.py
python3 homemade/MissingNumber/build.py
```

## Build

Double-click `homemade/launchers/Play MissingNumber.command` to play the editable PICO-8
cartridge on this Mac.

From the Gameboy folder:

```sh
python3 homemade/MissingNumber/build.py
```

This builds `ROMS/PICO-8/MissingNumber.p8.png` and matching box and grid
artwork. The builder uses only Python 3 and packs the editable `.p8` source;
it does not execute the game. Play-test in PICO-8 with:

```sh
open -a "$HOME/Downloads/pico-8/PICO-8.app" --args \
  -run "$PWD/homemade/MissingNumber/MissingNumber.p8"
```

The heart sprite and burst style come from the original DinoSnacks cartridge.
Some sound effects are reused from Stringer. Stringer's back and error sounds
originate in [Rekenspelletje by Mathieu (mazieus)](https://www.lexaloffle.com/bbs/?pid=diwitorimu),
which is marked CC BY-NC-SA; keep that attribution and license in mind when
sharing this game.
