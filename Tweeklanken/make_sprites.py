"""Convert the family's sprite sheet and import 32x32 pictures into the cart.

sprites-v2.png is the editable 5x3 sheet of 256x256 cells. Each cell is an 8x
enlargement of a 32x32 picture. The generated sprites.png is the PICO-8 4x4
sheet. Change PALETTE_IDS to choose any 16 colors from the default and extended
palettes.
"""

from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "boxart" / ".deps"))
    from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SHEET = HERE / "sprites.png"
SOURCE = HERE / "sprites-v2.png"
CART = HERE / "Tweeklanken.p8"
PALETTE = (
    "#000000", "#1d2b53", "#7e2553", "#008751",
    "#ab5236", "#5f574f", "#c2c3c7", "#fff1e8",
    "#ff004d", "#ffa300", "#ffec27", "#00e436",
    "#29adff", "#83769c", "#ff77a8", "#ffccaa",
    "#291814", "#111d35", "#422136", "#125359",
    "#742f29", "#49333b", "#a28879", "#f3ef7d",
    "#be1250", "#ff6c24", "#a8e72e", "#00b543",
    "#065ab5", "#754665", "#ff6e59", "#ff9d81",
)
# The 16 sprite pixel values map to these PICO-8 display colors.
# Extended colors are 128..143. Keep slot 1 dark blue for the background.
PALETTE_IDS = tuple(range(16))
RGB = [tuple(bytes.fromhex(PALETTE[i if i < 16 else i - 112][1:]))
       for i in PALETTE_IDS]


def convert_source():
    """Pack the 5x3 enlarged artwork into PICO-8's 4x4 native sprite sheet."""
    source = Image.open(SOURCE).convert("RGB")
    if source.size != (1280, 768):
        raise ValueError("sprites-v2.png must be 1280x768 (5x3 cells of 256x256)")
    result = Image.new("RGB", (128, 128), RGB[1])
    for slot in range(15):
        x, y = (slot % 5) * 256, (slot // 5) * 256
        cell = source.crop((x, y, x + 256, y + 256))
        small = cell.resize((32, 32), Image.Resampling.NEAREST)
        if cell.tobytes() != small.resize((256, 256), Image.Resampling.NEAREST).tobytes():
            raise ValueError(f"Sprite slot {slot} is not pixel-perfect at 8x")
        result.paste(small, ((slot % 4) * 32, (slot // 4) * 32))
    result.save(SHEET)


def make_starters():
    im = Image.new("RGB", (128, 128), RGB[1])
    for n in range(15):
        tile = Image.new("RGB", (32, 32), RGB[1])
        d = ImageDraw.Draw(tile)
        c = lambda i: RGB[i]
        if n == 0:  # neus: face profile and nose
            d.ellipse((4, 3, 26, 29), fill=c(15), outline=c(5), width=2)
            d.polygon((24, 13, 30, 19, 23, 21), fill=c(15))
            d.line((24, 13, 30, 19, 23, 21), fill=c(5), width=2)
            d.ellipse((18, 12, 20, 14), fill=c(0))
            d.point((26, 19), fill=c(4))
        elif n == 1:  # deur
            d.rectangle((7, 2, 25, 30), fill=c(4), outline=c(15), width=2)
            d.rectangle((10, 5, 22, 27), outline=c(5), width=2)
            d.ellipse((19, 16, 21, 18), fill=c(10))
        elif n == 2:  # reus, with tiny house for scale
            d.ellipse((10, 2, 21, 13), fill=c(15), outline=c(5))
            d.rectangle((8, 13, 23, 24), fill=c(12), outline=c(5))
            d.line((10, 24, 7, 31), fill=c(5), width=3)
            d.line((21, 24, 25, 31), fill=c(5), width=3)
            d.rectangle((0, 26, 5, 31), fill=c(9))
            d.polygon((0, 26, 2, 23, 5, 26), fill=c(8))
            d.point((13, 8), fill=c(0)); d.point((19, 8), fill=c(0))
        elif n == 3:  # auto
            d.polygon((2, 17, 8, 16, 12, 9, 23, 9, 27, 16, 30, 18, 30, 25, 2, 25), fill=c(8))
            d.polygon((12, 11, 22, 11, 25, 16, 9, 16), fill=c(12))
            for x in (8, 24): d.ellipse((x-3, 22, x+3, 29), fill=c(0), outline=c(6))
        elif n == 4:  # pauw
            for x,y in ((5,8),(10,4),(16,3),(22,4),(27,8),(7,15),(25,15)):
                d.ellipse((x-4,y-4,x+4,y+4), fill=c(3), outline=c(11))
                d.ellipse((x-1,y-1,x+1,y+1), fill=c(12))
            d.ellipse((12, 13, 21, 28), fill=c(12))
            d.ellipse((14, 8, 20, 17), fill=c(12))
            d.polygon((20, 12, 25, 14, 20, 15), fill=c(10))
            d.point((18, 12), fill=c(0))
        elif n == 5:  # saus bottle
            d.rectangle((11, 2, 21, 6), fill=c(6))
            d.rounded_rectangle((7, 6, 25, 29), radius=4, fill=c(8), outline=c(15), width=2)
            d.ellipse((11, 13, 21, 23), fill=c(7))
            d.ellipse((14, 16, 18, 20), fill=c(8))
        elif n == 6:  # touw
            d.arc((2, 5, 24, 29), 20, 280, fill=c(9), width=4)
            d.arc((8, 5, 30, 29), 180, 500, fill=c(10), width=4)
            d.line((7, 24, 3, 29), fill=c(9), width=3)
        elif n == 7:  # hout, logs
            for x,y in ((5,15),(12,11),(18,16)):
                d.rectangle((x,y,x+12,y+8), fill=c(4), outline=c(5), width=2)
                d.ellipse((x+8,y,x+15,y+8), fill=c(15), outline=c(4), width=2)
                d.arc((x+10,y+2,x+14,y+6), 0, 300, fill=c(4))
        elif n == 8:  # goud bars
            d.polygon((3,22,7,14,20,14,24,22), fill=c(10), outline=c(9))
            d.polygon((12,27,16,19,28,19,31,27), fill=c(10), outline=c(9))
            d.line((8,17,17,17), fill=c(7), width=2)
            d.point((5,5), fill=c(7)); d.line((24,5,24,11), fill=c(7))
        elif n == 9:  # geit
            d.ellipse((8, 9, 25, 25), fill=c(7), outline=c(5), width=2)
            d.polygon((10,11,7,3,13,7), fill=c(6), outline=c(5))
            d.polygon((20,8,25,2,24,12), fill=c(6), outline=c(5))
            d.polygon((15,23,18,31,22,23), fill=c(6))
            d.ellipse((12,15,14,17), fill=c(0)); d.ellipse((20,15,22,17), fill=c(0))
            d.ellipse((15,21,19,23), fill=c(14))
        elif n == 10:  # trein
            d.rectangle((4, 8, 28, 25), fill=c(8), outline=c(7), width=2)
            for x in (8,15,22): d.rectangle((x,11,x+4,16), fill=c(12))
            for x in (10,23): d.ellipse((x-3,22,x+3,28), fill=c(0), outline=c(6))
            d.line((1,30,31,30), fill=c(5), width=2)
        elif n == 11:  # zeil boat
            d.polygon((3,23,29,23,24,29,9,29), fill=c(4), outline=c(15))
            d.line((16,4,16,23), fill=c(6), width=2)
            d.polygon((14,5,14,21,4,21), fill=c(7), outline=c(12))
            d.polygon((18,7,18,21,28,21), fill=c(10), outline=c(9))
            d.line((2,30,30,30), fill=c(12))
        elif n == 12:  # koe
            d.ellipse((6,8,26,27), fill=c(7), outline=c(5), width=2)
            d.polygon((9,11,3,6,4,17), fill=c(7), outline=c(5))
            d.polygon((23,11,29,6,28,17), fill=c(7), outline=c(5))
            d.ellipse((14,10,20,16), fill=c(0))
            d.ellipse((10,20,22,27), fill=c(14), outline=c(5))
            d.point((13,23), fill=c(4)); d.point((19,23), fill=c(4))
        elif n == 13:  # huis
            d.polygon((2,14,16,3,30,14), fill=c(8), outline=c(15))
            d.rectangle((5,14,27,29), fill=c(9), outline=c(15), width=2)
            d.rectangle((13,20,19,29), fill=c(4))
            d.rectangle((7,17,11,21), fill=c(12))
            d.rectangle((21,17,25,21), fill=c(12))
        elif n == 14:  # bij
            d.ellipse((7, 11, 16, 20), fill=c(7), outline=c(12))
            d.ellipse((16, 8, 25, 18), fill=c(7), outline=c(12))
            d.ellipse((8, 16, 25, 27), fill=c(10), outline=c(5), width=2)
            d.line((14,17,14,26), fill=c(0), width=3)
            d.line((20,17,20,26), fill=c(0), width=3)
            d.point((24,20), fill=c(0))
        im.paste(tile, ((n % 4) * 32, (n // 4) * 32))
    # Rearrange reusable sketches to match the current word order. Draw simple
    # temporary pictures for the new words; families can paint over each cell.
    old = im
    im = Image.new("RGB", (128, 128), RGB[1])
    reuse = {0: 0, 1: 1, 2: 4, 3: 3, 6: 9, 7: 10, 8: 6}
    for dest, src in reuse.items():
        crop = old.crop(((src % 4) * 32, (src // 4) * 32,
                         (src % 4 + 1) * 32, (src // 4 + 1) * 32))
        im.paste(crop, ((dest % 4) * 32, (dest // 4) * 32))
    for n in (4, 5, 9, 10, 11, 12, 13, 14):
        tile = Image.new("RGB", (32, 32), RGB[1])
        d = ImageDraw.Draw(tile)
        c = lambda i: RGB[i]
        if n == 4:  # blauw: blue paint tin and brush
            d.rectangle((5, 12, 24, 29), fill=c(12), outline=c(7), width=2)
            d.rectangle((4, 10, 25, 13), fill=c(6))
            d.line((24, 3, 15, 19), fill=c(4), width=3)
            d.polygon((14, 19, 18, 21, 13, 27, 10, 24), fill=c(12))
        elif n == 5:  # kei
            d.polygon((3, 26, 7, 14, 17, 7, 27, 13, 30, 25, 24, 29, 7, 29),
                      fill=c(6), outline=c(5))
            d.polygon((7, 14, 17, 7, 19, 18, 11, 21), fill=c(7))
            d.line((19, 18, 27, 13), fill=c(5))
        elif n == 9:  # kous
            d.polygon((10, 3, 22, 3, 22, 20, 28, 22, 27, 28, 18, 30,
                       8, 25, 10, 20), fill=c(8), outline=c(7))
            d.rectangle((10, 4, 22, 8), fill=c(7))
            d.line((8, 25, 17, 29), fill=c(15), width=2)
        elif n == 10:  # koud: snowman
            d.ellipse((7, 14, 25, 31), fill=c(7), outline=c(12))
            d.ellipse((10, 3, 22, 17), fill=c(7), outline=c(12))
            d.rectangle((9, 13, 23, 16), fill=c(8))
            d.point((14, 9), fill=c(0)); d.point((19, 9), fill=c(0))
            d.polygon((16, 11, 23, 12, 16, 13), fill=c(9))
            d.point((16, 21), fill=c(0)); d.point((16, 26), fill=c(0))
        elif n == 11:  # boek
            d.polygon((3, 7, 15, 10, 15, 27, 3, 24), fill=c(7), outline=c(5))
            d.polygon((16, 10, 29, 7, 29, 24, 16, 27), fill=c(7), outline=c(5))
            d.line((15, 10, 15, 27), fill=c(4), width=2)
            for y in (14, 17, 20):
                d.line((6, y, 12, y + 2), fill=c(6))
                d.line((19, y + 2, 26, y), fill=c(6))
        elif n == 12:  # poes
            d.polygon((4, 12, 5, 3, 12, 8, 20, 8, 27, 3, 28, 13,
                       25, 25, 16, 30, 7, 25), fill=c(9), outline=c(5))
            d.ellipse((9, 16, 12, 19), fill=c(0))
            d.ellipse((21, 16, 24, 19), fill=c(0))
            d.polygon((15, 21, 19, 21, 17, 24), fill=c(14))
            d.line((3, 22, 13, 23), fill=c(7))
            d.line((21, 23, 30, 22), fill=c(7))
        elif n == 13:  # bijl
            d.line((8, 29, 22, 5), fill=c(4), width=4)
            d.polygon((20, 5, 28, 3, 29, 18, 20, 15, 16, 12),
                      fill=c(6), outline=c(7))
            d.line((4, 29, 12, 29), fill=c(5), width=2)
        elif n == 14:  # ijs: ice cream
            d.polygon((10, 15, 23, 15, 17, 30), fill=c(9), outline=c(4))
            d.ellipse((5, 6, 27, 20), fill=c(15), outline=c(14))
            d.ellipse((10, 2, 23, 15), fill=c(7), outline=c(14))
            d.ellipse((15, 3, 18, 6), fill=c(8))
        im.paste(tile, ((n % 4) * 32, (n // 4) * 32))
    im.save(SHEET)


def import_sheet():
    if len(PALETTE_IDS) != 16 or len(set(PALETTE_IDS)) != 16:
        raise ValueError("PALETTE_IDS must contain 16 distinct colors")
    if any(not (0 <= i <= 15 or 128 <= i <= 143) for i in PALETTE_IDS):
        raise ValueError("Palette colors must be 0..15 or 128..143")
    im = Image.open(SHEET).convert("RGB")
    if im.size != (128, 128):
        raise ValueError("sprites.png must be exactly 128x128")
    lookup = {color: f"{i:x}" for i, color in enumerate(RGB)}
    rows = []
    for y in range(128):
        row = []
        for x in range(128):
            color = im.getpixel((x, y))
            if color not in lookup:
                raise ValueError(f"Non-PICO-8 color {color} at {(x, y)}")
            row.append(lookup[color])
        rows.append("".join(row))
    source = CART.read_text(encoding="ascii")
    begin = "-- palette begin (generated by make_sprites.py)"
    end = "-- palette end"
    generated = begin + "\nfunction set_sprite_palette()\n"
    generated += "".join(f" pal({i},{color},1)\n" for i, color in enumerate(PALETTE_IDS)
                         if color != i)
    generated += "end\n" + end
    source = source[:source.index(begin)] + generated + source[source.index(end) + len(end):]
    before, marker, after = source.partition("__gfx__")
    if not marker:
        raise ValueError("Cartridge has no __gfx__ section")
    suffix = "__sfx__" + after.split("__sfx__", 1)[1] if "__sfx__" in after else ""
    source = before + "__gfx__\n" + "\n".join(rows) + "\n" + suffix
    CART.write_text(source, encoding="ascii")


if __name__ == "__main__":
    if SOURCE.exists():
        convert_source()
    elif not SHEET.exists():
        make_starters()
    import_sheet()
    print(f"Imported {SHEET} into {CART}")
