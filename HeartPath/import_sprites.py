"""Import animal silhouettes from the user's original sheet into Heart Path.

The source is a JPEG enlargement of pixel art. Each original pixel spans about
7.58 image pixels, so sample its center to avoid JPEG edge artifacts. Nearest
neighbor doubling keeps every source pixel in the same shape and position.
Only colors are reduced to the PICO-8 palette; the silhouettes are untouched.
"""

from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "boxart" / ".deps"))
    from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_animals.jpg"
CARTRIDGE = HERE / "HeartPath.p8"
SHEET = HERE / "sprites.png"
PIXEL_SIZE = 7.58

# Name, first source pixel, and original pixel dimensions. Order matches the
# four 24x24 PICO-8 slots at x=0,24,48,72 on the first graphics row.
ANIMALS = (
    ("dog", 165, 41, 10, 10),
    ("bunny", 270, 133, 7, 11),
    ("cat", 82, 41, 9, 10),
    ("duck", 429, 147, 9, 9),
)

# Each source animal has a few dominant colors. Keep its original dark details
# and shape, while using at most four game colors per animal.
COLORS = {
    "dog": (((240, 170, 90), 15), ((200, 140, 80), 9),
            ((100, 75, 55), 4), ((45, 55, 55), 1)),
    "bunny": (((170, 180, 170), 7), ((140, 155, 155), 13),
              ((45, 60, 60), 1), ((220, 160, 100), 9)),
    "cat": (((250, 170, 60), 9), ((235, 110, 30), 4),
            ((45, 60, 60), 1)),
    "duck": (((250, 200, 80), 10), ((250, 170, 60), 9),
             ((220, 150, 40), 9), ((50, 60, 60), 1)),
}

PALETTE = (
    (0, 0, 0), (29, 43, 83), (117, 70, 101), (0, 135, 81),
    (171, 82, 54), (95, 87, 79), (194, 195, 199), (255, 241, 232),
    (255, 0, 77), (255, 108, 36), (255, 236, 39), (168, 231, 46),
    (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170),
)


def source_pixel(image, x0, y0, col, row):
    x = round(x0 + (col + 0.5) * PIXEL_SIZE)
    y = round(y0 + (row + 0.5) * PIXEL_SIZE)
    return image.getpixel((x, y))


def game_color(name, rgb):
    # All animal colors are far from white at pixel centers. This threshold
    # removes the JPEG background without trimming the source silhouettes.
    if min(rgb) >= 220:
        return 0
    return min(COLORS[name], key=lambda item: sum(
        (rgb[i] - item[0][i]) ** 2 for i in range(3)))[1]


def import_animals(gfx, image):
    for slot, (name, sx, sy, width, height) in enumerate(ANIMALS):
        base_x = slot * 24
        # Bottom-align differing source heights so feet share one ground line.
        offset_x = (24 - width * 2) // 2
        offset_y = 22 - height * 2
        for y in range(24):
            for x in range(24):
                gfx[y][base_x + x] = 0
        for row in range(height):
            for col in range(width):
                color = game_color(name, source_pixel(image, sx, sy, col, row))
                for yy in range(2):
                    for xx in range(2):
                        gfx[offset_y + row * 2 + yy][base_x + offset_x + col * 2 + xx] = color


def import_decorations(gfx):
    """Draw crisp scenery inspired by decor_reference.png into spare GFX slots."""
    sheet = Image.new("P", (128, 128))
    sheet.putdata([color for row in gfx for color in row])
    d = ImageDraw.Draw(sheet)
    for x0, y0, x1, y1 in ((0, 32, 95, 47), (96, 32, 111, 39),
                           (0, 64, 31, 111), (32, 64, 55, 87),
                           (64, 64, 87, 79), (88, 64, 119, 79),
                           (32, 96, 47, 111), (48, 96, 63, 111),
                           (64, 96, 71, 111)):
        d.rectangle((x0, y0, x1, y1), fill=0)

    # 32x48 tree: a branched trunk and stepped, shaded canopy.
    d.polygon([(13, 111), (13, 94), (10, 89), (8, 88), (9, 85),
               (15, 91), (15, 80), (19, 80), (19, 89), (23, 85),
               (25, 87), (20, 93), (20, 111)], fill=4, outline=4)
    d.rectangle((15, 94, 16, 109), fill=9)
    d.rectangle((11, 109, 23, 111), fill=4, outline=4)
    d.polygon([(10, 68), (20, 68), (20, 65), (25, 65), (25, 69),
               (29, 69), (29, 74), (31, 74), (31, 87), (28, 87),
               (28, 91), (23, 91), (23, 94), (7, 94), (7, 91),
               (3, 91), (3, 87), (0, 87), (0, 76), (3, 76),
               (3, 71), (7, 71), (7, 68)], fill=11, outline=11)
    for rect in ((5, 80, 10, 84), (11, 72, 15, 75), (20, 77, 25, 81),
                 (14, 86, 18, 90), (24, 86, 27, 89)):
        d.rectangle(rect, fill=3)
    for x, y in ((8, 77), (18, 71), (23, 84)):
        d.rectangle((x, y, x + 2, y + 1), fill=10)

    # 24x24 dog house mirrored exactly around the center between pixels 11/12.
    hx, hy = 32, 64
    d.rectangle((hx + 3, hy + 11, hx + 20, hy + 23), fill=4, outline=4)
    d.rectangle((hx + 5, hy + 14, hx + 7, hy + 20), fill=9)
    d.rectangle((hx + 16, hy + 14, hx + 18, hy + 20), fill=9)
    d.rectangle((hx + 9, hy + 16, hx + 14, hy + 23), fill=5)
    for row in range(11):
        left, right = 11 - row, 12 + row
        d.line((hx + left, hy + row, hx + right, hy + row), fill=8)
        d.point((hx + left, hy + row), fill=8)
        d.point((hx + right, hy + row), fill=8)
    d.line((hx + 1, hy + 11, hx + 22, hy + 11), fill=8)
    d.line((hx + 2, hy + 12, hx + 21, hy + 12), fill=7)

    # 24x16 bush: three green lobes with darker interior patches.
    bx, by = 64, 64
    d.ellipse((bx, by + 5, bx + 12, by + 15), fill=11, outline=11)
    d.ellipse((bx + 6, by, bx + 18, by + 15), fill=11, outline=11)
    d.ellipse((bx + 12, by + 4, bx + 23, by + 15), fill=11, outline=11)
    d.rectangle((bx + 5, by + 9, bx + 8, by + 11), fill=3)
    d.rectangle((bx + 14, by + 5, bx + 17, by + 7), fill=3)

    # 32x16 pond: irregular shore and bright water highlights.
    px, py = 88, 64
    d.polygon([(px + 3, py + 4), (px + 10, py + 4),
               (px + 10, py + 2), (px + 20, py + 2),
               (px + 20, py + 4), (px + 28, py + 4),
               (px + 31, py + 7), (px + 31, py + 11),
               (px + 27, py + 14), (px + 4, py + 14),
               (px, py + 10), (px, py + 7)], fill=12, outline=12)
    d.line((px + 5, py + 7, px + 10, py + 7), fill=7, width=2)
    d.line((px + 18, py + 10, px + 22, py + 10), fill=7, width=2)

    # Rock and mushroom occupy small independent sprite slots.
    rx, ry = 32, 96
    d.polygon([(rx + 1, ry + 12), (rx + 2, ry + 6),
               (rx + 6, ry + 3), (rx + 10, ry + 3),
               (rx + 14, ry + 8), (rx + 15, ry + 13),
               (rx + 11, ry + 15), (rx + 3, ry + 15)], fill=13, outline=13)
    d.rectangle((rx + 5, ry + 6, rx + 8, ry + 7), fill=7)
    d.rectangle((rx + 9, ry + 11, rx + 12, ry + 12), fill=7)

    mx, my = 48, 96
    d.rectangle((mx + 5, my + 8, mx + 11, my + 15), fill=7, outline=7)
    d.polygon([(mx, my + 8), (mx + 2, my + 4), (mx + 5, my + 2),
               (mx + 11, my + 2), (mx + 14, my + 5),
               (mx + 15, my + 9), (mx + 12, my + 11),
               (mx + 3, my + 11)], fill=8, outline=8)
    for x, y in ((mx + 5, my + 5), (mx + 11, my + 6), (mx + 8, my + 8)):
        d.rectangle((x, y, x + 1, y + 1), fill=7)

    # The supplied heart rows have seven columns in their tapered lower half.
    # Double those center columns to keep the requested design symmetric in 8px.
    heart_rows = (
        "O##OO##O",
        "#XX##XX#",
        "#XXXXXX#",
        "O#XXXX#O",
        "OO#XX#OO",
        "OOO##OOO",
    )
    for base_x, outline, fill in ((96, 8, 8), (104, 7, 0)):
        for row, pattern in enumerate(heart_rows):
            for col, marker in enumerate(pattern):
                if marker == "#":
                    d.point((base_x + col, 32 + row), fill=outline)
                elif marker == "X" and fill:
                    d.point((base_x + col, 32 + row), fill=fill)
    pixels = sheet.load()
    for y in range(24):
        for x in range(12):
            assert pixels[hx + x, hy + y] == pixels[hx + 23 - x, hy + y]
    for y in range(6):
        for x in range(4):
            assert pixels[96 + x, 32 + y] == pixels[103 - x, 32 + y]
    flat = list(sheet.getdata())
    return [flat[y * 128:(y + 1) * 128] for y in range(128)]


def main():
    source = CARTRIDGE.read_text(encoding="ascii")
    before, gfx_marker, after = source.partition("__gfx__\n")
    if not gfx_marker:
        raise ValueError("HeartPath.p8 has no graphics section")
    graphics, sound_marker, sound = after.partition("__sfx__\n")
    rows = graphics.strip().splitlines()
    if len(rows) != 128 or any(len(row) != 128 for row in rows):
        raise ValueError("Expected a 128x128 PICO-8 graphics sheet")
    gfx = [[int(char, 16) for char in row] for row in rows]
    with Image.open(SOURCE) as original:
        image = original.convert("RGB")
        import_animals(gfx, image)
    gfx = import_decorations(gfx)
    lines = ["".join(format(color, "x") for color in row) for row in gfx]
    CARTRIDGE.write_text(before + gfx_marker + "\n".join(lines) + "\n"
                         + (sound_marker + sound if sound_marker else ""), encoding="ascii")
    preview = Image.new("P", (128, 128))
    preview.putpalette([component for rgb in PALETTE for component in rgb]
                       + [0] * (256 * 3 - len(PALETTE) * 3))
    preview.putdata([color for row in gfx for color in row])
    preview.save(SHEET)
    print("Imported dog, bunny, cat, and duck pixels from source_animals.jpg")


if __name__ == "__main__":
    main()
