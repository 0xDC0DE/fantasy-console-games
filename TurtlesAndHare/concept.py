"""Render light-grass and black-field 128x128 board concepts.

Run with: python3 concept.py
The animals are downsized directly from the supplied image.png artwork.
"""

from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "boxart" / ".deps"))
    from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
PALETTE = [
    "#000000", "#1d2b53", "#7e2553", "#008751",
    "#ab5236", "#5f574f", "#c2c3c7", "#fff1e8",
    "#ff004d", "#ffa300", "#ffec27", "#00e436",
    "#29adff", "#83769c", "#ff77a8", "#ffccaa",
    "#a8e72e",  # extended PICO-8 color 138, available with pal(11,138,1)
    "#00b543",  # 139 jade
    "#065ab5",  # 140 royal blue
    "#754665",  # 141 mauve
    "#ff6e59",  # 142 coral
    "#be1250",  # 136 burgundy
]
C = [tuple(bytes.fromhex(value[1:])) for value in PALETTE]
EDGE = 4
CELL = 40
FENCE_WIDTH = 6


def rect(draw, box, color):
    draw.rectangle(box, fill=C[color])


def fence(draw, orientation, boundary, start, width):
    """A fence is centered on a cell boundary, spanning 36 pixels."""
    if orientation == "h":
        x0, x1 = start + 2, start + CELL - 3
        y0 = boundary - width // 2
        rect(draw, (x0, y0, x1, y0 + width - 1), 1)
    else:
        y0, y1 = start + 2, start + CELL - 3
        x0 = boundary - width // 2
        rect(draw, (x0, y0, x0 + width - 1, y1), 1)


def cursor(draw, col, row):
    """A 32x32 corner-only selection frame inside a 40x40 space."""
    x0 = EDGE + col * CELL + 4
    y0 = EDGE + row * CELL + 4
    x1, y1 = x0 + 31, y0 + 31
    # Five-pixel arms, two pixels thick; the center and most edges stay open.
    for x, sx in ((x0, 1), (x1, -1)):
        for y, sy in ((y0, 1), (y1, -1)):
            rect(draw, (min(x, x + sx * 4), min(y, y + sy),
                        max(x, x + sx * 4), max(y, y + sy)), 1)
            rect(draw, (min(x, x + sx), min(y, y + sy * 4),
                        max(x, x + sx), max(y, y + sy * 4)), 1)


def render(background, filename, selected=None):
    image = Image.new("RGB", (128, 128), C[background])
    d = ImageDraw.Draw(image)

    # Four-pixel food sections on a dark-blue rim.
    rect(d, (0, 0, 127, 127), 1)
    rect(d, (EDGE, EDGE, 123, 123), background)
    food_edges = (
        (3, (0, 0, 43, 3)), (3, (0, 4, 3, 43)),       # green
        (9, (44, 0, 83, 3)),                           # orange
        (13, (84, 0, 127, 3)), (13, (124, 4, 127, 43)), # purple
        (8, (0, 84, 3, 127)), (8, (4, 124, 43, 127)), # red
        (12, (44, 124, 83, 127)),                       # blue
        (10, (84, 124, 127, 127)),
        (10, (124, 84, 127, 123)),                     # yellow
    )
    for color, box in food_edges:
        rect(d, box, color)

    # The first photo's broad fence arrangement, now uniformly six pixels wide.
    fence(d, "h", 44, 44, FENCE_WIDTH)  # top center / middle center
    fence(d, "v", 44, 44, FENCE_WIDTH)  # middle left / middle center
    fence(d, "h", 84, 84, FENCE_WIDTH)  # middle right / bottom right
    fence(d, "v", 84, 84, FENCE_WIDTH)  # bottom center / bottom right

    # Reference sprites are 32x32 slots with transparent padding.
    sheet = Image.open(HERE / "animals.png").convert("RGBA")
    for slot, col, row in (
        (0, 0, 0), (4, 2, 0), (1, 0, 1),
        (3, 2, 1), (2, 1, 2), (5, 1, 0),
    ):
        sprite = sheet.crop((slot * 32, 0, (slot + 1) * 32, 32))
        image.paste(sprite, (EDGE + col * CELL + 4, EDGE + row * CELL + 4), sprite)
    if selected is not None:
        cursor(d, *selected)

    image.save(HERE / filename)
    image.resize((512, 512), Image.Resampling.NEAREST).save(
        HERE / filename.replace("-128", "-4x"))


def main():
    render(16, "concept-128.png")
    render(0, "concept-black-128.png")
    render(16, "concept-cursor-128.png", selected=(0, 0))


if __name__ == "__main__":
    main()
