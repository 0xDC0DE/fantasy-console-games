"""Import the five 40x64 unicorn PNGs into MissingNumber's PICO-8 sprites.

Run from the Gameboy folder: python3 fantasy-console-games/MissingNumber/import_unicorns.py
The supplied PNGs are the source of truth for these five sprite regions.
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "boxart" / ".deps"))
from PIL import Image

CARTRIDGE = HERE / "MissingNumber.p8"
ART = HERE / "unicorn_sprites_v3"
FILES = (
    "01_ivory_left.png",
    "02_ivory_right_raised_hoof.png",
    "03_gray_blue_left.png",
    "04_cream_sunset_right.png",
    "05_midnight_left.png",
)
# Top-left pixel positions for sprite IDs 0, 5, 10, 128, and 133.
POSITIONS = ((0, 0), (40, 0), (80, 0), (0, 64), (40, 64))
HEART = ("00000000", "01100110", "18e11881", "18e88881",
         "18888881", "01888810", "00188100", "00011000")
PALETTE = (
    (0, 0, 0), (29, 43, 83), (126, 37, 83), (0, 135, 81),
    (171, 82, 54), (95, 87, 79), (194, 195, 199), (255, 241, 232),
    (255, 0, 77), (255, 163, 0), (255, 236, 39), (0, 228, 54),
    (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170),
)
COLOR_IDS = {rgb: index for index, rgb in enumerate(PALETTE)}


def read_sprite(filename):
    image = Image.open(ART / filename).convert("RGBA")
    if image.size != (40, 64):
        raise ValueError(f"{filename} must be 40x64 pixels")
    result = []
    for y in range(64):
        row = []
        for x in range(40):
            red, green, blue, alpha = image.getpixel((x, y))
            if alpha == 0:
                row.append(0)
            elif alpha != 255:
                raise ValueError(f"{filename} has partial transparency at {x},{y}")
            else:
                rgb = (red, green, blue)
                if rgb not in COLOR_IDS:
                    raise ValueError(f"{filename} has a non-PICO-8 color {rgb} at {x},{y}")
                # Sprite color 0 is transparent. Use dark blue for opaque black
                # outlines so they remain visible against the game's black sky.
                row.append(COLOR_IDS[rgb] or 1)
        result.append(row)
    return result


def main():
    source = CARTRIDGE.read_text(encoding="ascii")
    before, graphics = source.split("__gfx__\n", 1)
    _, after = graphics.split("__sfx__\n", 1)
    sheet = [[0] * 128 for _ in range(128)]

    for filename, (left, top) in zip(FILES, POSITIONS):
        pixels = read_sprite(filename)
        for y, row in enumerate(pixels):
            sheet[top + y][left:left + 40] = row

    # The 8x8 heart sits in the free strip beside the three top-row unicorns.
    for y, row in enumerate(HEART):
        sheet[y][120:128] = [int(color, 16) for color in row]

    rows = ["".join(format(color, "x") for color in row) for row in sheet]
    CARTRIDGE.write_text(before + "__gfx__\n" + "\n".join(rows)
                         + "\n__sfx__\n" + after, encoding="ascii")
    print(f"Imported {len(FILES)} unicorn sprites into {CARTRIDGE}")


if __name__ == "__main__":
    main()
