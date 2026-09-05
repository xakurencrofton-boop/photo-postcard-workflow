#!/usr/bin/env python3
"""Create a labeled contact sheet without modifying source images."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--cell-width", type=int, default=640)
    parser.add_argument("--cell-height", type=int, default=720)
    args = parser.parse_args()

    if args.columns < 1 or args.cell_width < 100 or args.cell_height < 100:
        raise SystemExit("columns must be >= 1 and cell dimensions >= 100")

    rows = math.ceil(len(args.images) / args.columns)
    label_height = 42
    sheet = Image.new("RGB", (args.columns * args.cell_width, rows * (args.cell_height + label_height)), "#f3f0e9")
    draw = ImageDraw.Draw(sheet)
    font = safe_font(20)
    failures: list[str] = []

    for index, path in enumerate(args.images):
        column = index % args.columns
        row = index // args.columns
        left = column * args.cell_width
        top = row * (args.cell_height + label_height)
        try:
            with Image.open(path) as source:
                tile = ImageOps.contain(ImageOps.exif_transpose(source).convert("RGB"), (args.cell_width - 24, args.cell_height - 24), Image.Resampling.LANCZOS)
            x = left + (args.cell_width - tile.width) // 2
            y = top + (args.cell_height - tile.height) // 2
            sheet.paste(tile, (x, y))
        except Exception as exc:
            failures.append(f"{path}: {exc}")
            draw.rectangle((left + 12, top + 12, left + args.cell_width - 12, top + args.cell_height - 12), outline="#b00020", width=3)

        label = f"{index + 1:02d}  {path.name}"
        try:
            draw.text((left + 14, top + args.cell_height + 9), label, fill="#222222", font=font)
        except UnicodeEncodeError:
            draw.text((left + 14, top + args.cell_height + 9), f"{index + 1:02d}", fill="#222222", font=font)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, format="PNG", optimize=True)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 2
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
