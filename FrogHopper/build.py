"""Build Frog Hopper's TIC-80 cartridge and its pixel-art cover.

Uses the selected frames from the supplied 32x32 frog sheets. Pillow is loaded
from the workspace's existing boxart dependency directory when needed.
"""

from pathlib import Path
from math import pi, sin
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.path.insert(0, str(ROOT / "boxart" / ".deps"))
    from PIL import Image, ImageDraw, ImageFont

SOURCE = HERE / "FrogHopper.lua"
CART = HERE / "FrogHopper.tic"
ART = HERE / "art.png"
SHEETS = HERE / "frog_spritesheets"

# Index 0 is the transparent sprite key. The remaining colors serve both the
# scenery and the green/purple source artwork.
PALETTE = [
    (0, 0, 0), (19, 42, 58), (39, 108, 132), (91, 164, 174),
    (225, 244, 224), (39, 92, 56), (93, 160, 83), (160, 214, 103),
    (70, 87, 111), (128, 147, 163), (242, 211, 104),
    (0, 88, 4), (64, 188, 70), (100, 230, 105),
    (97, 31, 98), (209, 68, 230),
]

# The guide marks columns 0-7 as idle/croak, 9-10 as jumps, and rows 8-10 as reactions.
# The supplied reference crop is row 1, columns 0-5: angled idle and croak.
# One 24x24 crop retains the source frame's bottom baseline and its full shape.
FRAMES = [
    ("green", 1, 0), ("green", 1, 1),
    ("green", 1, 3), ("green", 1, 4), ("green", 1, 5),
    ("green", 0, 9), ("green", 1, 9), ("green", 2, 9),
    ("green", 3, 9), ("green", 9, 0), ("green", 10, 0),
    ("green", 8, 2), ("green", 8, 3), ("green", 8, 4),
    ("purple", 1, 0), ("purple", 1, 0), ("green", 1, 0),
]


def color_index(rgba, frog):
    r, g, b, a = rgba
    if a < 128:
        return 0
    if max(r, g, b) < 25:
        return 1  # dark visible outline, distinct from the transparent key
    if frog == "green":
        if r > 145 and g > 225:
            return 4  # pale croak belly
        if g < 150:
            return 11
        if g < 215:
            return 12
        return 13
    if r > 210 and g > 140:
        return 4
    if r < 150:
        return 14
    return 15


def make_atlas():
    atlas = [[0] * 128 for _ in range(128)]
    sheets = {
        name: Image.open(SHEETS / f"frog_{name}_spritesheet.png").convert("RGBA")
        for name in ("green", "purple")
    }
    for index, (name, row, col) in enumerate(FRAMES):
        source = sheets[name]
        x0, y0 = col * 32 + 4, row * 32 + 8
        target_x, target_y = (index % 5) * 24, (index // 5) * 24
        for dy in range(24):
            for dx in range(24):
                atlas[target_y + dy][target_x + dx] = color_index(
                    source.getpixel((x0 + dx, y0 + dy)), name
                )

        if index in (15, 16):
            # Speaking pose: keep the angled resting frog and replace its
            # three-pixel mouth with a compact two-by-two open mouth.
            atlas[target_y + 17][target_x + 13] = 15 if name == "purple" else 13
            for mouth_y in (17, 18):
                for mouth_x in (14, 15):
                    atlas[target_y + mouth_y][target_x + mouth_x] = 1

    def place_small(index, pixels, convert):
        x0, y0 = (index % 5) * 24, (index // 5) * 24
        for y in range(pixels.height):
            for x in range(pixels.width):
                atlas[y0 + y][x0 + x] = convert(pixels.getpixel((x, y)), x, y)

    # The bubble uses the supplied artwork, reduced to readable native pixels.
    mini_frog = sheets["green"].crop((4, 40, 28, 64))
    mini_frog = mini_frog.crop(mini_frog.getchannel("A").getbbox()).resize(
        (14, 11), Image.Resampling.NEAREST
    )
    place_small(17, mini_frog, lambda rgba, x, y: color_index(rgba, "green"))

    heart = Image.open(HERE / "hearts.png").convert("RGB").crop(
        (178, 172, 316, 312)
    ).resize((10, 10), Image.Resampling.NEAREST)
    def heart_ink(rgb, x, y):
        r, g, b = rgb
        if min(rgb) > 180:
            return 4
        if r > 160 and g < 100:
            return 15
        if r > 40 and g < 90:
            return 14
        return 0
    place_small(18, heart, heart_ink)

    crown = Image.open(HERE / "crown.png").convert("RGB").crop(
        (272, 288, 528, 464)
    ).resize((16, 11), Image.Resampling.NEAREST)
    def crown_ink(rgb, x, y):
        r, g, b = rgb
        if (x, y) in ((3, 6), (4, 6), (5, 5)):
            return 4
        if max(rgb) < 60:
            return 1
        if r > 170 and g > 115 and b < 90:
            return 10
        if r > 70 and g > 45 and b < 70:
            return 8
        # Clear the stock-image watermark from inside the gold shape.
        if y >= 5 and 1 <= x <= 14:
            return 10
        return 0
    place_small(19, crown, crown_ink)

    smiley = Image.open(HERE / "smiley.png").convert("RGB").crop(
        (43, 42, 217, 218)
    ).resize((12, 12), Image.Resampling.NEAREST)
    dark = {
        (x, y) for y in range(12) for x in range(12)
        if max(smiley.getpixel((x, y))) < 100
    }
    # Preserve the supplied face; make the yellow area outside its outline
    # transparent so it sits cleanly inside the speech bubble.
    outside = set()
    todo = [(x, y) for x in range(12) for y in (0, 11)]
    todo += [(x, y) for y in range(12) for x in (0, 11)]
    while todo:
        x, y = todo.pop()
        if not (0 <= x < 12 and 0 <= y < 12) or (x, y) in dark or (x, y) in outside:
            continue
        outside.add((x, y))
        todo.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    place_small(20, smiley, lambda rgb, x, y:
                1 if (x, y) in dark else 0 if (x, y) in outside else 10)

    def fish_ink(rgba, kind):
        r, g, b, a = rgba
        if a < 128:
            return 0
        if max(r, g, b) < 75:
            return 1
        if min(r, g, b) > 185:
            return 4
        if b > r + 35 and b > g + 12:
            return 3
        if kind == "green":
            if g > 185 and g > r * 1.3:
                return 13
            if g > 95 and g > r:
                return 12
            return 11
        if r > 185 and g > 100:
            return 10
        if r > 95 and g > 40:
            return 8
        return 1

    # Four remaining 24x24 atlas slots hold low/high poses of both fish.
    for kind, filename, first_index in (
        ("green", "fish-sprites2.png", 21),
        ("gold", "fish-sprites3.png", 23),
    ):
        sheet = Image.open(HERE / filename).convert("RGBA")
        frame_width = sheet.width // 3
        for offset, column in enumerate((0, 2)):
            frame = sheet.crop((column * frame_width, 0,
                                (column + 1) * frame_width, sheet.height))
            frame = frame.crop((200, 270, 520, 530)).resize(
                (24, 20), Image.Resampling.NEAREST
            )
            place_small(first_index + offset, frame,
                        lambda rgba, x, y, kind=kind: fish_ink(rgba, kind))
    return atlas


def sprite_bytes(atlas):
    output = bytearray(8192)
    for tile_y in range(16):
        for tile_x in range(16):
            tile = tile_y * 16 + tile_x
            for py in range(8):
                for px in range(0, 8, 2):
                    lo = atlas[tile_y * 8 + py][tile_x * 8 + px]
                    hi = atlas[tile_y * 8 + py][tile_x * 8 + px + 1]
                    output[tile * 32 + py * 4 + px // 2] = lo | (hi << 4)
    return bytes(output)


def chunk(kind, payload):
    if len(payload) > 65536:
        raise ValueError(f"TIC-80 chunk {kind} is too large")
    return bytes((kind,)) + (len(payload) % 65536).to_bytes(2, "little") + b"\0" + payload


def sound_bytes():
    """Six native TIC-80 effects with brief, tapered volume envelopes.

    Each step stores an inverted 4-bit volume beneath its waveform index.
    Leaving the wave bank empty makes TIC-80 play noise, so build_cart also
    installs the pitched waves used here.
    """
    data = bytearray(7 * 66)
    effects = (
        (0, (3, 5, 6, 5, 3, 1)),
        (1, (4, 7, 9, 10, 10, 9, 8, 7, 6, 5, 3, 1)),
        (0, (3, 5, 7, 8, 8, 8, 7, 7, 6, 5, 4, 3, 2, 1)),
        (1, (3, 5, 7, 8, 8, 7, 7, 6, 5, 4, 3, 2, 1, 1)),
        (0, (1, 5, 7, 4, 1)),
        (0, (3, 5, 7, 6, 4, 2, 1)),
        (0, (5, 8, 8, 6, 4, 2, 1)),
    )
    for slot, (wave, levels) in enumerate(effects):
        for step in range(30):
            level = levels[step] if step < len(levels) else 0
            data[slot * 66 + step * 2] = (wave << 4) | (15 - level)
    return bytes(data)


def waveform_bytes():
    """A rounded sine and a gentle triangle, 32 four-bit samples each."""
    sine = [round(7.5 + 7.5 * sin(2 * pi * i / 32)) for i in range(32)]
    triangle = [round(7.5 + 7.5 * (1 - abs(i - 8) / 8)) for i in range(16)]
    triangle += [round(7.5 - 7.5 * (1 - abs(i - 24) / 8)) for i in range(16, 32)]
    samples = sine + triangle
    return bytes(samples[i] | (samples[i + 1] << 4) for i in range(0, 64, 2))


def build_cart(atlas):
    code = SOURCE.read_bytes()
    if len(code) > 65536:
        raise ValueError("Lua code exceeds TIC-80's 64 KiB code limit")
    # Native TIC-80 chunks: 1 = tiles, 5 = Lua, 9 = SFX,
    # 10 = waveform bank, 12 = palette.
    CART.write_bytes(
        chunk(1, sprite_bytes(atlas))
        + chunk(9, sound_bytes())
        + chunk(10, waveform_bytes())
        + chunk(12, bytes(component for rgb in PALETTE for component in rgb))
        + chunk(5, code)
    )


def build_art(atlas):
    scale = 2
    im = Image.new("RGB", (240, 136), PALETTE[2])
    draw = ImageDraw.Draw(im)
    c = PALETTE
    draw.rectangle((0, 0, 239, 44), fill=c[7])
    draw.rectangle((0, 0, 239, 10), fill=c[6])
    draw.rectangle((0, 45, 239, 59), fill=c[3])
    draw.line((0, 45, 239, 45), fill=c[4])
    for y in range(66, 134, 13):
        for x in range(0, 240, 31):
            draw.line((x, y, x + 9, y), fill=c[3])
            draw.point((x + 14, y + 2), fill=c[4])
    for i in range(24):
        x = i * 11 + (i * 7) % 5
        h = 3 + (i * 3) % 5
        if x < 76 or x > 115:
            draw.line((x, 43, x - 2, 43 - h), fill=c[5])
            draw.line((x + 1, 43, x + 2, 42 - h), fill=c[5])
            draw.line((x + 3, 43, x + 3, 40 - h), fill=c[6])
    for x in (4, 27, 207, 230):
        draw.line((x + 2, 43, x + 2, 31), fill=c[5])
        draw.line((x + 2, 38, x - 1, 35), fill=c[6])
        draw.line((x + 2, 40, x + 5, 36), fill=c[6])
        draw.point((x + 1, 30), fill=c[15])
        draw.point((x + 3, 30), fill=c[15])
        draw.point((x + 2, 29), fill=c[4])
    for x in (7, 228):
        for j in (0, 1):
            sx = x + j * 5
            draw.line((sx, 67, sx + 1, 48 - j * 2), fill=c[5])
            draw.line((sx, 59, sx - 4, 55), fill=c[11])
            draw.line((sx, 62, sx + 4, 57), fill=c[11])
            draw.rectangle((sx, 43 - j * 2, sx + 2, 50 - j * 2), fill=c[10])
    draw.ellipse((117, 115, 135, 121), fill=c[5])
    draw.ellipse((119, 114, 133, 118), fill=c[7])
    draw.line((120, 118, 131, 116), fill=c[11])
    draw.line((134, 115, 137, 113), fill=c[5])
    for i in range(6):
        x = round(18 + i * 204 / 5)
        draw.ellipse((x - 16, 88, x + 16, 96), fill=c[1])
        draw.ellipse((x - 14, 83, x + 14, 93), fill=c[8])
        draw.ellipse((x - 12, 81, x + 12, 89), fill=c[9])
        draw.line((x - 9, 84, x, 83), fill=c[10])
    for index, x, bottom in ((0, 18, 88), (14, 95, 42)):
        sx, sy = (index % 5) * 24, (index // 5) * 24
        for dy in range(24):
            for dx in range(24):
                ink = atlas[sy + dy][sx + dx]
                if ink:
                    im.putpixel((x - 12 + dx, bottom - 24 + dy), c[ink])
    # The selector is a 7x4 V above the second stone.
    vx = round(18 + 204 / 5)
    for dx, dy in ((-3, 0), (3, 0), (-2, 1), (2, 1),
                   (-1, 2), (1, 2), (0, 3)):
        draw.point((vx + dx, 66 + dy), fill=c[10])
    draw.rectangle((112, 5, 175, 30), fill=c[1])
    draw.rectangle((111, 7, 177, 28), fill=c[1])
    draw.rectangle((113, 6, 174, 29), fill=c[4])
    draw.rectangle((111, 8, 176, 27), fill=c[4])
    draw.polygon(((111, 17), (111, 27), (101, 25)), fill=c[1])
    draw.rectangle((110, 20, 112, 25), fill=c[4])
    draw.polygon(((112, 19), (112, 25), (104, 25)), fill=c[4])
    draw.text((122, 15), "HOP", fill=c[1])
    for dx in range(11):
        draw.point((144 + dx, 18), fill=c[1])
    for step in range(1, 4):
        draw.point((154 - step, 18 - step), fill=c[1])
        draw.point((154 - step, 18 + step), fill=c[1])
    draw.text((161, 15), "3", fill=c[1])
    draw.text((4, 0), "MODE: COUNT HOPS", fill=c[1])
    draw.text((212, 0), "EASY", fill=c[1])
    draw.rectangle((0, 123, 239, 135), fill=c[1])
    draw.text((24, 126), "LEFT/RIGHT:CHOOSE X:HOP O:MENU", fill=c[4])
    im.resize((240 * scale, 136 * scale), Image.Resampling.NEAREST).save(ART)


def main():
    atlas = make_atlas()
    build_cart(atlas)
    build_art(atlas)
    print(f"Built {CART.name} and {ART.name} ({len(FRAMES)} frog frames, 4 bubble icons and 4 fish poses)")


if __name__ == "__main__":
    main()
