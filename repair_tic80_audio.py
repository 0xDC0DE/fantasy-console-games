"""Rebuild converted TIC-80 effects from the original PICO-8 note data."""

from pathlib import Path
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
GAMES = ("MathSplit", "ColorMix", "ShapeSum")
MARKER = b"-- Repaired PICO-8 sound playback"
WAVE_SLOTS = {0: 60, 1: 61, 3: 62, 5: 63}
PITCH_SHIFT = 24
TIME_SCALE = 2  # The Stringer timing the user called "Much better".


def chunks(cart):
    offset = 0
    while offset < len(cart):
        if offset + 4 > len(cart):
            raise ValueError("Truncated TIC-80 chunk header")
        kind = cart[offset] & 31
        size = int.from_bytes(cart[offset + 1 : offset + 3], "little")
        if kind == 5 and size == 0:
            size = 65536
        end = offset + 4 + size
        if end > len(cart):
            raise ValueError("Truncated TIC-80 chunk data")
        yield kind, offset, end
        offset = end


def sound_events(source):
    text = source.read_text()
    lua = text.split("__lua__\n", 1)[1].split("__gfx__", 1)[0]
    used_ids = sorted({int(n) for n in re.findall(r"\bsfx\((\d+)", lua)})
    lines = text.split("__sfx__\n", 1)[1].splitlines()
    events = {}
    for sound_id in used_ids:
        line = lines[sound_id]
        speed = int(line[2:4], 16)
        notes = []
        for index in range(32):
            sample = line[8 + index * 5 : 13 + index * 5]
            if len(sample) != 5:
                raise ValueError(f"Incomplete SFX {sound_id} in {source}")
            pitch = int(sample[:2], 16) + PITCH_SHIFT
            wave = int(sample[2], 16)
            volume = int(sample[3], 16)
            if not volume:
                continue
            if pitch > 95 or wave not in WAVE_SLOTS:
                raise ValueError(f"Unsupported note in SFX {sound_id} of {source}")
            frame = (index * speed * TIME_SCALE + 1) // 2
            end_frame = ((index + 1) * speed * TIME_SCALE + 1) // 2
            notes.append((frame, WAVE_SLOTS[wave], pitch, max(1, end_frame - frame), min(15, volume * 2)))
        events[sound_id] = notes
    return events


def lua_playback(events):
    rows = [
        f"{MARKER.decode()} (pitch +{PITCH_SHIFT}, time x{TIME_SCALE})",
        "__sfx=sfx",
        "local sound_notes={",
    ]
    for sound_id, notes in events.items():
        values = ",".join("{" + ",".join(map(str, note)) + "}" for note in notes)
        rows.append(f" [{sound_id}]={{{values}}},")
    rows.extend(
        [
            "}",
            "local sound_queue=nil",
            "local sound_frame=0",
            "local sound_index=1",
            "local function sound_step()",
            " while sound_queue and sound_index<=#sound_queue do",
            "  local event=sound_queue[sound_index]",
            "  if event[1]>sound_frame then break end",
            "  __sfx(event[2],event[3],event[4],0,event[5])",
            "  sound_index=sound_index+1",
            " end",
            " if sound_queue and sound_index>#sound_queue then sound_queue=nil end",
            "end",
            "function sfx(n,channel,offset)",
            " if n<0 then",
            "  sound_queue=nil",
            "  __sfx(-1,nil,nil,0)",
            "  return",
            " end",
            " sound_queue=sound_notes[n]",
            " sound_frame=0",
            " sound_index=1",
            " sound_step()",
            "end",
            "function repaired_sound_tick()",
            " if sound_queue then",
            "  sound_frame=sound_frame+1",
            "  sound_step()",
            " end",
            "end",
            "",
        ]
    )
    return ("\n".join(rows) + "\n").encode()


def repair(cart, source):
    sections = list(chunks(cart))
    code_chunks = [(start, end) for kind, start, end in sections if kind == 5]
    sample_chunks = [(start, end) for kind, start, end in sections if kind == 9]
    if len(code_chunks) != 1 or len(sample_chunks) != 1:
        raise ValueError("Expected one code chunk and one SFX chunk")
    code_start, code_end = code_chunks[0]
    sound_start, _ = sample_chunks[0]
    code = cart[code_start + 4 : code_end].rstrip(b"\0")
    wrapper_start = code.index(MARKER if MARKER in code else b"__sfx=sfx\n")
    wrapper_end = code.index(b"function stat(", wrapper_start)
    code = code[:wrapper_start] + lua_playback(sound_events(source)) + code[wrapper_end:]
    if b"function TIC()\n repaired_sound_tick()\n" not in code:
        code = code.replace(b"function TIC()\n", b"function TIC()\n repaired_sound_tick()\n", 1)
    if source.stem == "ShapeSum" and b"function deli(" not in code:
        # PICO-8 DELI removes by index; the converter only supplies DEL.
        helper = b"function deli(t,i)\n return table.remove(t,i or #t)\nend\n\n"
        code = code.replace(b"function del(t,a)\n", helper + b"function del(t,a)\n", 1)
    if len(code) >= 65536:
        raise ValueError("TIC-80 code chunk is too large")

    data = bytearray(cart)
    for wave, slot in WAVE_SLOTS.items():
        effect = sound_start + 4 + slot * 66
        for step in range(30):
            data[effect + step * 2] = wave << 4
            data[effect + step * 2 + 1] = 0
        data[effect + 60 : effect + 66] = bytes(6)
    data[code_start + 1 : code_start + 3] = len(code).to_bytes(2, "little")
    return bytes(data[: code_start + 4]) + code + bytes(data[code_end:])


def main(names):
    for name in names:
        if name not in GAMES:
            raise SystemExit(f"Unknown game: {name}")
        folder = ROOT / "homemade" / name
        cart_path = folder / f"{name}.tic"
        before = cart_path.read_bytes()
        after = repair(before, folder / f"{name}.p8")
        if after != before:
            backup = folder / f"{name}-before-audio.tic"
            if not backup.exists() and MARKER not in before:
                shutil.copy2(cart_path, backup)
            cart_path.write_bytes(after)
            print(f"Rebuilt TIC-80 SFX playback: {cart_path}")
        else:
            print(f"Already repaired: {cart_path}")


if __name__ == "__main__":
    main(sys.argv[1:] or GAMES)
