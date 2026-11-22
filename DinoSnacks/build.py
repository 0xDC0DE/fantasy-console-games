"""Build the Dino Snacks cartridge and matching MustardOS artwork.

Run: python3 homemade/DinoSnacks/build.py
Only Python's standard library is required. The game uses original code, sprites, and sound effects; map and music stay empty.
"""

from pathlib import Path
import struct
import zlib


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "DinoSnacks.p8"
OUTPUT = HERE.parent.parent / "ROMS" / "PICO-8" / "DinoSnacks.p8.png"
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


def label_image(data):
    """Draw cartridge art using the actual dinosaur sprites."""
    sky=(173,222,211)
    dark=(29,43,83)
    grass=(0,135,81)
    pale=(255,241,232)
    yellow=(255,236,39)
    palette=(
        (0,0,0),(29,43,83),(117,70,101),(0,135,81),
        (0,181,67),(95,87,79),(194,195,199),(255,241,232),
        (255,0,77),(255,110,89),(255,236,39),(0,228,54),
        (41,173,255),(131,118,156),(255,157,129),(255,204,170)
    )
    pixels=bytearray([*sky,252]*(WIDTH*HEIGHT))

    def pixel(x,y,color):
        if 0<=x<WIDTH and 0<=y<HEIGHT:
            at=(y*WIDTH+x)*4
            pixels[at:at+4]=bytes((*color,252))

    def rect(x0,y0,x1,y1,color):
        for yy in range(y0,y1+1):
            for xx in range(x0,x1+1):
                pixel(xx,yy,color)

    glyphs={
      "A":("010","101","111","101","101"),
      "C":("011","100","100","100","011"),
      "D":("110","101","101","101","110"),
      "I":("111","010","010","010","111"),
      "K":("101","101","110","101","101"),
      "N":("101","111","111","111","101"),
      "O":("010","101","101","101","010"),
      "P":("110","101","110","100","100"),
      "S":("011","100","010","001","110"),
      "-":("000","000","111","000","000"),
      " ":("000","000","000","000","000"),
    }

    def text(message,x,y,scale,color):
        for char in message:
            for yy,row in enumerate(glyphs[char]):
                for xx,bit in enumerate(row):
                    if bit=="1":
                        rect(x+xx*scale,y+yy*scale,
                             x+(xx+1)*scale-1,y+(yy+1)*scale-1,color)
            x+=4*scale

    def sprite(sprite_id,x,y):
        sx=(sprite_id%16)*8
        sy=(sprite_id//16)*8
        for yy in range(32):
            for xx in range(32):
                source_x=sx+xx*24//32
                source_y=sy+yy*24//32
                offset=source_y*64+source_x//2
                byte=data[offset]
                color=(byte&15) if source_x%2==0 else (byte>>4)
                if color:
                    pixel(x+xx,y+yy,palette[color])

    rect(5,5,154,199,dark)
    rect(10,10,149,154,sky)
    rect(10,116,149,154,grass)
    rect(15,18,144,52,dark)
    text("DINO SNACKS",15,28,3,pale)
    # Three distinct dinosaur portraits from the playable sprite sheet.
    for sprite_id,x in ((0,18),(51,64),(102,110)):
        rect(x-2,72,x+33,113,pale)
        rect(x,74,x+31,111,(124,205,179))
        sprite(sprite_id,x,76)
    for x in (55,73,91):
        rect(x,135,x+8,143,dark)
        rect(x+2,136,x+6,141,yellow)
    rect(0,160,159,204,dark)
    text("DINO SNACKS",15,169,3,pale)
    text("D-PAD",50,191,2,yellow)
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
        for name in ("DinoSnacks.p8.png", "DinoSnacks.png"):
            (destination / name).write_bytes(image)


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
    write_artwork(pixels)
    print(f"Built {OUTPUT} ({len(code)} code bytes)")
    print(f"Built matching box and grid artwork in {ARTWORK}")


if __name__ == "__main__":
    main()
