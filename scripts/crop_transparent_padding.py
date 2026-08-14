#!/usr/bin/env python3
"""Crop known padded transparent rasters before recursive Figma scaling."""
from __future__ import annotations

import csv
import pathlib

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "master_list.tsv"
TARGETS = {
    "payments/indo/games-vouchers/battlefield-6",
    "payments/indo/games-vouchers/dead-by-daylight",
}


def main() -> int:
    with MASTER.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
    header = rows[0]
    idx = {name: index for index, name in enumerate(header)}
    changed = 0
    for row in rows[1:]:
        path = row[idx["figma_path"]]
        if path not in TARGETS or not row[idx["file_link"]]:
            continue
        asset = ROOT / row[idx["file_link"]]
        image = Image.open(asset).convert("RGBA")
        bbox = image.getchannel("A").getbbox()
        if not bbox:
            continue
        pad = max(4, round(max(image.size) * 0.02))
        left = max(0, bbox[0] - pad)
        top = max(0, bbox[1] - pad)
        right = min(image.width, bbox[2] + pad)
        bottom = min(image.height, bbox[3] + pad)
        cropped = image.crop((left, top, right, bottom))
        cropped.save(asset, format="PNG", optimize=True)
        ratio = cropped.width / cropped.height
        shape = "square" if 0.95 <= ratio <= 1.05 else "horizontal" if ratio > 1 else "vertical"
        row[idx["aspect"]] = f"{ratio:.2f}:1 ({shape}, {cropped.width}x{cropped.height})"
        row[idx["background"]] = "transparent"
        note = "Manual cleanup: transparent padding cropped so recursive 40px scaling uses the actual title-mark bounds."
        if note not in row[idx["notes"]]:
            row[idx["notes"]] = f"{row[idx['notes']]} {note}".strip()
        changed += 1

    with MASTER.open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, delimiter="\t", lineterminator="\n").writerows(rows)
    with (ROOT / "data/master_list.csv").open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(rows)
    print(f"cropped {changed} transparent raster(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
