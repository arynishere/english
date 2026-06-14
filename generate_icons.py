#!/usr/bin/env python3
"""Generate PWA icons (book + daily 4 badge)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent
ICONS = BASE / "static" / "icons"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def gradient(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            px[x, y] = (lerp(0x4F, 0xA7, t), lerp(0x8C, 0x8B, t), lerp(0xFF, 0xFA, t), 255)
    return img


def round_rect_mask(size: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.22), fill=255)
    return mask


def draw_logo(size: int) -> Image.Image:
    img = gradient(size)
    img.putalpha(round_rect_mask(size))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    bw, bh = int(size * 0.42), int(size * 0.36)
    x0, y0 = cx - bw // 2, cy - bh // 2 + int(size * 0.02)
    draw.polygon(
        [(x0, y0), (cx - 4, y0 - 6), (cx - 4, y0 + bh + 6), (x0, y0 + bh)],
        fill=(255, 255, 255, 235),
    )
    draw.polygon(
        [(cx + 4, y0 - 6), (x0 + bw, y0), (x0 + bw, y0 + bh), (cx + 4, y0 + bh + 6)],
        fill=(255, 255, 255, 200),
    )
    draw.line(
        [(cx, cy - bh // 2 - 4), (cx, cy + bh // 2 + 4)],
        fill=(79, 140, 255, 220),
        width=max(2, size // 85),
    )
    for i, w in enumerate((0.55, 0.42, 0.48)):
        ly = y0 + int(bh * (0.28 + i * 0.22))
        lw = int(bw * w)
        draw.line(
            [(x0 + int(bw * 0.12), ly), (x0 + int(bw * 0.12) + lw, ly)],
            fill=(79, 140, 255, 120),
            width=max(2, size // 50),
        )
    br = int(size * 0.1)
    bx, by = int(size * 0.72), int(size * 0.72)
    draw.ellipse((bx - br, by - br, bx + br, by + br), fill=(61, 214, 140, 255))
    try:
        font = ImageFont.truetype(FONT, int(size * 0.11))
    except OSError:
        font = ImageFont.load_default()
    draw.text((bx, by), "4", fill=(255, 255, 255, 255), font=font, anchor="mm")
    return img


def main() -> None:
    ICONS.mkdir(parents=True, exist_ok=True)
    for size in (180, 192, 512):
        out = ICONS / f"icon-{size}.png"
        draw_logo(size).save(out)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
