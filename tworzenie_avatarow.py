"""Generate a PNG avatar with one or two initials."""

import argparse
import hashlib
import unicodedata
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw, ImageFont

SIZE = (256, 256)


def normalize_initials(s: str) -> str:
    s = unicodedata.normalize("NFC", (s or "").strip().upper())
    s = "".join(ch for ch in s if ch.isalnum())
    return s[:2]


def bg_from_text(text: str) -> tuple[int, int, int]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    return (h[0] % 201, h[1] % 201, h[2] % 201)


def luminance(rgb: tuple[int, int, int]) -> float:
    """Return relative sRGB luminance, with gamma correction."""
    channels = [value / 255 for value in rgb]
    r, g, b = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def fg_for_bg(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    light = luminance(bg)
    black_contrast = (light + 0.05) / 0.05
    white_contrast = 1.05 / (light + 0.05)
    return (0, 0, 0) if black_contrast >= white_contrast else (255, 255, 255)


def try_fonts(font_size: int) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
    # Pillow searches the font directories for the current OS, including XDG on Linux.
    candidates = [
        "DejaVuSans-Bold.ttf",
        "LiberationSans-Bold.ttf",
        "NotoSans-Bold.ttf",
        "segoeuib.ttf",
        "arialbd.ttf",
        "calibrib.ttf",
        "Arial Bold.ttf",
    ]

    for name in candidates:
        try:
            return ImageFont.truetype(name, font_size)
        except OSError:
            continue

    return ImageFont.load_default(size=font_size)


def create_avatar(initials: str, size=SIZE) -> Image.Image:
    bg = bg_from_text(initials)
    fg = fg_for_bg(bg)

    img = Image.new("RGB", size, color=bg)
    draw = ImageDraw.Draw(img)

    font_size = max(1, min(size) * 100 // 256)
    while True:
        font = try_fonts(font_size)
        left, top, right, bottom = draw.textbbox((0, 0), initials, font=font)
        width, height = right - left, bottom - top
        if font_size == 1 or (width <= size[0] * 0.85 and height <= size[1] * 0.85):
            break
        font_size -= 1

    # Bounding boxes can have a nonzero origin, especially for accented letters.
    x = (size[0] - width) / 2 - left
    y = (size[1] - height) / 2 - top

    draw.text((x, y), initials, font=font, fill=fg)
    return img


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an avatar with initials.")
    parser.add_argument("--user", required=True, help="Initials, e.g. mc")
    parser.add_argument("--outdir", default="avatary", help="Output directory (default: avatary)")
    args = parser.parse_args()

    initials = normalize_initials(args.user)
    if not initials:
        parser.error("Podaj 1-2 znaki (litery/cyfry), np. --user mc")

    outdir = Path(args.outdir)
    out_path = outdir / f"etg_{initials}.png"
    try:
        img = create_avatar(initials)
        outdir.mkdir(parents=True, exist_ok=True)
        img.save(out_path, optimize=True)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Nie udało się utworzyć awatara: {error}\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
