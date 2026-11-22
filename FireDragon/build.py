"""Build the simplified Dragon Fury cartridge from its Lua source."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
ORIGINAL = HERE / "dragon_fury-original.tic"
SOURCE = HERE / "dragon_fury.lua"
OUTPUT = HERE / "dragon_fury.tic"


def build():
    cart = ORIGINAL.read_bytes()
    code = SOURCE.read_bytes()
    if len(code) > 65536:
        raise ValueError(f"TIC-80 Lua code is {len(code)} bytes; limit is 65536")

    pos = 0
    chunks = []
    found = False
    while pos < len(cart):
        if pos + 4 > len(cart):
            raise ValueError("Truncated cartridge chunk header")
        kind = cart[pos] & 31
        size = int.from_bytes(cart[pos + 1:pos + 3], "little")
        if kind == 5 and size == 0:
            size = 65536
        end = pos + 4 + size
        if end > len(cart):
            raise ValueError("Truncated cartridge chunk")
        if kind == 5:
            if found:
                raise ValueError("Expected one code chunk")
            header = bytearray(cart[pos:pos + 4])
            header[1:3] = (len(code) % 65536).to_bytes(2, "little")
            chunks.append(bytes(header) + code)
            found = True
        else:
            chunks.append(cart[pos:end])
        pos = end
    if not found:
        raise ValueError("Missing code chunk")
    OUTPUT.write_bytes(b"".join(chunks))
    print(f"Built {OUTPUT} ({len(code)} Lua bytes)")


if __name__ == "__main__":
    build()
