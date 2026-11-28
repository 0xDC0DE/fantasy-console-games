# Little Pixel Games website

Static website containing browser exports of twelve games. `public/` is the
web root; it includes the game index, gameplay screenshots, downloadable cartridges, and
the PICO-8 and TIC-80 HTML players. The exported players are checked in so a
Docker build does not need either fantasy console installed.

Each game has a play page at `public/games/<game>/index.html` with its PC
keyboard controls below the player. The console export lives in that game's
`player/` subfolder. On PC, the PICO-8 games use **X** to start or confirm and
**C** to return to the menu.

## Run locally

```sh
cd website
python3 -m http.server 8080 --directory public
```

Open `http://localhost:8080`. Browser players need HTTP; opening the HTML files
directly may fail, especially Dragon Fury's WebAssembly player.

## Docker and Traefik

```sh
cd website
cp .env.example .env
# Set DOMAINNAME to your real domain in .env.
docker compose up -d --build
```

The example domain becomes `games.example.com`. Compose builds an
`nginx:alpine` image and attaches it to your existing external
`traefik2_proxy` network. Your Traefik instance must have an entrypoint named
`https`, and DNS must point the hostname to it. To change the hostname, edit
the `Host(...)` rule in `compose.yaml`. No volume mount is needed: the site is
copied into the image.

To push an image to a registry, tag and push `fantasy-console-games:local`,
then replace `build: .` and `image:` in Compose with your registry image name.

## Refresh browser exports

The source games live one directory above this site. From the Gameboy folder,
run `python3 fantasy-console-games/update_game.py Stringer` (or use `--all`).
It rebuilds the cartridge under `ROMS/`, refreshes browser exports and
downloads, and copies each game's `art.png` to the website screenshots.

For a manual PICO-8 browser export, use the labeled cartridge and installed
PICO-8 CLI:

```sh
pico8 /path/to/ColorMix.p8.png -export /path/to/website/public/games/color-mix/player/index.html
```

That writes both `index.html` and `index.js`. The labeled cartridge is needed;
exporting an unlabeled `.p8` source may stop with “please capture a label
first”. The site also offers the existing `.tic` ports for Color Mix, Count Numbers,
Math Split, Shape Sum, and Stringer; refresh those downloads from their game
folders after rebuilding a port.

Dragon Fury was exported with TIC-80's CLI:

```sh
tic80 --cli --fs /path/to/FireDragon --cmd='load dragon_fury.tic & export html DragonFury.zip & exit'
unzip -o /path/to/FireDragon/DragonFury.zip -d /path/to/website/public/games/dragon-fury/player
chmod 644 /path/to/website/public/games/dragon-fury/player/*
```

The TIC-80 export contains `index.html`, `tic80.js`, `tic80.wasm`, and
`cart.tic`. Copy the updated `.tic` to `public/downloads/` as well. Exports
must be regenerated with installed PICO-8 and TIC-80; the Docker image only
serves them. The TIC-80 ZIP can mark its generated HTML and cartridge files
unreadable, so the `chmod` step is needed before building the image.
