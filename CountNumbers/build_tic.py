"""Build a TIC-80 version using the existing PICO-8 compatibility shim.

The MathSplit port supplies the shim and palette. Game code, sprites, and
sound events come from CountNumbers.p8.
"""

from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "CountNumbers.p8"
TEMPLATE = ROOT / "homemade" / "MathSplit" / "MathSplit.tic"
OUTPUT = HERE / "CountNumbers.tic"
sys.path.insert(0, str(HERE.parent))
from repair_tic80_audio import repair


def chunks(data):
    offset = 0
    while offset < len(data):
        kind = data[offset] & 31
        size = int.from_bytes(data[offset + 1:offset + 3], "little")
        if kind == 5 and size == 0:
            size = 65536
        end = offset + 4 + size
        if end > len(data):
            raise ValueError("Truncated TIC-80 cartridge")
        yield kind, data[offset:offset + 4], data[offset + 4:end]
        offset = end


def lua_code(source, template):
    game = source.split("__lua__\n", 1)[1].split("__gfx__", 1)[0]
    game = game.replace("!=", "~=")
    game = re.sub(r"\b(\w+)([+-])=(\d+)",
                  lambda m: f"{m[1]}={m[1]}{m[2]}{m[3]};", game)
    game = game.replace("x+=flr", "x=x+flr")
    game = game.replace("y+=dy or 0", "y=y+(dy or 0)")
    if re.search(r"\b\w+\s*[+-]=", game):
        raise ValueError("Untranslated PICO-8 assignment")
    shim = template.split("-- Add pico-8 cart below!", 1)[0]
    aliases = """-- Add pico-8 cart below!
flr=math.floor
rnd=function(n) return math.random()*(n or 1) end
srand=math.randomseed
min=math.min
max=math.max
"""
    code = (shim + aliases + game).encode("utf-8")
    if len(code) >= 65536:
        raise ValueError("TIC-80 code chunk is too large")
    return code


def sprite_data(source):
    rows = source.split("__gfx__\n", 1)[1].split("__sfx__", 1)[0].splitlines()
    if len(rows) > 128 or any(len(row) != 128 for row in rows):
        raise ValueError("Invalid PICO-8 sprite sheet")
    rows += ["0" * 128] * (128 - len(rows))
    data = bytearray(8192)
    for y in range(128):
        for x in range(128):
            tile = (y // 8) * 16 + x // 8
            offset = tile * 32 + (y % 8) * 4 + (x % 8) // 2
            value = int(rows[y][x], 16)
            if x % 2:
                data[offset] |= value << 4
            else:
                data[offset] |= value
    return bytes(data)


def main():
    source = SOURCE.read_text(encoding="ascii")
    template = TEMPLATE.read_bytes()
    parts = []
    for kind, header, payload in chunks(template):
        if kind == 1:
            payload = sprite_data(source)
        elif kind == 5:
            payload = lua_code(source, payload.decode("utf-8"))
        if len(payload) >= 65536:
            raise ValueError("TIC-80 chunk exceeds size limit")
        header = bytes((header[0],)) + len(payload).to_bytes(2, "little") + header[3:4]
        parts.append(header + payload)
    OUTPUT.write_bytes(repair(b"".join(parts), SOURCE))
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    main()
