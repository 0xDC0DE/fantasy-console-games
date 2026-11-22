"""Package the Apple silicon TIC-80 app and current games for another Mac."""

from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "TIC80-Mac"
ARCHIVE = ROOT / "TIC80-Mac.zip"
APP = ROOT / "tools/TIC-80.app"
GAMES = ("Stringer", "MathSplit", "ColorMix", "ShapeSum")


def write_executable(path, content):
    path.write_text(content)
    path.chmod(0o755)


def game_launcher(name):
    return f'''#!/bin/zsh
bundle_dir=${{0:A:h}}
tic80_app="$bundle_dir/TIC-80.app"
games_dir="$bundle_dir/Games"

open -n -a "$tic80_app" --args --fs "$games_dir" --cmd 'load {name}.tic & run'
'''


INSTALLER = '''#!/bin/zsh
set -e

bundle_dir=${0:A:h}
source_app="$bundle_dir/TIC-80.app"
install_dir="${1:-$HOME/Applications}"
installed_app="$install_dir/TIC-80.app"

mkdir -p "$install_dir"
if [[ -e "$installed_app" || -L "$installed_app" ]]; then
  if cmp -s "$source_app/Contents/MacOS/tic80" "$installed_app/Contents/MacOS/tic80"; then
    echo "TIC-80 is already installed in $install_dir"
  else
    echo "Another TIC-80.app exists in $install_dir. I left it unchanged."
    echo "You can still play with the launchers in this folder."
    exit 1
  fi
else
  ditto "$source_app" "$installed_app"
  echo "Installed TIC-80 in $install_dir"
fi
if [[ $# -eq 0 ]]; then open -R "$installed_app"; fi
'''


README = '''TIC-80 games for Apple silicon Macs
====================================

1. Unzip TIC80-Mac.zip, then keep this folder together.
2. Double-click a "Play ... .command" file to start a game. The included
   TIC-80.app is used, so installation is optional.
3. To put TIC-80 in your personal Applications folder, double-click
   "Install TIC-80.command". It does not require an administrator password.

If macOS blocks TIC-80 or a launcher on first use, try opening it once,
then go to System Settings > Privacy & Security > Open Anyway and confirm.
Only do this for the bundle you copied from your own Mac.

The launchers use the app inside this folder even after installation. Keep
this folder if you want to keep using them. For the handheld, copy only the
.tic files in Games to its TIC-80 ROM folder.

TIC-80 1.4.1 for macOS arm64 is from the official release:
https://github.com/nesbox/TIC-80/releases/tag/v1.4.1

Some Stringer, MathSplit, ColorMix, and ShapeSum coin art and effects are
adapted from "Rekenspelletje" by Mathieu (mazieus), whose PICO-8 cartridge
is marked CC BY-NC-SA:
https://www.lexaloffle.com/bbs/?pid=diwitorimu
'''


def main():
    if not APP.is_dir():
        raise SystemExit(f"Missing TIC-80 app: {APP}")
    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)
    DESTINATION.mkdir()
    subprocess.run(["ditto", str(APP), str(DESTINATION / "TIC-80.app")], check=True)

    games_dir = DESTINATION / "Games"
    games_dir.mkdir()
    for name in GAMES:
        cartridge = ROOT / "homemade" / name / f"{name}.tic"
        shutil.copy2(cartridge, games_dir / cartridge.name)
        write_executable(DESTINATION / f"Play {name}.command", game_launcher(name))

    write_executable(DESTINATION / "Install TIC-80.command", INSTALLER)
    (DESTINATION / "README.txt").write_text(README)
    shutil.copy2(ROOT / "homemade/TIC80-LICENSE.txt", DESTINATION / "TIC-80-LICENSE.txt")

    if ARCHIVE.exists():
        ARCHIVE.unlink()
    subprocess.run(
        ["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(DESTINATION), str(ARCHIVE)],
        check=True,
    )
    print(f"Built {ARCHIVE}")


if __name__ == "__main__":
    main()
