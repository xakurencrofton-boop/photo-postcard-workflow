#!/usr/bin/env python3
"""Write a provenance manifest for a completed photo postcard set."""

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


def image_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing image: {path}")
    with Image.open(path) as source:
        source.load()
        width, height = ImageOps.exif_transpose(source).size
        image_format = source.format
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "format": image_format,
        "width": width,
        "height": height,
        "aspect_width_over_height": round(width / height, 6),
    }


def roles_and_skills(mode: str) -> tuple[list[str], list[str]]:
    roles: list[str] = []
    skills: list[str] = ["photo-postcard-workflow", "imagegen"]
    if mode == "full":
        roles.append("photo-retouch-pro")
        skills.append("photo-retouch-pro")
    roles.extend(["scenes-gathered-zine", "gc-minimal-zine", "photo-evidence-ledger", "photo-revival"])
    skills.extend(
        [
            "scenes-gathered-zine-v1-3",
            "gc-minimal-zine-poster-v0-3",
            "photo-evidence-ledger",
            "photo-revival",
        ]
    )
    return roles, skills


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source", type=Path, help="Local source image")
    source_group.add_argument(
        "--conversation-source",
        metavar="LABEL",
        help="Honest label for a conversation-only attachment with no local path",
    )
    parser.add_argument("--mode", choices=("standard", "full"), required=True)
    parser.add_argument("--technical-report", type=Path)
    parser.add_argument(
        "--executor",
        action="append",
        default=[],
        help="Additional actual raster executor, such as adobe-batch-edit-photos",
    )
    parser.add_argument("--visual-status", choices=("not-reviewed", "pass", "limited"), default="not-reviewed")
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("images", nargs="+", type=Path)
    args = parser.parse_args()

    roles, skills = roles_and_skills(args.mode)
    if len(args.images) != len(roles):
        parser.error(f"expected {len(roles)} ordered primary images, received {len(args.images)}")
    if args.out.exists() and not args.force:
        parser.error(f"refusing to overwrite existing manifest: {args.out}")

    try:
        if args.source:
            source = image_record(args.source)
        else:
            source = {
                "path": None,
                "conversation_attachment": args.conversation_source,
                "sha256": None,
                "format": None,
                "width": None,
                "height": None,
                "aspect_width_over_height": None,
                "metadata_status": "unavailable-no-local-path",
            }
        outputs = []
        for role, path in zip(roles, args.images, strict=True):
            record = image_record(path)
            record["role"] = role
            outputs.append(record)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    technical = "not-run"
    if args.technical_report:
        try:
            report = json.loads(args.technical_report.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"cannot read technical report: {exc}")
        report_paths = [str(Path(item["path"]).resolve()) for item in report.get("files", [])]
        output_paths = [item["path"] for item in outputs]
        if report_paths != output_paths:
            parser.error("technical report paths/order do not match manifest outputs")
        if report.get("mode") != args.mode or report.get("photo_revival") is not True:
            parser.error("technical report mode or fixed Photo Revival route does not match manifest")
        if report.get("expected_count") != len(roles) or report.get("actual_count") != len(outputs):
            parser.error("technical report counts do not match manifest outputs")
        report_files = report.get("files", [])
        for report_item, output_item in zip(report_files, outputs, strict=True):
            if report_item.get("role") != output_item["role"]:
                parser.error("technical report roles do not match manifest outputs")
            for field in ("sha256", "width", "height"):
                if report_item.get(field) != output_item[field]:
                    parser.error(f"technical report {field} is stale or does not match current files")
        if report.get("technical_pass") is True and report.get("errors"):
            parser.error("technical report is internally inconsistent")
        technical = "pass" if report.get("technical_pass") is True else "fail"

    executors = list(dict.fromkeys(["imagegen", *args.executor]))

    payload = {
        "source": source,
        "mode": args.mode,
        "photo_revival": True,
        "skills": skills,
        "executors": executors,
        "outputs": outputs,
        "qa": {
            "technical": technical,
            "visual": args.visual_status,
            "notes": args.note,
        },
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered + "\n", encoding="utf-8")
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
