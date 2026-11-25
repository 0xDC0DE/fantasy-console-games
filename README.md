# Fantasy console games

Ten homemade games for children, including eight learning games and two playful
adventures. The [website](website/README.md) lets friends and teachers play them
in a browser. This repository also keeps the editable cartridges, build scripts,
artwork sources, and per-game notes.

From the Gameboy folder, run `python3 fantasy-console-games/update_game.py --all`
to rebuild cartridges, launchers, website players, downloads, and artwork.
Each game folder has an `art.png` source. See the [Gameboy workspace README](../README.md)
for the update and backup workflow.

| Learning games | Just for fun |
| --- | --- |
| Color Mix, Count Numbers, Frog Hopper, Heart Path, Math Split, Missing Number, Shape Sum, Stringer | Dino Snacks, Dragon Fury |

The PICO-8 games have editable `.p8` cartridges. Dragon Fury uses TIC-80 and has
an editable `.lua` source plus `.tic` cartridge. The `.tic` files in the other
folders are PICO-8 ports. Open each game's README for its controls, build notes,
and credits.

## Share and deploy the website

From the `website` folder:

```sh
cp .env.example .env
# Edit DOMAINNAME in .env, then build and start:
docker compose up -d --build
```

The Compose file uses the existing external `traefik2_proxy` network and serves
at `games.$DOMAINNAME` through the `https` Traefik entrypoint. Set a DNS record
for that host and ensure the network exists. The site is static, so no database
or bind-mounted files are required. See [website/README.md](website/README.md)
for local preview and image deployment instructions.

## Sharing and credits

Several learning games adapt sound effects or coin art from
[Rekenspelletje by Mathieu (mazieus)](https://www.lexaloffle.com/bbs/?pid=diwitorimu),
marked **CC BY-NC-SA**. Their individual READMEs identify which parts are
adapted. Keep the attribution and the applicable license terms when sharing the
games and website. Dino Snacks uses original included art inspired by a paid
sprite pack; the paid pack's files are not included. `TIC80-LICENSE.txt` is kept
with the TIC-80 related material.

## Game design notes

These games use a small, friendly, readable pixel-art style. Most are short
activities for a young player: one task per screen, a few controls, and an
immediate reward for progress. The individual game folders contain the editable
cartridges, build scripts, and game-specific instructions.

## Menu style

- Start with a centered game title, then a plain-language invitation or a
  preview of the activity. MathSplit, Shape Sum, and ColorMix explain the task
  in one short line; Stringer, CountNumbers, MissingNumber, and Dino Snacks
  also show the objects or character the player will use.
- Keep settings on the same screen. Show one meaningful choice, such as a
  maximum number, difficulty tier, or dinosaur, between `<` and `>` markers.
  Left/right changes it; `A` starts. ColorMix skips the setting and starts
  directly. There is no nested menu.
- Put short button hints near the bottom. Use the same terms the player sees
  during play: `left/right:choose`, `a:start`, `a:check` or `a:pick`, and
  `b:menu`. Keep the selected value or character visually obvious.

## Play experience

- Put the puzzle or playfield in the center, with the title and any level or
  progress at the top. Leave room at the bottom for feedback and button hints.
- Use directional controls for a single action at a time: left/right selects
  among visible choices, up/down changes a number or count, and the D-pad
  moves the dinosaur. `A` confirms; `B` returns to the menu.
- Give immediate, gentle feedback. Wrong answers show `try again!` and can be
  retried without penalty. Correct answers get a bright message, sound, and a
  visible reward such as a coin, heart, rainbow band, or filled food icon.
  Some games wait for `A` to continue; CountNumbers, MissingNumber, Stringer,
  and Dino Snacks move on after a short celebration.
- Keep rounds short and repeatable. New puzzles vary the numbers, shapes,
  colors, or order while preserving the same controls. Dino Snacks has no
  hazards, timer, or score.

## UI and artwork

- Work at crisp native pixels and integer scaling. The PICO-8 games use a
  128×128 screen, small pixel text, simple lines and outlines, and generous
  empty space around the main object. Center groups by their full visible
  width, including selection marks and shape edges.
- In the puzzle games, a dark or black background gives the bright focus
  colors room to stand out. Titles, labels, and secondary hints are muted;
  selected values, answers, and success feedback are brighter. Keep text
  brief and readable against its background.
- Use recognizable shapes and friendly sprite art to carry the lesson:
  outlined geometric pieces and beads, colored mixing circles, counting
  objects, a number-bond tree, unicorns and hearts, and expressive dinosaurs.
  Selection marks stay small so they point to the choice without covering it.
- Let each game have its own character. Dino Snacks uses softer greens and
  larger 24×24 dinosaurs on a simple tiled field; MissingNumber uses unicorn
  sprites and a growing rainbow tower. Dragon Fury is a more action-oriented
  TIC-80 exception with a wider scene and a title screen that explains its
  two main buttons.

## Console choice

**PICO-8 is preferred for new homemade games.** Its simpler 128×128 canvas
suits the compact menus, direct controls, and focused puzzles above. Math
games should stay on PICO-8.

Use **TIC-80 only when a game is visually fun and can make meaningful use of
its wider screen and larger pixel count**, such as a scene-rich action game.
The existing TIC-80 versions of several puzzle games are ports; their
presence does not make TIC-80 the default for future math games.
