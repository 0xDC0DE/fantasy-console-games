# Frog Hopper

Help the green frog cross the pond in one of three learning modes. Move the V
above a pebble and press X. Correct answers animate a hop with a boing sound;
wrong answers play either a hurt "oww" or a surprised eye scan with little
cricket chirps, then can be retried. Reaching the final pebble starts a
celebration with both frogs and both fish, confetti, and sprite pictures in the
guide's bubble before sliding in another row. The pebbles stay still during play;
only the water ripples and leaf drift.
The fish surface in the water below the final pebble, bob in place, and pan with it
during the row transition.

From the third wrong guess on the same prompt, a green or gold fish briefly pops
up beside the correct rock with a two-note alert after each miss. The guess
count resets after a correct hop.

## Game modes

| Mode | Task | Pebble labels |
| --- | --- | --- |
| Count Hops | Follow the drawn arrow and count that many rocks from the frog. | Hidden. |
| Sums | Add the purple frog's positive number to the number under the green frog. | Shuffled numbers; the answer may be left or right. |
| Plus & Minus | Add or subtract the signed number in the bubble. | Shuffled numbers; each row includes both signs. |

The menu shows both settings. Use up/down to select mode or difficulty,
left/right to change it, and X to start. In the numbered modes, each row has a
prepared path ending at its final rock, with other numbers as distractors.
Some correct hops go left. Labels stay fixed until the row pans.

## Difficulty

| Level | Pebbles | Numbered starting value | Largest step |
| --- | ---: | --- | ---: |
| Easy | 6 | 0 (the row is 0–5) | 3 |
| Medium | 7 | 1–3 | 4 |
| Hard | 9 | A random start from 5–7, 10–12, or 15–17 | 5 |

The selector can reach every pebble, including the frog's current one. Count
Hops gives one or two backward prompts before the frog reaches the end. In the
numbered modes, each new row starts fresh at the selected difficulty. The frog
faces left on backward jumps and turns forward after landing. There is no score
or time limit.

## Controls

- Menu: up/down selects mode or difficulty; left/right changes the selected
  setting; X starts the game.
- Pond: left/right moves the V; X confirms the pebble; O returns to the menu
  (Z on TIC-80's default keyboard).

## Build and art

Run `python3 fantasy-console-games/FrogHopper/build.py` from the Gameboy folder
to rebuild `FrogHopper.tic` and `art.png`. The editable game code is
`FrogHopper.lua`. The build takes seventeen selected frames from the supplied
green and purple frog sheets, including three-quarter resting poses. Speaking
poses use those same resting frames with a small square mouth. It also packs
smaller frog, heart, crown, and smiley sprites
for the celebration bubble into the TIC-80 sprite bank. The
pebbles and scenery are original drawings made for this game; the supplied
watermarked pebble image served only as a visual reference and is not in the
cartridge.

The two supplied fish sheets contribute two poses each. TIC-80 has a fixed
sprite bank; all four fish poses fit alongside the frog and bubble sprites.

The frog spritesheets were supplied by the user as free-to-use artwork. Their
original artist and license were not included with the files; retain the
original sheets and add that credit here if it becomes available.

The website player includes the TIC-80 JavaScript and WebAssembly runtime
already used by Dragon Fury. `update_game.py FrogHopper` refreshes its
`cart.tic`, downloads, launcher, and artwork after rebuilding the source.
