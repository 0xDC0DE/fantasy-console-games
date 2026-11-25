# Heart Path

A PICO-8 sequence memory game. Choose a dog, bunny, cat, or duck with
left/right and a sequence length from two to five with up/down. Press A to play.
Each level has three hearts. The field appears first, then the path is shown as
colored arrows over the field for three seconds. Up is blue, right is red,
down is yellow, and left is green.

Use the D-pad to rebuild the sequence in the sky. The last arrow checks it
automatically after a short beat. B removes the last arrow, or returns to the
menu when empty. Each direction has its own tone, heard during the sequence
preview, when entered, and at each walking step. The dog, bunny, cat, and duck
also have four different heart pickup sounds.
On a correct answer, the animal walks the path to the heart. On a wrong answer,
the same sequence appears again and the entry clears. After three hearts, a
four-tone sound plays, then the player may choose an animal again before
starting the next level with A. The chosen sequence length stays the same.
There is no timer or penalty.

## Build and edit

The editable game is `HeartPath.p8`. Its scenery and sounds are original. The
scenery sprites follow the supplied `decor_reference.png` image. The animal
silhouettes come from the supplied `source_animals.jpg` sheet. The importer
samples the center of each enlarged source pixel to avoid JPEG edge
artifacts, doubles each pixel without changing the outline, and reduces only
the colors. Run `import_sprites.py` to refresh the editable animals and scenery.
Run the project update command from the Gameboy folder to build the ROM,
launcher, browser export, and artwork:

```sh
python3 fantasy-console-games/update_game.py HeartPath
python3 fantasy-console-games/update_game.py HeartPath --check
```

The play area is an invisible four by three grid across the grass. Trees,
bushes, rocks, ponds, the dog house, flowers, and mushrooms decorate the scene
and do not block movement. The chosen sequence always reaches its heart. The
level appears before the three-second sequence overlay; the player rebuilds
the sequence in the sky below the heart indicator.
