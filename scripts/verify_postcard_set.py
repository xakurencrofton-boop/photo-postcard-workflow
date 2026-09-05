#!/usr/bin/env python3
"""Verify output count, file readability, role order, ratios, and duplicates."""

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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_roles(mode: str) -> list[tuple[str, float | None]]:
    roles: list[tuple[str, float | None]] = []
    if mode == "full":
        roles.append(("photo-retouch-pro", None))
    roles.extend(
        [
            ("scenes-gathered-zine", 3 / 5),
            ("gc-minimal-zine", 3 / 5),
            ("photo-evidence-ledger", 2 / 3),
            ("photo-revival", 3 / 4),
        ]
    )
    return roles


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("standard", "full"), required=True)
    parser.add_argument("--tolerance", type=float, default=0.04)
    parser.add_argument("--out", type=Path, help="Optional path for the JSON report")
    parser.add_argument(
        "--skip-name-check",
        action="store_true",
        help="Do not require each ordered filename to contain its expected role slug",
    )
    parser.add_argument("images", nargs="+", type=Path)
    args = parser.parse_args()

    if args.tolerance < 0:
        parser.error("--tolerance must be non-negative")

    expected = expected_roles(args.mode)
    payload: dict[str, Any] = {
        "mode": args.mode,
        "photo_revival": True,
        "expected_count": len(expected),
        "actual_count": len(args.images),
        "files": [],
        "errors": [],
        "warnings": [],
    }
    if len(args.images) != len(expected):
        payload["errors"].append(f"expected {len(expected)} ordered outputs, received {len(args.images)}")

    seen_hashes: dict[str, str] = {}
    for index, path in enumerate(args.images):
        role, target_ratio = expected[index] if index < len(expected) else ("unexpected", None)
        record: dict[str, Any] = {"role": role, "path": str(path.resolve())}
        if not path.is_file():
            record["error"] = "missing or not a regular file"
            payload["errors"].append(f"{role}: missing file {path}")
            payload["files"].append(record)
            continue

        try:
            digest = sha256(path)
            with Image.open(path) as source:
                source.load()
                width, height = ImageOps.exif_transpose(source).size
            ratio = width / height
            name_matches_role = role == "unexpected" or role in path.stem.lower()
            record.update(
                {
                    "sha256": digest,
                    "width": width,
                    "height": height,
                    "aspect_width_over_height": round(ratio, 6),
                    "name_matches_role": name_matches_role,
                }
            )
            if not args.skip_name_check and not name_matches_role:
                payload["errors"].append(f"{role}: filename does not contain expected role slug")
            if digest in seen_hashes:
                payload["errors"].append(f"{role}: byte-identical to {seen_hashes[digest]}")
            else:
                seen_hashes[digest] = role
            if target_ratio is not None and abs(ratio - target_ratio) > args.tolerance:
                payload["errors"].append(f"{role}: ratio {ratio:.4f} differs from expected {target_ratio:.4f}")
            if target_ratio is not None and width >= height:
                payload["errors"].append(f"{role}: expected portrait orientation")
            if min(width, height) < 800:
                payload["warnings"].append(f"{role}: short edge is only {min(width, height)} px")
        except Exception as exc:
            record["error"] = str(exc)
            payload["errors"].append(f"{role}: unreadable image: {exc}")
        payload["files"].append(record)

    payload["technical_pass"] = not payload["errors"]
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    print(rendered)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    return 0 if payload["technical_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
