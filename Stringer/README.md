# Stringer

A PICO-8 pattern game. Pick one of five difficulty tiers on the menu:

1. AB
2. AAB, ABB, or AABB
3. ABC
4. AABC, ABBC, or ABCC
5. ABCD

Each exercise chooses one pattern from the selected tier and shows two repeats
made from colored outline shapes:
circle, square, triangle pointing down, and triangle pointing up. A bead may
repeat within a pattern. Continue the winding string by
choosing six more beads for a two- or three-bead pattern, or eight more for a
four-bead pattern. The last row fits six beads. The 3, 4, or 5 choices include
every pattern bead and at least one extra bead. Choices and selector stay in
place throughout an exercise. Each correct bead reveals more of a coin;
completing one full pattern cycle drops that coin on the stack with a pling.
After the final coin, a short sparkle plays before the next exercise begins.
That takes three coins for a two-bead pattern and two coins for a three- or
four-bead pattern.
Wrong guesses can be retried without penalty.

The coin stack routine, coin sprite, and back/error sounds come from
[Rekenspelletje by Mathieu (mazieus)](https://www.lexaloffle.com/bbs/?pid=diwitorimu),
whose cartridge is marked CC BY-NC-SA. The selection buzz, correct-answer
tones, landing pling, and final sparkle are original. Keep that attribution
and license in mind when sharing Stringer.

## Controls

- Menu: left/right chooses a difficulty tier; X starts.
- String: left/right moves the V between bead choices; X selects; O returns to
  the menu.

## Build

From the Gameboy folder:

```sh
python3 fantasy-console-games/Stringer/build.py
```

This writes `ROMS/PICO-8/Stringer.p8.png` and matching box and grid artwork
under `boxart/PICO-8/`. The builder needs only Python 3 and packs the editable
`Stringer.p8` source. It does not execute the game; use PICO-8 or the handheld
runtime for a play test.

## TIC-80 sound

The converter has partial SFX support: it drops most of each note's pitch and
plays effects continuously. `Stringer.tic` in this folder instead plays the original
PICO-8 note sequences using short TIC-80 sounds. The pre-adjustment cartridge is
`Stringer-before-audio.tic` in this folder. After converting the PICO-8 cart
again, run `python3 fantasy-console-games/Stringer/repair_tic_audio.py` from the Gameboy
folder to rebuild the TIC-80 sounds. Following play tests, it shifts the
original note IDs up 24 semitones in TIC-80 and plays them at twice the
first repaired version's note length. The TIC-80 award animation and pause give
the longer correct answer, coin, and sparkle sounds room to finish.
The `Play Stringer.command` launcher uses the PICO-8 cartridge. To compare
the port, load `Stringer.tic` in TIC-80 separately.
