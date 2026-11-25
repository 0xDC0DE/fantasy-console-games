"""Build Turtles and Hare from levels.json, animals.png, and game.lua."""

import json
from pathlib import Path
import struct
import sys
import zlib

try:
    from PIL import Image
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "boxart" / ".deps"))
    from PIL import Image

from validate_levels import parse_wall


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "TurtlesAndHare.p8"
ROM = ROOT / "ROMS" / "PICO-8" / "TurtlesAndHare.p8.png"
PALETTE = (
    (168, 231, 46), (29, 43, 83), (126, 37, 83), (0, 135, 81),
    (171, 82, 54), (255, 0, 77), (255, 163, 0), (255, 236, 39),
    (0, 228, 54), (41, 173, 255), (131, 118, 156), (0, 181, 67),
    (6, 90, 181), (117, 70, 101), (255, 110, 89), (190, 18, 80),
)
COLOR_ID = {rgb: index for index, rgb in enumerate(PALETTE)}
SPRITE_DEST = ((0, 0), (32, 0), (64, 0), (96, 0), (0, 32), (32, 32))


def wall_mask(codes):
    result = 0
    for code in codes:
        a, b = parse_wall(code)
        if b == a + 1:
            r, c = divmod(a, 3)
            bit = r * 2 + c
        else:
            r, c = divmod(a, 3)
            bit = 6 + r * 3 + c
        result |= 1 << bit
    return result


def level_lua():
    levels = json.loads((HERE / "levels.json").read_text())
    if len(levels) != 48:
        raise ValueError(f"Expected 48 levels, found {len(levels)}")
    rows = []
    for level in levels:
        board = level["rows"]
        if len(board) != 3 or any(len(row) != 3 for row in board):
            raise ValueError(f"Bad board rows: {board}")
        rows.append('{' + ','.join(f'"{row.lower()}"' for row in board)
                    + f',{wall_mask(level["walls"])}' + '}')
    return 'level_data={' + ',\n'.join(rows) + '}\n'


def gfx_rows():
    image = Image.open(HERE / "animals.png").convert("RGBA")
    if image.size != (192, 32):
        raise ValueError("animals.png must stay 192x32")
    gfx = [[0] * 128 for _ in range(128)]
    for slot, (dest_x, dest_y) in enumerate(SPRITE_DEST):
        for y in range(32):
            for x in range(32):
                r, g, b, a = image.getpixel((slot * 32 + x, y))
                if a == 0:
                    continue
                if a != 255:
                    raise ValueError("Animal pixels must be opaque or transparent")
                rgb = (r, g, b)
                if rgb not in COLOR_ID:
                    raise ValueError(f"Off-palette animal pixel {rgb} at slot {slot}, {x},{y}")
                gfx[dest_y + y][dest_x + x] = COLOR_ID[rgb]
    return [''.join(f'{pixel:x}' for pixel in row) for row in gfx]


def sfx_row(speed, notes):
    output = f'00{speed:02x}0000'
    for pitch, wave, volume in notes:
        output += f'{pitch:02x}{wave:x}{volume:x}0'
    return output + '00000' * (32 - len(notes))


def sfx_rows():
    return [
        sfx_row(4, [(23, 0, 3), (26, 0, 2)]),
        sfx_row(5, [(20, 0, 4), (25, 0, 5), (30, 0, 4)]),
        sfx_row(6, [(27, 0, 4), (21, 0, 3)]),
        sfx_row(3, [(12, 1, 3), (10, 1, 2)]),
        sfx_row(8, [(20, 0, 4), (24, 0, 4), (27, 0, 5),
                    (32, 0, 5), (36, 0, 5), (39, 0, 6),
                    (36, 0, 5), (39, 0, 6)]),
    ]


def make_source():
    code = (HERE / "game.lua").read_text(encoding="ascii")
    if code.count("--LEVELS--") != 1:
        raise ValueError("game.lua needs one --LEVELS-- marker")
    code = code.replace("--LEVELS--", level_lua())
    gfx = gfx_rows()
    sound = sfx_rows()
    if len(code.encode("ascii")) >= 0x8000 - 0x4300:
        raise ValueError("Cartridge code does not fit")
    if any(len(row) != 128 for row in gfx):
        raise ValueError("Bad graphics row")
    if any(len(row) != 168 for row in sound):
        raise ValueError("Bad sound row")
    SOURCE.write_text("pico-8 cartridge // http://www.pico-8.com\nversion 41\n"
                      + "__lua__\n" + code + "\n__gfx__\n"
                      + "\n".join(gfx) + "\n__sfx__\n"
                      + "\n".join(sound) + "\n", encoding="ascii")
    return code, gfx, sound


def cartridge_bytes(code, gfx, sound):
    data = bytearray(160 * 205)
    for y, row in enumerate(gfx):
        for x in range(64):
            data[y * 64 + x] = int(row[x * 2], 16) | (int(row[x * 2 + 1], 16) << 4)
    for slot, row in enumerate(sound):
        offset = 0x3200 + slot * 68
        data[offset + 64:offset + 68] = bytes.fromhex(row[:8])
        for note in range(32):
            at = 8 + note * 5
            pitch = int(row[at:at + 2], 16)
            wave = int(row[at + 2], 16)
            volume = int(row[at + 3], 16)
            effect = int(row[at + 4], 16)
            data[offset + note * 2] = pitch | ((wave & 3) << 6)
            data[offset + note * 2 + 1] = ((wave & 4) >> 2) | ((wave & 8) << 4) | (volume << 1) | (effect << 4)
    encoded = code.encode("ascii")
    data[0x4300:0x4300 + len(encoded)] = encoded
    data[0x8000] = 41
    return data


def write_rom(data):
    label = Image.open(HERE / "concept-128.png").convert("RGBA")
    image = Image.new("RGBA", (160, 205), (29, 43, 83, 252))
    image.paste(label, (16, 24))
    pixels = bytearray(image.tobytes())
    for index, value in enumerate(data):
        at = index * 4
        pixels[at] = (pixels[at] & 252) | ((value >> 4) & 3)
        pixels[at + 1] = (pixels[at + 1] & 252) | ((value >> 2) & 3)
        pixels[at + 2] = (pixels[at + 2] & 252) | (value & 3)
        pixels[at + 3] = (pixels[at + 3] & 252) | ((value >> 6) & 3)
    ROM.parent.mkdir(parents=True, exist_ok=True)
    Image.frombytes("RGBA", (160, 205), bytes(pixels)).save(ROM)
    if not (HERE / "art.png").exists():
        (HERE / "art.png").write_bytes((HERE / "concept-128.png").read_bytes())


def main():
    code, gfx, sound = make_source()
    write_rom(cartridge_bytes(code, gfx, sound))
    print(f"Built {ROM} ({len(code.encode('ascii'))} code bytes)")


if __name__ == "__main__":
    main()
