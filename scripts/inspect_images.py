#!/usr/bin/env python3
"""Read-only image preflight for the photo postcard workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageOps
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc


GPS_INFO_TAG = 34853


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {"path": str(path.resolve()), "exists": path.is_file()}
    if not path.is_file():
        record["error"] = "not a regular file"
        return record

    record["bytes"] = path.stat().st_size
    record["sha256"] = sha256(path)
    try:
        with Image.open(path) as source:
            source.load()
            image_format = source.format
            source_info = dict(source.info)
            exif = source.getexif()
            display = ImageOps.exif_transpose(source)
            width, height = display.size
            orientation = "square" if width == height else ("landscape" if width > height else "portrait")
            record.update(
                {
                    "format": image_format,
                    "width": width,
                    "height": height,
                    "aspect_width_over_height": round(width / height, 6),
                    "orientation": orientation,
                    "mode": display.mode,
                    "has_alpha": "A" in display.getbands(),
                    "icc_profile_present": bool(source_info.get("icc_profile")),
                    "exif_present": bool(exif),
                    "gps_metadata_present": bool(exif.get(GPS_INFO_TAG)) if exif else False,
                }
            )
    except Exception as exc:
        record["error"] = f"unreadable image: {exc}"
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    payload = {"images": [inspect(path) for path in args.images]}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    print(rendered)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    return 2 if any("error" in item for item in payload["images"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
