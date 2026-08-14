#!/usr/bin/env python3
"""Repair cached SVGs that declare width/height but no viewBox.

Those exports are still vectors, but Figma can interpret their coordinate
system inconsistently when they are recursively rescaled into 40px wrappers.
This small, idempotent pass adds a matching 0 0 width height viewBox and leaves
all artwork untouched.
"""
from __future__ import annotations

import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "master_list.tsv"


def normalize(path: pathlib.Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "viewbox" in text.lower():
        return False
    opening = re.search(r"<svg\b[^>]*>", text, flags=re.IGNORECASE | re.DOTALL)
    if not opening:
        return False
    tag = opening.group(0)
    width = re.search(r"\bwidth\s*=\s*[\"']([0-9.]+)", tag, flags=re.IGNORECASE)
    height = re.search(r"\bheight\s*=\s*[\"']([0-9.]+)", tag, flags=re.IGNORECASE)
    if not (width and height and float(width.group(1)) > 0 and float(height.group(1)) > 0):
        return False
    viewbox = f' viewBox="0 0 {width.group(1)} {height.group(1)}"'
    replacement = tag[:-1] + viewbox + ">"
    path.write_text(text[:opening.start()] + replacement + text[opening.end():], encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    seen: set[pathlib.Path] = set()
    with MASTER.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row.get("category") != "payment":
                continue
            value = row.get("file_link", "")
            path = ROOT / value
            if path.suffix.lower() != ".svg" or path in seen or not path.is_file():
                continue
            seen.add(path)
            if normalize(path):
                changed += 1
                print(f"normalized {path.relative_to(ROOT)}")
    print(f"normalized {changed} SVG asset(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
