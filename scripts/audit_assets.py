#!/usr/bin/env python3
"""Audit bank and payment logo assets against the small-UI quality contract.

The audit is deliberately conservative about provenance and structure. It can
prove that an asset is a usable file, scalable or large enough for a 24–48px
UI, free of obvious embedded/page imagery, and not an app-store candidate. It
cannot prove trademark ownership or that a logo is the latest artwork; those
remain explicit manual-review fields in the generated CSV.

    uv run --with Pillow python scripts/audit_assets.py --category bank --check
    uv run --with Pillow python scripts/audit_assets.py --category bank --write
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import pathlib
import re
import sys
from collections import defaultdict
from typing import Iterable

try:
    from PIL import Image
except ImportError:  # pragma: no cover - exercised only without requirements installed
    Image = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "master_list.tsv"
REPORT = ROOT / "data" / "fetch_report.csv"
DEFAULT_OUTPUT = ROOT / "data" / "logo_audit.csv"

MIN_RASTER_EDGE = 128
PREFERRED_RASTER_EDGE = 256
MIN_ASPECT = 0.2
MAX_ASPECT = 8.0


def _split_values(value: str) -> list[str]:
    return [x.strip() for x in value.split(";") if x.strip()]


def _aspect(width: float, height: float) -> str:
    ratio = width / height if height else 1.0
    if 0.95 <= ratio <= 1.05:
        shape = "square"
    elif ratio > 1:
        shape = "horizontal"
    else:
        shape = "vertical"
    pretty = f"{ratio:.2f}:1" if ratio >= 1 else f"1:{1 / ratio:.2f}"
    return f"{pretty} ({shape}, {int(width)}x{int(height)})"


def _svg_size(text: str) -> tuple[float, float, bool]:
    box = re.search(r"viewBox\s*=\s*[\"']([\d.eE+\-\s,]+)[\"']", text)
    if box:
        nums = [float(n) for n in re.split(r"[\s,]+", box.group(1).strip()) if n]
        if len(nums) == 4 and nums[2] > 0 and nums[3] > 0:
            return nums[2], nums[3], True
    width = re.search(r"\bwidth\s*=\s*[\"']([\d.]+)", text)
    height = re.search(r"\bheight\s*=\s*[\"']([\d.]+)", text)
    if width and height and float(width.group(1)) > 0 and float(height.group(1)) > 0:
        return float(width.group(1)), float(height.group(1)), False
    return 0.0, 0.0, False


def _raster_info(path: pathlib.Path) -> tuple[int, int, bool, list[str], list[str]]:
    if Image is None:
        raise RuntimeError("Pillow is required; install requirements.txt or run with uv run --with Pillow")
    issues: list[str] = []
    warnings: list[str] = []
    try:
        image = Image.open(path)
        image.load()
    except Exception as exc:
        return 0, 0, False, [f"unreadable-raster:{type(exc).__name__}"], warnings

    width, height = image.size
    has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
    transparent = False
    if has_alpha:
        try:
            transparent = image.convert("RGBA").getchannel("A").getextrema()[0] < 255
        except Exception:
            warnings.append("alpha-channel-not-measurable")

    longest = max(width, height)
    if longest < MIN_RASTER_EDGE:
        issues.append(f"low-resolution:{longest}px")
    elif longest < PREFERRED_RASTER_EDGE:
        warnings.append(f"low-headroom:{longest}px; 256px preferred")
    if not transparent:
        issues.append("opaque-background")

    # A transparent canvas with a very small content box is usually an asset
    # exported with excessive padding; it will become unreadable in a chip.
    if transparent:
        alpha_bbox = image.convert("RGBA").getchannel("A").getbbox()
        if alpha_bbox:
            bbox_width = alpha_bbox[2] - alpha_bbox[0]
            bbox_height = alpha_bbox[3] - alpha_bbox[1]
            if bbox_width < width * 0.55 or bbox_height < height * 0.55:
                warnings.append("excessive-transparent-padding")
    return width, height, transparent, issues, warnings


def analyse_asset(path: pathlib.Path, role: str = "primary") -> dict[str, object]:
    """Inspect one asset; kept public for focused unit tests and tooling."""
    suffix = path.suffix.lower()
    issues: list[str] = []
    warnings: list[str] = []
    asset_type = "unknown"
    width = height = 0.0
    transparent = False

    if not path.is_file():
        issues.append("missing-file")
    elif suffix == ".svg":
        asset_type = "vector"
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        width, height, has_viewbox = _svg_size(text)
        transparent = True
        if "<svg" not in lower:
            issues.append("invalid-svg")
        if not has_viewbox:
            issues.append("svg-missing-viewbox")
        if "<image" in lower:
            issues.append("svg-embedded-raster")
        if role != "fallback" and "<text" in lower:
            issues.append("svg-embedded-text")
        if re.search(r"(?:href|xlink:href)\s*=\s*[\"'](?:https?:|//)", lower):
            issues.append("svg-external-reference")
        if re.search(r"@import|url\(\s*[\"']?(?:https?:|//)", lower):
            issues.append("svg-external-style")
        # Full-canvas fills are allowed on fallbacks only. A branded logo that
        # needs a baked rectangle will fail on a dark/light UI background.
        # Many clean icon sets use a full-viewBox rect only as a clip path.
        # Remove those definitions before looking for a painted background.
        painted_content = re.sub(r"<clippath\b.*?</clippath>", "", lower, flags=re.DOTALL)
        if role != "fallback":
            for rect in re.findall(r"<rect\b[^>]*>", painted_content):
                # Exporters commonly add an explicit transparent canvas rect;
                # class="f" is the convention used by the SCB source below.
                rect_class = re.search(r"\bclass\s*=\s*[\"']([^\"']+)[\"']", rect)
                class_is_non_painting = bool(
                    rect_class
                    and re.search(
                        rf"\.{re.escape(rect_class.group(1).split()[0])}\s*\{{[^}}]*fill\s*:\s*none",
                        lower,
                    )
                )
                non_painting = (
                    re.search(r"\bclass\s*=\s*[\"'][^\"']*\bf\b[^\"']*[\"']", rect)
                    or re.search(r"\bfill\s*=\s*[\"']none[\"']", rect)
                    or re.search(r"\bstyle\s*=\s*[\"'][^\"']*fill\s*:\s*none", rect)
                    or re.search(r"\bopacity\s*=\s*[\"']0(?:\.0*)?[\"']", rect)
                    or re.search(r"\bfill-opacity\s*=\s*[\"']0(?:\.0*)?[\"']", rect)
                    or class_is_non_painting
                )
                if non_painting:
                    continue
                if re.search(
                    r"width\s*=\s*[\"'](?:100%|\d+)[\"'][^>]*height\s*=\s*[\"'](?:100%|\d+)[\"']",
                    rect,
                ):
                    warnings.append("possible-svg-background-rectangle")
                    break
    elif suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        asset_type = "raster"
        width, height, transparent, issues, warnings = _raster_info(path)
    else:
        issues.append(f"unsupported-extension:{suffix or 'none'}")

    if width and height:
        ratio = width / height
        if ratio < MIN_ASPECT or ratio > MAX_ASPECT:
            warnings.append(f"extreme-aspect:{ratio:.2f}:1")
    return {
        "asset_type": asset_type,
        "width": int(width),
        "height": int(height),
        "aspect": _aspect(width, height) if width and height else "TBD",
        "transparent": "yes" if transparent else "no",
        "issues": issues,
        "warnings": warnings,
    }


def _source_tier(row: dict[str, str], report: dict[str, dict[str, str]]) -> str:
    if row.get("variant") == "fallback":
        return "fallback"
    url = row.get("source_url", "").lower()
    if "idn-finlogos" in url:
        return "curated-idn"
    if "auraveni/global-bank-logos" in url:
        return "curated-global"
    if "simple-icons" in url or "simpleicons.org" in url:
        return "curated-simple-icons"
    if any(host in url for host in ("svgrepo.com", "seeklogo.com", "stickpng.com", "xlogo.org", "zonalogo.com")):
        return "curated-vector"
    if "folaplay.com" in url:
        return "official-or-brand-site"
    if any(host in url for host in (
        "telkomsel.com", "indosatooredoo.com", "im3-img.indosatooredoo.com", "axis.co.id",
        "tri.co.id", "biznetnetworks.com", "static.ext.dp.xl.co.id", "poppo.com",
        "idn.app", "bstarstatic.com", "bigo.tv", "chamet.com", "honorofkings.com",
        "blood-strike.com", "pointblank.id", "megaxus.com", "freefiremobile.com",
        "nintendo.com", "f1manager.com", "baznas.go.id", "fm2.galasports.com",
        "magicchessgogo.com", "youngjoygame.com", "ea.com", "drop-assets.ea.com",
    )):
        return "official-or-brand-site"
    if "kbbank.co.id" in url or "kbbanksyariah" in url or "commons.wikimedia.org" in url:
        return "official-or-authoritative"
    if "mzstatic.com" in url or "itunes.apple.com" in url:
        return "app-store"
    if re.search(r"favicon|apple-touch|\.ico(?:$|[?#])", url):
        return "favicon"
    detail = report.get(row.get("figma_path", ""), {}).get("detail", "").lower()
    if "app-store" in detail or "app-icon" in detail:
        return "app-store"
    if "brand-site" in detail or "brand-press" in detail:
        return "official-or-brand-site"
    return "unknown"


def _provenance_flags(row: dict[str, str], tier: str, report: dict[str, dict[str, str]]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    url = row.get("source_url", "").lower()
    detail = report.get(row.get("figma_path", ""), {}).get("detail", "").lower()
    haystack = f"{url} {detail}"
    policy_category = row.get("category") in {"bank", "payment"}
    if policy_category and (tier == "app-store" or "mzstatic.com" in url or "itunes.apple.com" in url):
        issues.append("app-store-source")
    if policy_category and row.get("variant") == "app-icon":
        issues.append("mobile-app-role")
    if policy_category and any(token in haystack for token in ("og:image", "social", "thumbnail", "paze_logo", "youtube-logo", "banker-with", "call.png", "apple-touch", "favicon")):
        issues.append("page-or-social-image")
    if policy_category and tier == "favicon":
        warnings.append("favicon-source; replace with corporate artwork when available")
    if not row.get("source_url") and tier != "fallback":
        warnings.append("unattributed-source")
    return issues, warnings


def _sha(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_rows() -> list[dict[str, str]]:
    with MASTER.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _read_report() -> dict[str, dict[str, str]]:
    if not REPORT.exists():
        return {}
    with REPORT.open(encoding="utf-8", newline="") as fh:
        return {row["figma_path"]: row for row in csv.DictReader(fh)}


def audit_rows(rows: Iterable[dict[str, str]], category: str = "bank") -> list[dict[str, str]]:
    report = _read_report()
    selected = [row for row in rows if not category or row.get("category") == category]
    records: list[dict[str, str]] = []
    hash_to_paths: defaultdict[str, list[str]] = defaultdict(list)

    for row in selected:
        path_text = row.get("file_link", "")
        path = ROOT / path_text if path_text else ROOT / "__missing__"
        is_skipped = "Excluded" in row.get("status", "") or row.get("country") == "mm"
        role = row.get("variant", "primary")
        measured = analyse_asset(path, role)
        tier = _source_tier(row, report)
        issues = list(measured["issues"])
        warnings = list(measured["warnings"])
        provenance_issues, provenance_warnings = _provenance_flags(row, tier, report)
        issues.extend(provenance_issues)
        warnings.extend(provenance_warnings)

        digest = _sha(path) if path.is_file() else ""
        if digest:
            hash_to_paths[digest].append(row["figma_path"])

        if is_skipped and not path.is_file():
            status = "skipped"
        elif role == "fallback":
            status = "fallback"
        elif issues:
            status = "needs-replacement"
        elif warnings:
            status = "review"
        else:
            status = "accepted"

        records.append({
            "figma_path": row.get("figma_path", ""),
            "institution": row.get("institution", ""),
            "asset_path": path_text,
            "status": status,
            "identity_status": "manual confirmation still required",
            "asset_type": str(measured["asset_type"]),
            "width": str(measured["width"]),
            "height": str(measured["height"]),
            "aspect": str(measured["aspect"]),
            "transparent": str(measured["transparent"]),
            "source_tier": tier,
            "source_url": row.get("source_url", ""),
            "issues": "; ".join(issues),
            "warnings": "; ".join(warnings),
            "sha256": digest,
            "duplicate_of": "",
        })

    for record in records:
        digest = record["sha256"]
        paths = hash_to_paths.get(digest, []) if digest else []
        if len(paths) > 1:
            record["duplicate_of"] = "; ".join(p for p in paths if p != record["figma_path"])
            # Shared marks across country/company rows are expected for global
            # banking groups; keep the fact in the report without failing the
            # asset unless the source policy already failed it.
            if "exact-duplicate" not in record["warnings"]:
                record["warnings"] = "; ".join(filter(None, [record["warnings"], "exact-duplicate/shared-mark"]))
            if record["status"] == "accepted":
                record["status"] = "review"
    return records


FIELDNAMES = [
    "figma_path", "institution", "asset_path", "status", "identity_status",
    "asset_type", "width", "height", "aspect", "transparent", "source_tier",
    "source_url", "issues", "warnings", "sha256", "duplicate_of",
]


def write_report(records: list[dict[str, str]], output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--category", default="bank", help="category to audit (default: bank); use payment for GoPay rows; empty means all")
    ap.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--write", action="store_true", help="write the CSV report (also implied by --check)")
    ap.add_argument("--check", action="store_true", help="fail on missing files or policy violations")
    args = ap.parse_args()

    records = audit_rows(_read_rows(), args.category)
    if args.write or args.check:
        write_report(records, args.output)

    counts: defaultdict[str, int] = defaultdict(int)
    for record in records:
        counts[record["status"]] += 1
    print(f"audited {len(records)} {args.category or 'all'} row(s): " + ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    if args.write or args.check:
        print(f"report written to {args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output}")

    if args.check:
        failures = [r for r in records if r["status"] == "needs-replacement"]
        if failures:
            print("quality check failed:", file=sys.stderr)
            for record in failures:
                print(f"  {record['figma_path']}: {record['issues']}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
