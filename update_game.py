#!/usr/bin/env python3
"""Build and publish a local fantasy-console game from the Gameboy workspace."""

import argparse
from datetime import datetime
import hashlib
from html import escape
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


GAMES = Path(__file__).resolve().parent
ROOT = GAMES.parent
WEB = GAMES / "website" / "public"
FUN = {"DinoSnacks", "FireDragon"}
KNOWN = {"ColorMix", "CountNumbers", "DinoSnacks", "FireDragon", "FrogHopper", "HeartPath", "MathSplit", "MissingNumber", "ShapeSum", "Stringer"}
SPECIAL = {"FireDragon": ("Dragon Fury", "dragon-fury", "dragon_fury.tic")}


def title_for(folder):
    if folder in SPECIAL:
        return SPECIAL[folder][0]
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", folder)


def slug_for(folder):
    if folder in SPECIAL:
        return SPECIAL[folder][1]
    return title_for(folder).lower().replace(" ", "-")


def source_for(folder):
    directory = GAMES / folder
    if not directory.is_dir() or not (directory / "build.py").is_file():
        raise ValueError(f"{folder}: expected a game folder with build.py")
    pico = directory / f"{folder}.p8"
    if pico.is_file():
        return "PICO-8", pico
    if folder == "FireDragon":
        return "TIC-80", directory / SPECIAL[folder][2]
    tic = [p for p in directory.glob("*.tic") if not p.stem.endswith("-original")]
    if len(tic) == 1:
        return "TIC-80", tic[0]
    raise ValueError(f"{folder}: expected {folder}.p8 or one .tic cartridge")


def rom_for(folder, console, source):
    if console == "PICO-8":
        return ROOT / "ROMS" / console / f"{folder}.p8.png"
    return ROOT / "ROMS" / console / source.name


def launcher_text(folder, title, console, source, rom):
    name = "Play Dragon Fury.command" if folder == "FireDragon" else f"Play {folder}.command"
    if console == "PICO-8":
        app = 'pico8_app=${PICO8_APP:-$HOME/Downloads/pico-8/PICO-8.app}'
        start = 'open -n -a "$pico8_app" --args -run "$cartridge"'
        check_app = '[[ -d "$pico8_app" ]] || { print -u2 "PICO-8 app missing: $pico8_app"; exit 1; }'
    else:
        app = 'tic80_app=${TIC80_APP:-$gameboy_dir/tools/TIC-80.app}'
        start = f'open -n -a "$tic80_app" --args --fs "$gameboy_dir/ROMS/TIC-80" --cmd \'load {source.name} & run\''
        check_app = '[[ -d "$tic80_app" ]] || { print -u2 "TIC-80 app missing: $tic80_app"; exit 1; }'
    relative_rom = rom.relative_to(ROOT)
    return name, f'''#!/bin/zsh

launcher_dir=${{0:A:h}}
gameboy_dir=${{launcher_dir:h:h}}
{app}
cartridge="$gameboy_dir/{relative_rom}"

[[ -f "$cartridge" ]] || {{ print -u2 "Cartridge missing: $cartridge"; exit 1; }}
{check_app}
if [[ $1 == --check ]]; then
 print -r -- "$cartridge"
 exit 0
fi
{start}
'''


def write_launcher(folder, title, console, source, rom):
    name, content = launcher_text(folder, title, console, source, rom)
    path = GAMES / "launchers" / name
    path.write_text(content)
    path.chmod(0o755)
    subprocess.run(["zsh", "-n", str(path)], check=True)
    return path


def run(command, **kwargs):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True, **kwargs)


def app_binary(env_name, default_app, executable):
    app = Path(os.environ.get(env_name, default_app)).expanduser()
    binary = app / "Contents" / "MacOS" / executable if app.suffix == ".app" else app
    if not binary.is_file():
        raise FileNotFoundError(f"Set {env_name} to an installed {executable} app or executable: {binary}")
    return binary


def backup_art(folder, art):
    digest = hashlib.sha256(art.read_bytes()).hexdigest()[:12]
    destination = ROOT / "backups" / "game-art" / folder
    destination.mkdir(parents=True, exist_ok=True)
    if not list(destination.glob(f"*-{digest}.png")):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(art, destination / f"{timestamp}-{digest}.png")


def sync_art(folder, slug, console, rom):
    art = GAMES / folder / "art.png"
    if not art.is_file():
        raise FileNotFoundError(f"{art} is missing; save a gameplay screenshot or custom art as art.png")
    try:
        from PIL import Image, ImageOps
    except ImportError:
        sys.path.insert(0, str(ROOT / "boxart" / ".deps"))
        from PIL import Image, ImageOps
    with Image.open(art) as image:
        image.load()
        if image.width < 64 or image.height < 64:
            raise ValueError(f"Art is too small: {art}")
        web_art = WEB / "assets" / "screens" / f"{slug}.png"
        web_art.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(art, web_art)
        backup_art(folder, art)
        for directory, size in (("box", 384), ("grid", 120)):
            output = ROOT / "boxart" / console / directory
            output.mkdir(parents=True, exist_ok=True)
            square = ImageOps.pad(image.convert("RGB"), (size, size), method=Image.Resampling.NEAREST, color="#080b15")
            names = (rom.name + ".png", rom.stem + ".png") if console == "TIC-80" else (rom.name, rom.name.removesuffix(".p8.png") + ".png")
            for name in names:
                square.save(output / name, format="PNG")


def ensure_web_page(folder, title, slug, console):
    page = WEB / "games" / slug / "index.html"
    if page.is_file():
        return
    safe = escape(title)
    wide = console == "TIC-80"
    page_class = "play-page wide-page" if wide else "play-page"
    player_class = "player wide" if wide else "player"
    controls_class = "controls wide" if wide else "controls"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f5f6fb">
  <title>{safe} · Little Pixel Games</title>
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/assets/play.css">
</head>
<body>
<main class="{page_class}">
  <a class="back-link" href="/">All games</a>
  <h1>{safe}</h1>
  <iframe class="{player_class}" title="{safe} game" src="player/" allow="autoplay; fullscreen" allowfullscreen></iframe>
  <section class="{controls_class}" aria-labelledby="controls-title">
    <h2 id="controls-title">Keyboard controls</h2>
    <ul class="control-list">
      <li>Try the <kbd>arrow keys</kbd> to play.</li>
      <li>Try <kbd>X</kbd> and <kbd>Z</kbd> for actions. On AZERTY keyboards, try <kbd>X</kbd> and <kbd>W</kbd>.</li>
      <li><kbd>C</kbd> Return to the menu</li>
    </ul>
  </section>
</main>
</body>
</html>
''')


def ensure_web_index(title, slug, category, downloads):
    index = WEB / "index.html"
    html = index.read_text()
    if f'href="/games/{slug}/"' in html:
        return
    if not category:
        raise ValueError(f"New game {title}: pass --category educational or fun")
    section_id = "educational-title" if category == "educational" else "fun-title"
    start = html.index(f'aria-labelledby="{section_id}"')
    end = html.index("</section>", start)
    insert_at = html.rfind("    </div>", start, end)
    links = "".join(f'<a href="/downloads/{escape(p.name)}" download>Download for {console}</a>' for p, console in downloads)
    card = f'''      <article class="game-card">
        <a class="thumbnail" href="/games/{slug}/" aria-label="Play {escape(title)}"><img src="/assets/screens/{slug}.png" alt="" loading="lazy"></a>
        <div class="card-content">
          <h3>{escape(title)}</h3>
          <a class="play-button" href="/games/{slug}/">Play</a>
          <div class="downloads">{links}</div>
        </div>
      </article>
'''
    index.write_text(html[:insert_at] + card + html[insert_at:])


def version_web_assets(slug, art, rom, player, console, downloads):
    """Change asset URLs when their content changes, avoiding stale browser caches."""
    art_version = hashlib.sha256(art.read_bytes()).hexdigest()[:12]
    player_file = player / ("index.js" if console == "PICO-8" else "cart.tic")
    player_version = hashlib.sha256(player_file.read_bytes()).hexdigest()[:12]
    index = WEB / "index.html"
    html = index.read_text()
    screen = rf'(src="/assets/screens/{re.escape(slug)}\.png)(?:\?v=[0-9a-f]+)?"'
    html, count = re.subn(screen, lambda match: f'{match.group(1)}?v={art_version}"', html)
    if count != 1:
        raise ValueError(f"Expected one screenshot for {slug} in {index}, found {count}")
    for file, _ in downloads:
        digest = hashlib.sha256(file.read_bytes()).hexdigest()[:12]
        download = rf'(href="/downloads/{re.escape(file.name)})(?:\?v=[0-9a-f]+)?"'
        html, count = re.subn(download, lambda match: f'{match.group(1)}?v={digest}"', html)
        if count != 1:
            raise ValueError(f"Expected one download link for {file.name} in {index}, found {count}")
    index.write_text(html)

    page = WEB / "games" / slug / "index.html"
    html = page.read_text()
    html, count = re.subn(r'src="player/(?:\?v=[0-9a-f]+)?"',
                          f'src="player/?v={player_version}"', html)
    if count != 1:
        raise ValueError(f"Expected one player iframe in {page}, found {count}")
    page.write_text(html)

    if console == "PICO-8":
        exported = player / "index.html"
        html = exported.read_text()
        html, count = re.subn(r'e\.src = "index\.js(?:\?v=[0-9a-f]+)?";',
                              f'e.src = "index.js?v={player_version}";', html)
        if count != 1:
            raise ValueError(f"Expected one PICO-8 script URL in {exported}, found {count}")
        exported.write_text(html)


def update(folder, title, category, launcher_only=False):
    console, source = source_for(folder)
    slug = slug_for(folder) if title == title_for(folder) else re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    rom = rom_for(folder, console, source)
    launcher = write_launcher(folder, title, console, source, rom)
    if launcher_only:
        print(f"Launcher: {launcher}")
        return
    art = GAMES / folder / "art.png"
    if not art.is_file():
        raise FileNotFoundError(f"Add {art} before publishing")
    if not (WEB / "games" / slug / "index.html").is_file() and not category:
        raise ValueError(f"New game {title}: pass --category educational or fun")
    run([sys.executable, source.parent / "build.py"])
    if console == "TIC-80":
        rom.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, rom)
    if not rom.is_file():
        raise FileNotFoundError(f"Builder did not create {rom}")
    downloads = [(rom, console)]
    port = source.parent / f"{folder}.tic"
    port_rom = None
    if console == "PICO-8" and port.is_file():
        port_rom = ROOT / "ROMS" / "TIC-80" / port.name
        port_rom.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(port, port_rom)
        downloads.append((port_rom, "TIC-80"))
    for file, _ in downloads:
        target = WEB / "downloads" / file.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
    player = WEB / "games" / slug / "player"
    player.mkdir(parents=True, exist_ok=True)
    if console == "PICO-8":
        pico8 = app_binary("PICO8_APP", Path.home() / "Downloads/pico-8/PICO-8.app", "pico8")
        run([pico8, rom, "-export", player / "index.html"])
        if not (player / "index.js").is_file():
            raise FileNotFoundError(f"PICO-8 did not write {player / 'index.js'}")
    elif (player / "cart.tic").is_file():
        shutil.copy2(rom, player / "cart.tic")
    else:
        raise ValueError("New TIC-80 games need a browser player export before publishing")
    sync_art(folder, slug, console, rom)
    if port_rom:
        sync_art(folder, slug, "TIC-80", port_rom)
    ensure_web_page(folder, title, slug, console)
    ensure_web_index(title, slug, category, downloads)
    version_web_assets(slug, art, rom, player, console, downloads)
    print(f"Published {title}: {rom}, {launcher}, website, and artwork")


def check(folder, title):
    console, source = source_for(folder)
    slug = slug_for(folder) if title == title_for(folder) else re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    rom = rom_for(folder, console, source)
    name, expected = launcher_text(folder, title, console, source, rom)
    launcher = GAMES / "launchers" / name
    if not launcher.is_file() or launcher.read_text() != expected:
        raise ValueError(f"Launcher is missing or stale: {launcher}; run --launchers-only")
    run(["zsh", str(launcher), "--check"])
    art = GAMES / folder / "art.png"
    web_art = WEB / "assets/screens" / f"{slug}.png"
    player = WEB / "games" / slug / "player"
    required = (rom, art, web_art, WEB / "downloads" / rom.name,
                WEB / "games" / slug / "index.html", player / "index.html",
                player / ("index.js" if console == "PICO-8" else "cart.tic"),
                ROOT / "boxart" / console / "box" / (rom.name if console == "PICO-8" else rom.stem + ".png"),
                ROOT / "boxart" / console / "grid" / (rom.name if console == "PICO-8" else rom.stem + ".png"))
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)
    if art.read_bytes() != web_art.read_bytes() or rom.read_bytes() != (WEB / "downloads" / rom.name).read_bytes():
        raise ValueError(f"{title}: website files are stale; rerun the update")
    digest = hashlib.sha256(art.read_bytes()).hexdigest()[:12]
    if not list((ROOT / "backups" / "game-art" / folder).glob(f"*-{digest}.png")):
        raise FileNotFoundError(f"Current art has no backup for {title}")
    port = source.parent / f"{folder}.tic"
    if console == "PICO-8" and port.is_file():
        port_rom = ROOT / "ROMS" / "TIC-80" / port.name
        port_download = WEB / "downloads" / port.name
        for path in (port_rom, port_download,
                     ROOT / "boxart" / "TIC-80" / "box" / f"{port.stem}.png",
                     ROOT / "boxart" / "TIC-80" / "grid" / f"{port.stem}.png"):
            if not path.is_file():
                raise FileNotFoundError(path)
        if port.read_bytes() != port_rom.read_bytes() or port_rom.read_bytes() != port_download.read_bytes():
            raise ValueError(f"{title}: TIC-80 port is stale; rerun the update")
    print(f"OK: {title}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", nargs="?", help="Game folder name, such as Stringer")
    parser.add_argument("--all", action="store_true", help="Process all game folders with build.py")
    parser.add_argument("--check", action="store_true", help="Check launchers and published files without writing")
    parser.add_argument("--launchers-only", action="store_true", help="Generate launchers without rebuilding cartridges")
    parser.add_argument("--title", help="Display name for a new game")
    parser.add_argument("--category", choices=("educational", "fun"), help="Website section for a new game")
    args = parser.parse_args()
    if args.all == bool(args.game):
        parser.error("Choose one game folder or --all")
    folders = sorted(p.name for p in GAMES.iterdir() if (p / "build.py").is_file()) if args.all else [args.game]
    for folder in folders:
        title = args.title or title_for(folder)
        category = args.category or ("fun" if folder in FUN else "educational" if folder in KNOWN else None)
        if args.check:
            check(folder, title)
        else:
            update(folder, title, category, args.launchers_only)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
