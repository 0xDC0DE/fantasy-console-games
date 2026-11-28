"""Build the Tweeklanken cartridge and matching MustardOS artwork.

Run: python3 fantasy-console-games/Tweeklanken/build.py
The builder uses Pillow from the workspace if it is not installed globally.
"""

from pathlib import Path
import re
import struct
import zlib
from make_sprites import RGB as PALETTE_RGB


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Tweeklanken.p8"
OUTPUT = HERE.parent.parent / "ROMS" / "PICO-8" / "Tweeklanken.p8.png"
ARTWORK = HERE.parent.parent / "boxart" / "PICO-8"
PREVIEW = HERE / "art.png"
WIDTH, HEIGHT = 160, 205
CODE_START = 0x4300
ROM_SIZE = 0x8000


def cartridge_data():
    source = SOURCE.read_text(encoding="ascii")
    lines = source.splitlines()
    if lines[0] != "pico-8 cartridge // http://www.pico-8.com":
        raise ValueError("Not a PICO-8 text cartridge")
    version = int(lines[1].removeprefix("version "))
    marker = lines.index("__lua__")
    code_end = next((i for i in range(marker + 1, len(lines))
                     if lines[i].startswith("__")), len(lines))
    code = ("\n".join(lines[marker + 1 : code_end]) + "\n").encode("ascii")
    if b"\0" in code or len(code) >= ROM_SIZE - CODE_START:
        raise ValueError("Source does not fit the uncompressed cartridge code area")
    data = bytearray(WIDTH * HEIGHT)
    if "__gfx__" in lines:
        gfx_start = lines.index("__gfx__") + 1
        gfx_end = next((i for i in range(gfx_start, len(lines))
                        if lines[i].startswith("__")), len(lines))
        rows = lines[gfx_start:gfx_end]
        if len(rows) > 128 or any(len(row) != 128 for row in rows):
            raise ValueError("Invalid PICO-8 graphics rows")
        for y, row in enumerate(rows):
            for x in range(64):
                left = int(row[x * 2], 16)
                right = int(row[x * 2 + 1], 16)
                data[y * 64 + x] = left | (right << 4)
    if "__sfx__" in lines:
        sfx_start = lines.index("__sfx__") + 1
        sfx_end = next((i for i in range(sfx_start, len(lines))
                        if lines[i].startswith("__")), len(lines))
        rows = lines[sfx_start:sfx_end]
        if len(rows) > 64 or any(len(row) != 168 for row in rows):
            raise ValueError("Invalid PICO-8 sound effect rows")
        for slot, row in enumerate(rows):
            offset = 0x3200 + slot * 68
            data[offset + 64 : offset + 68] = bytes.fromhex(row[:8])
            for note in range(32):
                start = 8 + note * 5
                pitch = int(row[start:start + 2], 16)
                waveform = int(row[start + 2], 16)
                volume = int(row[start + 3], 16)
                effect = int(row[start + 4], 16)
                if pitch > 63 or volume > 7 or effect > 7:
                    raise ValueError("Invalid PICO-8 sound effect note")
                data[offset + note * 2] = pitch | ((waveform & 3) << 6)
                data[offset + note * 2 + 1] = (
                    ((waveform & 4) >> 2) | ((waveform & 8) << 4)
                    | (volume << 1) | (effect << 4)
                )
    data[CODE_START : CODE_START + len(code)] = code
    data[ROM_SIZE] = version
    return data, code


def font_glyphs():
    code = SOURCE.read_text(encoding="ascii").split("font={", 1)[1].split("\n}", 1)[0]
    entries = re.findall(r'^\s*(\w+|\["[^"]+"\])=\{([\d,]+)\}', code, re.M)
    return {name.strip('["]'): [int(row) for row in rows.split(",")]
            for name, rows in entries}


def draw_text(draw, glyphs, message, x, y, color, scale=1):
    for index, char in enumerate(message):
        for row, bits in enumerate(glyphs.get(char, [0] * 7)):
            for col in range(5):
                if bits & (1 << (4 - col)):
                    px = x + (index * 6 + col) * scale
                    py = y + row * scale
                    draw.rectangle((px, py, px + scale - 1, py + scale - 1), fill=color)


def centered_text(draw, glyphs, message, y, color, scale, width):
    x = (width - (len(message) * 6 - 1) * scale) // 2
    draw_text(draw, glyphs, message, x, y, color, scale)


def label_image(data):
    """A label showing the large lowercase nose puzzle."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        import sys
        sys.path.insert(0, str(HERE.parent.parent / "boxart" / ".deps"))
        from PIL import Image, ImageDraw
    palette = PALETTE_RGB
    im = Image.new("RGBA", (WIDTH, HEIGHT), (*palette[1], 252))
    d = ImageDraw.Draw(im)
    glyphs = font_glyphs()
    centered_text(d, glyphs, "tweeklanken", 12, palette[13], 2, WIDTH)
    draw_text(d, glyphs, "8", 148, 14, palette[14])
    centered_text(d, glyphs, "n__s", 41, palette[10], 3, WIDTH)
    for band in range(8):
        y = 143 - band * 9
        d.rectangle((149, y, 154, y + 6), fill=palette[(8, 9, 10, 11, 12, 13, 14)[band % 7]])
    # Show the editable nose picture at twice its game size.
    for sy in range(32):
        for sx in range(32):
            gx = sx  # slot 0, first column
            gy = sy  # first row
            packed = data[gy * 64 + gx // 2]
            color = (packed >> (4 * (gx % 2))) & 15
            d.rectangle((48 + sx * 2, 59 + sy * 2,
                         49 + sx * 2, 60 + sy * 2), fill=palette[color])
    for x, pair in ((30, "oe"), (80, "eu"), (130, "ei")):
        draw_text(d, glyphs, pair, x - 11, 138,
                  palette[7 if pair == "eu" else 6], 2)
    for x, y in ((78, 129), (82, 129), (79, 130), (81, 130), (80, 131)):
        d.point((x, y), fill=palette[10])
    d.rectangle((0, 160, 159, 204), fill=palette[2])
    centered_text(d, glyphs, "tweeklanken", 177, palette[7], 1, WIDTH)
    return bytearray(im.tobytes())


def write_preview(data):
    """Keep the editable gameplay thumbnail in step with the cartridge font."""
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (128, 128), PALETTE_RGB[1])
    d = ImageDraw.Draw(im)
    glyphs = font_glyphs()
    centered_text(d, glyphs, "tweeklanken", 2, PALETTE_RGB[13], 1, 128)
    draw_text(d, glyphs, "8", 121, 2, PALETTE_RGB[14])
    for band in range(8):
        y = 113 - band * 5
        d.rectangle((119, y, 124, y + 3),
                    fill=PALETTE_RGB[(8, 9, 10, 11, 12, 13, 14)[band % 7]])
    centered_text(d, glyphs, "n__s", 18, PALETTE_RGB[7], 2, 128)
    for sy in range(32):
        for sx in range(32):
            packed = data[sy * 64 + sx // 2]
            color = (packed >> (4 * (sx % 2))) & 15
            d.point((48 + sx, 43 + sy), fill=PALETTE_RGB[color])
    for x, pair in ((26, "oe"), (64, "eu"), (102, "ei")):
        draw_text(d, glyphs, pair, x - 11, 96,
                  PALETTE_RGB[7 if pair == "eu" else 6], 2)
    for x, y in ((62, 89), (66, 89), (63, 90), (65, 90), (64, 91)):
        d.point((x, y), fill=PALETTE_RGB[10])
    centered_text(d, glyphs, "a: kies", 119, PALETTE_RGB[6], 1, 128)
    im.resize((512, 512), Image.Resampling.NEAREST).save(PREVIEW)


def png_chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def png_bytes(pixels, width, height):
    rows = bytearray()
    for y in range(height):
        rows.append(0)  # PNG filter: none
        rows.extend(pixels[y * width * 4 : (y + 1) * width * 4])
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(rows, 9))
        + png_chunk(b"IEND", b"")
    )


def write_artwork():
    from PIL import Image
    preview = Image.open(PREVIEW).convert("RGB")
    for folder, size in (("box", 384), ("grid", 120)):
        destination = ARTWORK / folder
        destination.mkdir(parents=True, exist_ok=True)
        image = preview.resize((size, size), Image.Resampling.NEAREST)
        for name in ("Tweeklanken.p8.png", "Tweeklanken.png"):
            image.save(destination / name)


def main():
    data, code = cartridge_data()
    pixels = label_image(data)
    for index, value in enumerate(data):
        at = index * 4
        pixels[at] = (pixels[at] & 252) | ((value >> 4) & 3)
        pixels[at + 1] = (pixels[at + 1] & 252) | ((value >> 2) & 3)
        pixels[at + 2] = (pixels[at + 2] & 252) | (value & 3)
        pixels[at + 3] = (pixels[at + 3] & 252) | ((value >> 6) & 3)
    OUTPUT.write_bytes(png_bytes(pixels, WIDTH, HEIGHT))
    write_preview(data)
    write_artwork()
    print(f"Built {OUTPUT} ({len(code)} code bytes)")
    print(f"Built matching box and grid artwork in {ARTWORK}")


if __name__ == "__main__":
    main()
