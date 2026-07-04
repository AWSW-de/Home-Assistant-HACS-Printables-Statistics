"""Generate local branding assets for the Printables Stats integration."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORANGE = (250, 104, 49, 255)
ORANGE_DARK = (210, 72, 30, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)
GREY = (247, 247, 247, 255)
TEXT = (31, 41, 55, 255)


def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    """Write an RGBA PNG using only the Python standard library."""
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        start = y * width
        for pixel in pixels[start : start + width]:
            raw.extend(pixel)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    data = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(data)


def canvas(width: int, height: int, color: tuple[int, int, int, int]) -> list[tuple[int, int, int, int]]:
    """Create a filled RGBA canvas."""
    return [color for _ in range(width * height)]


def rect(
    pixels: list[tuple[int, int, int, int]],
    width: int,
    height: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int, int],
) -> None:
    """Draw a filled rectangle."""
    for y in range(max(0, y0), min(height, y1)):
        row = y * width
        for x in range(max(0, x0), min(width, x1)):
            pixels[row + x] = color


def circle(
    pixels: list[tuple[int, int, int, int]],
    width: int,
    height: int,
    cx: int,
    cy: int,
    radius: int,
    color: tuple[int, int, int, int],
) -> None:
    """Draw a filled circle."""
    r2 = radius * radius
    for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
        row = y * width
        for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r2:
                pixels[row + x] = color


def draw_icon(size: int) -> list[tuple[int, int, int, int]]:
    """Draw a simple Printables-inspired icon."""
    pixels = canvas(size, size, TRANSPARENT)
    circle(pixels, size, size, size // 2, size // 2, int(size * 0.46), ORANGE)

    scale = size / 256
    def s(value: int) -> int:
        return round(value * scale)

    rect(pixels, size, size, s(74), s(54), s(112), s(204), WHITE)
    rect(pixels, size, size, s(112), s(54), s(174), s(92), WHITE)
    rect(pixels, size, size, s(112), s(116), s(174), s(154), WHITE)
    circle(pixels, size, size, s(174), s(104), s(50), WHITE)
    circle(pixels, size, size, s(174), s(104), s(22), ORANGE)
    rect(pixels, size, size, s(174), s(54), s(220), s(154), ORANGE)
    return pixels


def draw_logo(size: int) -> list[tuple[int, int, int, int]]:
    """Draw a logo asset with the same mark on a white background."""
    pixels = canvas(size, size, GREY)
    icon = draw_icon(round(size * 0.72))
    icon_size = round(size * 0.72)
    offset = (size - icon_size) // 2
    for y in range(icon_size):
        for x in range(icon_size):
            pixel = icon[y * icon_size + x]
            if pixel[3]:
                pixels[(y + offset) * size + x + offset] = pixel
    return pixels


def draw_banner() -> list[tuple[int, int, int, int]]:
    """Draw the README preview image."""
    width, height = 1200, 630
    pixels = canvas(width, height, GREY)
    rect(pixels, width, height, 0, 0, 430, height, ORANGE)
    rect(pixels, width, height, 430, 0, 450, height, ORANGE_DARK)

    icon = draw_icon(300)
    for y in range(300):
        for x in range(300):
            pixel = icon[y * 300 + x]
            if pixel[3]:
                pixels[(y + 165) * width + x + 65] = pixel

    # Block lettering keeps the image dependency-free while still giving HACS a useful preview.
    rect(pixels, width, height, 520, 185, 1000, 235, TEXT)
    rect(pixels, width, height, 520, 270, 1110, 310, ORANGE)
    rect(pixels, width, height, 520, 345, 1020, 378, TEXT)
    rect(pixels, width, height, 520, 405, 860, 438, TEXT)
    return pixels


def main() -> None:
    """Generate all local asset files."""
    targets = [
        ROOT / "brand" / "icon.png",
        ROOT / "custom_components" / "printables_stats" / "brand" / "icon.png",
        ROOT / "custom_components" / "printables_stats" / "icon.png",
    ]
    for target in targets:
        write_png(target, 256, 256, draw_icon(256))

    logo_targets = [
        ROOT / "brand" / "logo.png",
        ROOT / "custom_components" / "printables_stats" / "brand" / "logo.png",
        ROOT / "custom_components" / "printables_stats" / "logo.png",
    ]
    for target in logo_targets:
        write_png(target, 512, 512, draw_logo(512))

    write_png(ROOT / "Image1.png", 1200, 630, draw_banner())


if __name__ == "__main__":
    main()
