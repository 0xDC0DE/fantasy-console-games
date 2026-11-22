"""Build the Stringer cartridge and matching MustardOS artwork.

Run: python3 fantasy-console-games/Stringer/build.py
Only Python's standard library is required. The game uses code, one coin
sprite, reference sounds, and original bead and coin sounds; map and music stay empty.
"""

from pathlib import Path
import struct
import zlib


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Stringer.p8"
OUTPUT = HERE.parent.parent / "ROMS" / "PICO-8" / "Stringer.p8.png"
ARTWORK = HERE.parent.parent / "boxart" / "PICO-8"
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


def label_image():
    pixels = bytearray([32, 34, 48, 252] * (WIDTH * HEIGHT))

    def pixel(x, y, color):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            at = (y * WIDTH + x) * 4
            pixels[at : at + 4] = bytes((*color, 252))

    def rect(x0, y0, x1, y1, color):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                pixel(x, y, color)

    def filled_circle(cx, cy, radius, color, outline):
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                distance = (x - cx) ** 2 + (y - cy) ** 2
                if distance <= radius**2:
                    pixel(x, y, outline if distance > (radius - 1)**2 else color)

    def rect_outline(x0, y0, x1, y1, color):
        rect(x0, y0, x1, y0, color)
        rect(x0, y1, x1, y1, color)
        rect(x0, y0, x0, y1, color)
        rect(x1, y0, x1, y1, color)

    glyphs = {
        "A": ("010", "101", "111", "101", "101"),
        "C": ("011", "100", "100", "100", "011"),
        "E": ("111", "100", "110", "100", "111"),
        "H": ("101", "101", "111", "101", "101"),
        "I": ("111", "010", "010", "010", "111"),
        "L": ("100", "100", "100", "100", "111"),
        "M": ("101", "111", "111", "101", "101"),
        "N": ("101", "111", "111", "111", "101"),
        "G": ("011", "100", "101", "101", "011"),
        "O": ("010", "101", "101", "101", "010"),
        "P": ("110", "101", "110", "100", "100"),
        "R": ("110", "101", "110", "101", "101"),
        "S": ("011", "100", "010", "001", "110"),
        "T": ("111", "010", "010", "010", "010"),
        "X": ("101", "101", "010", "101", "101"),
        "U": ("101", "101", "101", "101", "111"),
        "9": ("111", "101", "111", "001", "111"),
        "1": ("010", "110", "010", "010", "111"),
        "4": ("101", "101", "111", "001", "001"),
        "5": ("111", "100", "111", "001", "111"),
        "+": ("000", "010", "111", "010", "000"),
        "=": ("000", "111", "000", "111", "000"),
        " ": ("000", "000", "000", "000", "000"),
    }

    def text(message, x, y, scale, color):
        for char in message:
            for yy, row in enumerate(glyphs[char]):
                for xx, bit in enumerate(row):
                    if bit == "1":
                        rect(x + xx * scale, y + yy * scale,
                             x + (xx + 1) * scale - 1,
                             y + (yy + 1) * scale - 1, color)
            x += 4 * scale

    ink = (22, 25, 38)
    cream = (248, 243, 224)
    blue = (80, 184, 213)
    plum = (179, 130, 168)
    teal = (114, 191, 165)
    rect(0, 0, 159, 159, (215, 214, 209))
    rect(7, 7, 152, 153, ink)
    rect(13, 13, 146, 42, (54, 69, 91))
    text("STRINGER", 32, 26, 3, cream)
    rect(15, 49, 145, 137, (25, 28, 41))

    # The preview has opaque beads and ends at the last empty position.
    rect(24, 73, 134, 73, cream)
    rect(93, 106, 134, 106, cream)
    for y in range(74, 106):
        pixel(134, y, cream)
    filled_circle(36, 73, 9, ink, blue)
    rect(60, 64, 78, 82, ink)
    rect_outline(60, 64, 78, 82, plum)
    for step in range(19):
        half_width = step // 2
        rect(102-half_width, 81-step, 102+half_width, 81-step, ink)
    for step in range(10):
        pixel(102-step, 81-step*2, teal)
        pixel(102+step, 81-step*2, teal)
    rect(93, 63, 111, 63, teal)
    left, right, top, bottom = 93, 111, 97, 115
    rect(left, top, left+3, top, cream)
    rect(left, top, left, top+3, cream)
    rect(right-3, top, right, top, cream)
    rect(right, top, right, top+3, cream)
    rect(left, bottom, left+3, bottom, cream)
    rect(left, bottom-3, left, bottom, cream)
    rect(right-3, bottom, right, bottom, cream)
    rect(right, bottom-3, right, bottom, cream)
    rect(0, 160, 159, 204, (38, 42, 55))
    text("STRINGER", 32, 174, 3, cream)
    text("PATTERNS", 64, 193, 1, blue)
    return pixels


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


def artwork_pixels(cartridge_pixels, size):
    """Crop the cart label and scale it with nearest-neighbor pixels."""
    artwork = bytearray(size * size * 4)
    for y in range(size):
        source_y = 24 + (((2 * y + 1) * 128 - 1) // (2 * size))
        for x in range(size):
            source_x = 16 + (((2 * x + 1) * 128 - 1) // (2 * size))
            source = (source_y * WIDTH + source_x) * 4
            target = (y * size + x) * 4
            artwork[target : target + 4] = cartridge_pixels[source : source + 4]
    return artwork


def write_artwork(cartridge_pixels):
    for folder, size in (("box", 384), ("grid", 120)):
        destination = ARTWORK / folder
        destination.mkdir(parents=True, exist_ok=True)
        image = png_bytes(artwork_pixels(cartridge_pixels, size), size, size)
        for name in ("Stringer.p8.png", "Stringer.png"):
            (destination / name).write_bytes(image)


def main():
    data, code = cartridge_data()
    pixels = label_image()
    for index, value in enumerate(data):
        at = index * 4
        pixels[at] = (pixels[at] & 252) | ((value >> 4) & 3)
        pixels[at + 1] = (pixels[at + 1] & 252) | ((value >> 2) & 3)
        pixels[at + 2] = (pixels[at + 2] & 252) | (value & 3)
        pixels[at + 3] = (pixels[at + 3] & 252) | ((value >> 6) & 3)
    OUTPUT.write_bytes(png_bytes(pixels, WIDTH, HEIGHT))
    write_artwork(pixels)
    print(f"Built {OUTPUT} ({len(code)} code bytes)")
    print(f"Built matching box and grid artwork in {ARTWORK}")


if __name__ == "__main__":
    main()
