"""Downsize the supplied enlarged animal art into clean PICO-8-scale sprites.

The source has roughly 28-pixel eyes and 320-pixel-wide turtles. At 30 pixels
wide, the eyes land at about three pixels. Color is reduced to three body
shades per animal; the extra patch inside each shell is merged away.
"""

from pathlib import Path
import sys

try:
    from PIL import Image
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "boxart" / ".deps"))
    from PIL import Image

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "image.png"
OUTPUT = HERE / "reference-sprites.png"

# Source regions include only one animal each. Colors are light, mid, dark.
ANIMALS = (
    ("green", (46, 228, 367, 495), (30, 25),
     ((0, 228, 54), (0, 181, 67), (0, 135, 81))),
    ("blue", (391, 228, 727, 495), (30, 25),
     ((41, 173, 255), (6, 90, 181), (29, 43, 83))),
    ("red", (754, 228, 1082, 495), (30, 25),
     ((255, 110, 89), (255, 0, 77), (190, 18, 80))),
    ("yellow", (1110, 228, 1445, 495), (30, 25),
     ((255, 236, 39), (255, 163, 0), (171, 82, 54))),
    ("purple", (1465, 228, 1804, 495), (30, 25),
     ((131, 118, 156), (117, 70, 101), (126, 37, 83))),
    ("bunny", (1883, 181, 2102, 495), (21, 30),
     ((255, 236, 39), (255, 163, 0), (171, 82, 54))),
)


def nearest(rgb, shades):
    return min(range(3), key=lambda i: sum(
        (rgb[channel] - shades[i][channel]) ** 2 for channel in range(3)))


def extract(source, crop, size, shades, name):
    turtle = name != "bunny"
    original = source.crop(crop).resize(size, Image.Resampling.NEAREST)
    result = Image.new("RGBA", size)
    for y in range(size[1]):
        for x in range(size[0]):
            red, green, blue, alpha = original.getpixel((x, y))
            if alpha < 170:
                continue
            if max(red, green, blue) < 75:
                result.putpixel((x, y), (29, 43, 83, 255))
                continue
            index = nearest((red, green, blue), shades)
            # The source adds a fourth shade as a small inset on the shell.
            # Flatten that inset while retaining the original outer silhouette.
            if turtle and 18 <= x <= 23 and 10 <= y <= 16:
                index = 2
            result.putpixel((x, y), (*shades[index], 255))
    if turtle:
        # A straight, three-pixel-high bright belly rim under every shell.
        for y in range(16, 19):
            for x in range(13, 30):
                result.putpixel((x, y), (*shades[0], 255))
        # All turtles use the same four-pixel-wide middle visible leg.
        for y in range(19, 25):
            for x in range(17, 21):
                result.putpixel((x, y), (0, 0, 0, 0))
            for x in range(13, 17):
                result.putpixel((x, y), (*shades[1], 255))
        if name == "blue":
            result.putpixel((2, 2), (0, 0, 0, 0))
        if name in ("red", "purple"):
            result.putpixel((27, 19), (0, 0, 0, 0))
        if name == "green":
            for x in range(5, 13):
                result.putpixel((x, 13), (*shades[0], 255))
            result.putpixel((10, 19), (0, 0, 0, 0))
    # Nearest-neighbor scaling can turn a square eye into a 2x3 rectangle.
    # Restore the source art's square pixel block at this scale.
    if turtle:
        groups = [lambda x: x < 14]
    else:
        groups = [lambda x: x < 10, lambda x: x >= 10]
    for belongs in groups:
        eye = [(x, y) for y in range(14 if turtle else 21)
               for x in range(size[0]) if belongs(x)
               and result.getpixel((x, y))[:3] == (29, 43, 83)]
        if not eye:
            continue
        center_x = round(sum(x for x, _ in eye) / len(eye))
        center_y = round(sum(y for _, y in eye) / len(eye))
        for x, y in eye:
            result.putpixel((x, y), (*shades[0 if turtle else 1], 255))
        for y in range(center_y - 1, center_y + 2):
            for x in range(center_x - 1, center_x + 2):
                result.putpixel((x, y), (29, 43, 83, 255))
    return result


def main():
    source = Image.open(SOURCE).convert("RGBA")
    sheet = Image.new("RGBA", (32 * 6, 32))
    for slot, (name, crop, size, shades) in enumerate(ANIMALS):
        sprite = extract(source, crop, size, shades, name)
        sheet.paste(sprite, (slot * 32 + (32 - size[0]) // 2,
                             (32 - size[1]) // 2), sprite)
    sheet.save(OUTPUT)
    sheet.resize((32 * 6 * 4, 32 * 4), Image.Resampling.NEAREST).save(
        HERE / "reference-sprites-4x.png")


if __name__ == "__main__":
    main()
