from PIL import Image, ImageDraw, ImageFont
import argparse
import hashlib
import sys
from pathlib import Path
import os

SIZE = (256, 256)

def normalize_initials(s: str) -> str:
    s = (s or "").strip().upper()
    s = "".join(ch for ch in s if ch.isalnum())
    return s[:2]

def bg_from_text(text: str) -> tuple[int, int, int]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    return (h[0] % 201, h[1] % 201, h[2] % 201)

def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126*r + 0.7152*g + 0.0722*b

def fg_for_bg(bg: tuple[int, int, int]) -> tuple[int, int, int]:
    return (0, 0, 0) if luminance(bg) > 140 else (255, 255, 255)

def try_fonts(font_size: int) -> ImageFont.ImageFont:
    # Linux
    linux_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]
    # Windows (typowe lokalizacje)
    win_dir = os.environ.get("WINDIR", r"C:\Windows")
    windows_candidates = [
        str(Path(win_dir) / "Fonts" / "segoeuib.ttf"),  # Segoe UI Bold (często jest)
        str(Path(win_dir) / "Fonts" / "arialbd.ttf"),   # Arial Bold
        str(Path(win_dir) / "Fonts" / "calibrib.ttf"),  # Calibri Bold
    ]

    for p in linux_candidates + windows_candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, font_size)
            except Exception:
                pass

    # Ostateczny fallback: zawsze działa, ale wygląda jak “print z terminala”
    return ImageFont.load_default()

def create_avatar(initials: str, size=SIZE) -> Image.Image:
    bg = bg_from_text(initials)
    fg = fg_for_bg(bg)

    img = Image.new("RGB", size, color=bg)
    draw = ImageDraw.Draw(img)

    font = try_fonts(100)

    bbox = draw.textbbox((0, 0), initials, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size[0] - w) / 2
    y = (size[1] - h) / 2 - 10

    draw.text((x, y), initials, font=font, fill=fg)
    return img

def main():
    parser = argparse.ArgumentParser(description="Generate an avatar with initials.")
    parser.add_argument("--user", required=True, help="Initials, e.g. mc")
    parser.add_argument("--outdir", default="avatary", help="Output directory (default: avatary)")
    args = parser.parse_args()

    initials = normalize_initials(args.user)
    if not initials:
        print("Podaj 1-2 znaki (litery/cyfry), np. --user mc", file=sys.stderr)
        sys.exit(2)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    out_path = outdir / f"etg_{initials}.png"

    img = create_avatar(initials)
    img.save(out_path, optimize=True)
    print(str(out_path))

if __name__ == "__main__":
    main()
