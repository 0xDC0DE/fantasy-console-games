"""Copy the user's dinosaur and food art into PICO-8 sprite frames.

Run from the Gameboy folder: python3 fantasy-console-games/DinoSnacks/import_sprites.py
This replaces only the cartridge's __gfx__ section. Keep editing the PNGs if
you want to rerun the import; edits made in PICO-8's sprite editor afterward
will be replaced for the dinosaur and food frames by the next import.
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "boxart" / ".deps"))
from PIL import Image

SOURCE = HERE / "dino-sprites-24.png"
CARTRIDGE = HERE / "DinoSnacks.p8"

# These are display colors. Slots 2, 4, 9, and 14 are remapped in _init().
DISPLAY_PALETTE = [
    (0, 0, 0), (29, 43, 83), (117, 70, 101), (0, 135, 81),
    (0, 181, 67), (95, 87, 79), (194, 195, 199), (255, 241, 232),
    (255, 0, 77), (255, 110, 89), (255, 236, 39), (0, 228, 54),
    (41, 173, 255), (131, 118, 156), (255, 157, 129), (255, 204, 170),
]

# Game order: stegosaur, t-rex, triceratops. Each group is side x2,
# front x2, back x2. Coordinates are (source row, source column).
SOURCE_FRAMES = [
    (4, 0), (4, 1), (3, 0), (3, 1), (3, 2), (3, 3),
    (2, 2), (2, 3), (1, 2), (1, 3), (2, 0), (2, 1),
    (1, 0), (1, 1), (0, 0), (0, 1), (0, 2), (0, 3),
]
FRAME_IDS = [0, 3, 6, 9, 12, 48, 51, 54, 57, 60,
             96, 99, 102, 105, 108, 144, 147, 150]
SOURCE_X = (20, 168, 316, 464)
SOURCE_Y = (31, 186, 336, 491, 646)
BACKGROUND = (102, 155, 101)
# Preserve each flat source color's role in the nearest available PICO palette.
COLORS = {
    (56, 40, 65): 1,       # outline
    (105, 68, 129): 2,     # deep purple
    (104, 54, 116): 2,
    (144, 106, 172): 13,   # triceratops purple
    (149, 87, 169): 13,    # stegosaur plates
    (180, 118, 195): 6,    # light plate highlight
    (57, 122, 217): 12,    # t-rex blue
    (39, 97, 184): 13,     # t-rex shadow, closest available indigo
    (145, 201, 236): 6,    # t-rex highlight
    (245, 130, 114): 14,   # stegosaur coral
    (215, 103, 96): 9,     # stegosaur shadow
    (255, 194, 161): 15,   # warm highlight
    (255, 240, 198): 7,    # horns and teeth
    (255, 255, 255): 7,
}
FOOD_COLORS = {
    (29, 43, 83): 1,      # dark outline
    (0, 135, 81): 3,      # leaf shadow
    (255, 0, 77): 8,      # steak red
    (255, 163, 0): 9,     # steak warm edge
    (255, 236, 39): 10,   # leaf yellow
    (0, 228, 54): 11,     # leaf green
    (41, 173, 255): 12,  # blue edge
    (255, 119, 168): 14, # steak highlight
    (255, 241, 232): 7,  # steak bone
}


def sprite_pixels(sheet, sprite_id, width, height):
    x0 = sprite_id % 16 * 8
    y0 = sprite_id // 16 * 8
    return [[sheet[y0 + y][x0 + x] for x in range(width)]
            for y in range(height)]


def place(sheet, sprite_id, pixels):
    x0 = sprite_id % 16 * 8
    y0 = sprite_id // 16 * 8
    for y, row in enumerate(pixels):
        for x, color in enumerate(row):
            sheet[y0 + y][x0 + x] = color


def convert_pose(image, row, col):
    """Read 24x24 source pixels from the five-times-enlarged preview sheet."""
    x0 = SOURCE_X[col]
    y0 = SOURCE_Y[row]
    result = []
    for y in range(24):
        line = []
        for x in range(24):
            rgb = image.getpixel((x0 + x * 5 + 2, y0 + y * 5 + 2))[:3]
            if rgb == BACKGROUND:
                line.append(0)
            elif rgb in COLORS:
                line.append(COLORS[rgb])
            else:
                raise ValueError(f"Unknown sprite color {rgb} in row {row + 1}, "
                                 f"column {col + 1}")
        result.append(line)
    return result


def convert_food(name):
    image = Image.open(HERE / name).convert("RGBA")
    if image.size != (16, 16):
        raise ValueError(f"Expected a 16x16 food sprite in {name}")
    result = []
    for y in range(16):
        line = []
        for x in range(16):
            red, green, blue, alpha = image.getpixel((x, y))
            if alpha == 0:
                line.append(0)
            else:
                rgb = (red, green, blue)
                if rgb not in FOOD_COLORS:
                    raise ValueError(f"Unknown food color {rgb} in {name}")
                line.append(FOOD_COLORS[rgb])
        result.append(line)
    return result


def food_outline(pixels):
    result = [[0] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if pixels[y][x] and any(
                nx < 0 or ny < 0 or nx >= 16 or ny >= 16
                or pixels[ny][nx] == 0
                for nx, ny in ((x - 1, y), (x + 1, y),
                               (x, y - 1), (x, y + 1))
            ):
                result[y][x] = 6
    return result


def outline_shape(pixels):
    """Add a dark one-pixel edge around a filled obstacle."""
    original = [row[:] for row in pixels]
    for y in range(16):
        for x in range(16):
            if original[y][x]:
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 16 and 0 <= ny < 16 and not original[ny][nx]:
                        pixels[ny][nx] = 1
    return pixels


def make_rock_alt():
    pixels = [[0] * 16 for _ in range(16)]
    spans = {2: (7, 9), 3: (6, 10), 4: (5, 11),
             5: (4, 11), 6: (4, 12), 7: (3, 12),
             8: (3, 13), 9: (2, 13), 10: (2, 13),
             11: (2, 13), 12: (3, 12), 13: (3, 12),
             14: (4, 11)}
    for y, (left, right) in spans.items():
        for x in range(left, right + 1):
            pixels[y][x] = 5
    for x, y in ((7, 3), (7, 4), (6, 5), (7, 5), (5, 6),
                 (6, 6), (5, 7), (6, 7), (4, 8), (5, 8)):
        pixels[y][x] = 6
    for x, y in ((9, 8), (10, 8), (9, 9), (11, 10),
                 (6, 11), (7, 11), (10, 12)):
        pixels[y][x] = 13
    return outline_shape(pixels)


def make_pool():
    pixels = [[0] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            edge = ((x - 7.5) / 6.8) ** 2 + ((y - 8) / 5.2) ** 2
            inside = ((x - 7.5) / 5.6) ** 2 + ((y - 8) / 4.0) ** 2
            if edge <= 1:
                pixels[y][x] = 1
            if inside <= 1:
                pixels[y][x] = 12 if y < 10 else 13
    for x, y in ((5, 5), (6, 5), (4, 6), (5, 6), (11, 8)):
        pixels[y][x] = 7
    return pixels


def make_heart():
    rows = ("00000000", "01100110", "18e11881", "18e88881",
            "18888881", "01888810", "00188100", "00011000")
    return [[int(color, 16) for color in row] for row in rows]


def existing_or_new(sheet, sprite_id, width, height, maker):
    pixels = sprite_pixels(sheet, sprite_id, width, height)
    return pixels if any(color for row in pixels for color in row) else maker()


def main():
    image = Image.open(SOURCE).convert("RGBA")
    if image.size != (604, 818):
        raise ValueError("Expected the 604x818 five-row sprite sheet")

    source = CARTRIDGE.read_text(encoding="ascii")
    before, graphics = source.split("__gfx__\n", 1)
    old_rows, after = graphics.split("__sfx__\n", 1)
    old_sheet = [[int(char, 16) for char in row]
                 for row in old_rows.splitlines()]
    old_sheet.extend([[0] * 128 for _ in range(128 - len(old_sheet))])

    # Preserve rock edits made in PICO-8 between imports.
    new_rock_exists = any(color for row in sprite_pixels(old_sheet, 200, 16, 16)
                          for color in row)
    rock_id = 200 if new_rock_exists else 196
    rock = sprite_pixels(old_sheet, rock_id, 16, 16)

    sheet = [[0] * 128 for _ in range(128)]
    for sprite_id, (row, col) in zip(FRAME_IDS, SOURCE_FRAMES):
        place(sheet, sprite_id, convert_pose(image, row, col))
    leaf = convert_food("leaf.png")
    steak = convert_food("steak.png")
    for sprite_id, pixels in ((192, leaf), (194, steak),
                              (196, food_outline(leaf)),
                              (198, food_outline(steak))):
        place(sheet, sprite_id, pixels)
    place(sheet, 200, rock)
    place(sheet, 202, existing_or_new(old_sheet, 202, 16, 16,
                                      make_rock_alt))
    place(sheet, 204, existing_or_new(old_sheet, 204, 16, 16,
                                      make_pool))
    place(sheet, 206, existing_or_new(old_sheet, 206, 8, 8,
                                      make_heart))

    rows = ["".join(format(color, "x") for color in row) for row in sheet]
    CARTRIDGE.write_text(before + "__gfx__\n" + "\n".join(rows)
                         + "\n__sfx__\n" + after, encoding="ascii")
    print(f"Imported 18 dinosaur poses and 2 food sprites into {CARTRIDGE.name}")


if __name__ == "__main__":
    main()
