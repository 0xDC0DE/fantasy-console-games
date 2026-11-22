"""Repair Stringer's converted TIC-80 sounds from the PICO-8 source."""

from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
CART = HERE / "Stringer.tic"
SOURCE = HERE / "Stringer.p8"
MARKER = b"-- Stringer PICO-8 sound playback"
WAVE_SLOTS = {0: 60, 1: 61, 3: 62}
USED_SOUNDS = (1, 3, 4, 5, 6, 7, 8)
PITCH_SHIFT = 24  # Play-test adjustment: two octaves higher in TIC-80.
TIME_SCALE_NUM = 2  # The timing the user called "Much better".
TIME_SCALE_DEN = 1
COIN_FRAME = 25
SPARKLE_FRAME = 34
NEXT_PUZZLE_FRAME_REGULAR = 56
NEXT_PUZZLE_FRAME = 56


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


def sound_events():
    lines = SOURCE.read_text().split("__sfx__\n", 1)[1].splitlines()
    result = {}
    for sound_id in USED_SOUNDS:
        line = lines[sound_id]
        speed = int(line[2:4], 16)
        events = []
        for index in range(32):
            sample = line[8 + index * 5 : 13 + index * 5]
            note = int(sample[:2], 16) + PITCH_SHIFT
            if note > 95:
                raise ValueError(f"SFX {sound_id} note exceeds TIC-80's pitch range")
            wave = int(sample[2], 16)
            volume = int(sample[3], 16)
            if not volume:
                continue
            if wave not in WAVE_SLOTS:
                raise ValueError(f"Unsupported waveform {wave} in SFX {sound_id}")
            tick_denominator = 2 * TIME_SCALE_DEN
            frame = (index * speed * TIME_SCALE_NUM + tick_denominator // 2) // tick_denominator
            next_frame = (
                ((index + 1) * speed * TIME_SCALE_NUM + tick_denominator // 2)
                // tick_denominator
            )
            duration = max(1, next_frame - frame)
            events.append((frame, WAVE_SLOTS[wave], note, duration, min(15, volume * 2)))
        result[sound_id] = events
    return result


def lua_playback(events):
    rows = [
        f"{MARKER.decode()} (pitch +{PITCH_SHIFT}, time x{TIME_SCALE_NUM / TIME_SCALE_DEN:g})",
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
            "function stringer_sound_tick()",
            " if sound_queue then",
            "  sound_frame=sound_frame+1",
            "  sound_step()",
            " end",
            "end",
            "",
        ]
    )
    return ("\n".join(rows) + "\n").encode()


def repair(cart):
    sections = list(chunks(cart))
    code_chunks = [(start, end) for kind, start, end in sections if kind == 5]
    sample_chunks = [(start, end) for kind, start, end in sections if kind == 9]
    if len(code_chunks) != 1 or len(sample_chunks) != 1:
        raise ValueError("Expected one code chunk and one SFX chunk")
    code_start, code_end = code_chunks[0]
    sound_start, sound_end = sample_chunks[0]
    code = cart[code_start + 4 : code_end].rstrip(b"\0")
    wrapper_start = code.index(MARKER if MARKER in code else b"__sfx=sfx\n")
    wrapper_end = code.index(b"function stat(", wrapper_start)
    events = sound_events()
    code = code[:wrapper_start] + lua_playback(events) + code[wrapper_end:]
    if b"function TIC()\n stringer_sound_tick()\n" not in code:
        code = code.replace(b"function TIC()\n", b"function TIC()\n stringer_sound_tick()\n", 1)
    code, coin_count = re.subn(
        rb"if award_frame==\d+ then",
        f"if award_frame=={COIN_FRAME} then".encode(),
        code,
        count=1,
    )
    code, sparkle_count = re.subn(
        rb"if award_frame==\d+ and correct>=goal then",
        f"if award_frame=={SPARKLE_FRAME} and correct>=goal then".encode(),
        code,
        count=1,
    )
    next_condition = (
        f"if award_frame>={NEXT_PUZZLE_FRAME} then"
        if NEXT_PUZZLE_FRAME == NEXT_PUZZLE_FRAME_REGULAR
        else (
            f"if award_frame>=(correct>=goal and {NEXT_PUZZLE_FRAME} "
            f"or {NEXT_PUZZLE_FRAME_REGULAR}) then"
        )
    )
    code, next_count = re.subn(
        rb"if award_frame>=(?:\d+|\(correct>=goal and \d+ or \d+\)) then",
        next_condition.encode(),
        code,
        count=1,
    )
    code, animation_count = re.subn(
        rb"if award_frame<\d+ then",
        f"if award_frame<{COIN_FRAME} then".encode(),
        code,
        count=1,
    )
    code, animation_divisor_count = re.subn(
        rb"local t=award_frame/\d+",
        f"local t=award_frame/{COIN_FRAME}".encode(),
        code,
        count=1,
    )
    if (coin_count, sparkle_count, next_count, animation_count, animation_divisor_count) != (1, 1, 1, 1, 1):
        raise ValueError("Could not find Stringer's award timing")
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


before = CART.read_bytes()
after = repair(before)
if after != before:
    CART.write_bytes(after)
    print(f"Rebuilt TIC-80 SFX playback: {CART}")
else:
    print(f"Already repaired: {CART}")
