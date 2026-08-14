#!/usr/bin/env python3
"""Replace unsafe bank candidates with curated vectors or neutral fallbacks.

The fetcher is intentionally broad so it can discover candidates. This script is
the narrow, human-reviewed pass: app-store icons, page thumbnails, stale marks,
and unresolved rows are either replaced with a matching corporate asset or get a
neutral name badge that cannot be mistaken for another bank.

Source repositories are kept outside this repository because their collections
have different licences. The checked-in assets are the result of this import;
the provenance is written into ``master_list.tsv`` and ``data/logo_audit.csv``.

Example (the source checkouts used for this audit):

    python3 scripts/curate_bank_assets.py --apply \
      --idn-root /tmp/idn-finlogos/package/dist/icons \
      --global-root /tmp/global-bank-logos/assets/bank/international-bank \
      --simple-icons-root /tmp/simple-icons/icons \
      --official-root /tmp/official-bank-assets

Without ``--apply`` the command only prints the planned changes.
"""
from __future__ import annotations

import argparse
import csv
import html
import pathlib
import re
import shutil
import sys
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "master_list.tsv"
ASSETS = ROOT / "assets"


@dataclass(frozen=True)
class Source:
    kind: str
    filename: str = ""
    url: str = ""
    licence: str = ""
    note: str = ""


def _idn(slug: str, note: str = "") -> Source:
    return Source(
        "idn-finlogos",
        f"{slug}.svg",
        f"https://cdn.jsdelivr.net/npm/idn-finlogos@2.5.0/dist/icons/{slug}.svg",
        "CC BY-NC 4.0 (collection; underlying trademarks remain with their owners)",
        note,
    )


def _global(filename: str, note: str = "") -> Source:
    return Source(
        "global-bank-logos",
        filename,
        "https://raw.githubusercontent.com/auraveni/global-bank-logos/main/"
        f"assets/bank/international-bank/{filename}",
        "MIT (collection; underlying trademarks remain with their owners)",
        note,
    )


def _simple(filename: str) -> Source:
    return Source(
        "simple-icons",
        filename,
        f"https://github.com/simple-icons/simple-icons/blob/develop/icons/{filename}",
        "CC0 1.0 (artwork collection; underlying trademarks remain with their owners)",
        "",
    )


def _official(filename: str, url: str, note: str) -> Source:
    return Source("official", filename, url, "Official brand asset", note)


def _fallback(reason: str) -> Source:
    return Source("fallback", note=reason)


# Indonesian rows are normalized to one vector family where the current bank
# identity is represented. Old package aliases are deliberately not used for
# OCBC NISP, KB Bank, or Bank DKI; those have current official/rebranded assets.
IDN_FILES = {
    "bank-mandiri": "mandiri",
    "bri": "bri",
    "bni": "bni",
    "bca": "bca",
    "btn": "btn",
    "bsi": "bsi",
    "cimb-niaga": "cimb-niaga",
    "danamon": "danamon",
    "permata": "permata",
    "panin": "paninbank",
    "maybank-indonesia": "maybank",
    "smbc-indonesia": "bank-smbc-indonesia",
    "mega": "mega",
    "btpn-syariah": "btpn-syariah",
    "sinarmas": "sinarmas",
    "bjb": "bank-bjb",
    "bank-jatim": "bank-bpd-jatim",
    "muamalat": "muamalat",
    "jago": "jago",
    "seabank": "seabank",
    "allo-bank": "allo",
    "superbank": "superbank",
    "neo-commerce": "bnc",
    "blu-bca": "blu-bca",
    "hsbc-indonesia": "hsbc",
    "uob-indonesia": "uob",
    "citibank-indonesia": "citibank",
    "bank-raya": "bank-raya",
    "amar-bank": "amar-bank",
    "krom-bank": "krom",
    "bank-saqu": "bank-saqu",
    "hibank": "hibank",
    "aladin-syariah": "aladin",
    "nobu-bank": "nobu",
    "mayapada": "bank-mayapada",
    "artha-graha": "bank-artha-graha-internasional",
    "maspion": "bank-maspion",
    "bumi-arta": "bank-bumi-artha",
    "mestika": "bank-mestika-dharma",
    "ganesha": "bank-ganesha",
    "ina-perdana": "bank-ina",
    "victoria": "bank-victoria",
    "capital": "bank-capital",
    "oke-indonesia": "ok-bank",
    "index-selindo": "bank-index-selindo",
    "multiarta-sentosa": "bank-mas",
    "sahabat-sampoerna": "bank-sahabat-sampoerna",
    "jtrust": "j-trust-bank",
    "mandiri-taspen": "mandiri-taspen",
    "bank-of-india-indonesia": "bank-of-india-indonesia",
    "sbi-indonesia": "sbi-indonesia",
    "qnb-indonesia": "qnb",
    "woori-saudara": "bank-woori-saudara",
    "shinhan-indonesia": "shinhan-bank",
    "keb-hana": "keb-hana-bank",
    "ibk-indonesia": "ibk-bank",
    "ctbc-indonesia": "ctbc-bank",
    "mizuho-indonesia": "mizuho-bank",
    "mufg-indonesia": "mufg",
    "resona-perdania": "bank-resona-perdania",
    "icbc-indonesia": "icbc",
    "bnp-paribas-indonesia": "bnp-paribas",
    "dbs-indonesia": "dbs",
    "anz-indonesia": "anz",
    "standard-chartered-indonesia": "standard-chartered",
    "bca-syariah": "bca-syariah",
    "mega-syariah": "mega-syariah",
    "panin-dubai-syariah": "panin-dubai-syariah",
    "bjb-syariah": "bank-bjb-syariah",
    "victoria-syariah": "bank-victoria-syariah",
    "bank-jateng": "bank-bpd-jateng",
    "bank-bpd-diy": "bank-bpd-diy",
    "bank-banten": "bank-bpd-banten",
    "bank-sumut": "bank-bpd-sumut",
    "bank-nagari": "bank-nagari",
    "bank-riau-kepri-syariah": "bank-bpd-riau-kepri-syariah",
    "bank-jambi": "bank-bpd-jambi",
    "bank-sumsel-babel": "bank-bpd-sumsel-babel",
    "bank-bengkulu": "bank-bengkulu",
    "bank-lampung": "bank-bpd-lampung",
    "bank-aceh-syariah": "bank-bpd-aceh",
    "bank-kalbar": "bank-bpd-kalbar",
    "bank-kalsel": "bank-bpd-kalsel",
    "bank-kalteng": "bank-bpd-kalteng",
    "bank-kaltimtara": "bank-bpd-kalimantan-timur",
    "bank-sulselbar": "bank-bpd-sulselbar",
    "bank-sulutgo": "bank-bpd-sulutgo",
    "bank-sulteng": "bank-bpd-sulteng",
    "bank-sultra": "bank-bpd-sultra",
    "bank-bpd-bali": "bank-bpd-bali",
    "bank-ntb-syariah": "bank-bpd-ntb-syariah",
    "bank-ntt": "bank-bpd-ntt",
    "bank-maluku-malut": "bank-bpd-maluku-malut",
    "bank-papua": "bank-bpd-papua",
}


SOURCES: dict[str, Source] = {
    **{f"banks/indo/{tail}": _idn(slug) for tail, slug in IDN_FILES.items()},
    "banks/indo/bank-dki": _idn("bank-jakarta", "Current public brand is Bank Jakarta; legal entity remains PT Bank DKI."),
    "banks/indo/ocbc-indonesia": _global("ocbc.svg", "Current OCBC mark; do not use the pre-2023 OCBC NISP asset."),
    "banks/indo/bank-of-china-indonesia": _global("boc.svg", "Shared BOC corporate mark; do not substitute a different Chinese bank."),
    "banks/indo/kb-bank": _official(
        "kb-bank.png",
        "https://www.kbbank.co.id/kb-logo-2.png",
        "Downloaded from the current KB Bank site; not the old KB Bukopin mark.",
    ),
    "banks/indo/kb-bank-syariah": _official(
        "kb-bank-syariah.png",
        "https://commons.wikimedia.org/wiki/File:KB_Bank_Syariah.png",
        "Current 2024 KB Bank Syariah logo; Commons record identifies the official site as source.",
    ),
    "banks/indo/kesejahteraan-ekonomi": _fallback(
        "No trustworthy current corporate artwork was found; retain a name-only badge until the entity is confirmed.",
    ),
    "banks/indo/commonwealth": _fallback(
        "The Indonesian bank merged into OCBC effective 1 September 2024; no standalone current primary mark retained.",
    ),
    "banks/indo/amar-bank": _fallback(
        "The available curated file embedded raster content; no clean corporate vector was verified.",
    ),
    # Singapore / Malaysia / Thailand / Philippines / Vietnam / Cambodia.
    "banks/sea/sg/dbs": _global("dbs.svg"),
    "banks/sea/sg/ocbc": _global("ocbc.svg"),
    "banks/sea/sg/uob": _global("uob.svg"),
    "banks/sea/sg/standard-chartered": _global("standard.svg"),
    "banks/sea/sg/maybank": _global("maybank.svg"),
    "banks/sea/my/maybank": _global("maybank.svg"),
    "banks/sea/my/cimb": _fallback("The downloaded file was an app/favicon asset, not a verified corporate primary mark."),
    "banks/sea/my/public-bank": _fallback("The available candidate was a dated anniversary variant; do not ship it as the current primary mark."),
    "banks/sea/my/bank-islam": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/sea/th/bangkok-bank": _fallback("Only an app-store icon was available in the fetched set; no matching corporate vector was found in the authoritative fallback set."),
    "banks/sea/th/kasikornbank": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/sea/th/krungthai": _global("krungthai.svg"),
    "banks/sea/th/krungsri": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/sea/th/scb": _official(
        "scb-th.svg",
        "https://commons.wikimedia.org/wiki/File%3ASiam_Commercial_Bank_Logo.svg",
        "Current Siam Commercial Bank logo; source is the bank's 2022 annual report via Commons.",
    ),
    "banks/sea/th/ttb": _official(
        "ttb-th.svg",
        "https://www.ttbbank.com/th/about-us/ttb-logo",
        "Official current ttb corporate mark transcribed from the bank's inline SVG; transparent mark only, no page background or slogan.",
    ),
    "banks/sea/ph/bdo": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/sea/ph/landbank": _fallback("The available candidate was a small favicon; no corporate lockup was verified."),
    "banks/sea/ph/security-bank": _fallback("The available candidate was an app/favicon asset, not a verified corporate primary mark."),
    "banks/sea/ph/unionbank": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/sea/vn/vietinbank": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/sea/vn/bidv": _fallback("The downloaded candidate was an insurance/banner image, not the BIDV logo."),
    "banks/sea/vn/vpbank": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/sea/kh/aba-bank": _fallback("Only an app-store icon was available in the fetched set."),
    # International corridor banks.
    "banks/international/gb/hsbc": _global("hsbc.svg"),
    "banks/international/us/citibank": _global("citi.svg"),
    "banks/international/gb/standard-chartered": _global("standard.svg"),
    "banks/international/us/jpmorgan-chase": _global("chase.svg"),
    "banks/international/us/bank-of-america": _global("boa.svg"),
    "banks/international/us/wells-fargo": _global("wells.svg"),
    "banks/international/us/capital-one": _fallback("The downloaded candidate was Paze, a different Capital One product."),
    "banks/international/us/pnc-bank": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/international/us/chime": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/international/gb/barclays": _global("barclays.svg"),
    "banks/international/gb/lloyds-bank": _fallback("The available candidate was an app/favicon asset, not a verified corporate primary mark."),
    "banks/international/gb/natwest": _global("natwest.svg"),
    "banks/international/gb/monzo": _simple("monzo.svg"),
    "banks/international/de/deutsche-bank": _global("deutsche.svg"),
    "banks/international/de/commerzbank": _simple("commerzbank.svg"),
    "banks/international/de/n26": _fallback("The available candidate was the N26 app tile; no corporate primary mark was verified."),
    "banks/international/fr/bnp-paribas": _global("bnp.svg"),
    "banks/international/fr/societe-generale": _global("societe-generale.svg"),
    "banks/international/fr/credit-agricole": _fallback("The downloaded candidate was a YouTube logo; CACIB is a different corporate entity."),
    "banks/international/nl/ing": _fallback("Only an app-store icon was available in the fetched set."),
    "banks/international/nl/abn-amro": _global("abn-amro.svg"),
    "banks/international/nl/rabobank": _global("rabobank.svg"),
    "banks/international/cn/bank-of-china": _global("boc.svg"),
    "banks/international/cn/icbc": _global("icbc.svg"),
    "banks/international/cn/china-construction-bank": _fallback("No matching corporate vector was found in the authoritative fallback set."),
    "banks/international/au/commonwealth-bank": _global("commonwealth.svg"),
    "banks/international/au/westpac": _global("westpac.svg"),
    "banks/international/au/anz-australia": _global("anz.svg"),
    "banks/international/au/nab": _global("nab.svg"),
    "banks/international/ca/rbc": _global("rbc.svg"),
    "banks/international/ca/td-bank": _global("td.svg"),
    "banks/international/jp/mufg-bank": _global("mufg.svg", "Current MUFG mark; replaces the anniversary variant."),
    "banks/international/jp/smbc": _global("smbc.svg"),
    "banks/international/jp/japan-post-bank": _fallback("The downloaded candidate was a baseball promotion image, not the corporate mark."),
    "banks/international/kr/kb-kookmin-bank": _fallback("The available vector includes a full-canvas background; no transparent corporate lockup was verified."),
    "banks/international/kr/shinhan-bank": _global("shinhan.svg"),
    "banks/international/kr/woori-bank": _global("woori.svg"),
    "banks/international/hk/hang-seng-bank": _fallback("No matching corporate vector was found in the authoritative fallback set."),
    "banks/international/hk/bank-of-china-hk": _global("boc.svg"),
}


def _abbreviation(name: str, path: str) -> str:
    """Make a neutral, readable identifier for a fallback badge."""
    words = re.findall(r"[A-Za-z0-9]+", name)
    words = [w for w in words if w.lower() not in {"bank", "the", "of", "and", "indonesia"}]
    if len(words) >= 2:
        abbr = "".join(w[0] for w in words[:4]).upper()
    elif words:
        abbr = words[0][:4].upper()
    else:
        abbr = pathlib.PurePosixPath(path).name[:4].upper()
    return abbr[:5] or "BANK"


def _fallback_svg(name: str, path: str) -> str:
    abbr = html.escape(_abbreviation(name, path))
    label = html.escape(name)
    # Intentionally monochrome and generic: this is a distinguishable label
    # badge, not a substitute brand mark or a guessed corporate colour.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 72" role="img" aria-labelledby="title desc">
  <title id="title">{label} neutral fallback</title>
  <desc id="desc">No verified logo artwork. Display the institution name alongside this neutral badge.</desc>
  <rect x="1" y="1" width="238" height="70" rx="10" fill="#F3F4F6" stroke="#9CA3AF" stroke-width="2"/>
  <text x="120" y="45" text-anchor="middle" fill="#374151" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700" letter-spacing="1">{abbr}</text>
</svg>
'''


def _svg_dimensions(text: str) -> tuple[float, float]:
    match = re.search(r'viewBox\s*=\s*["\']([\d.eE+\-\s,]+)["\']', text)
    if match:
        nums = [float(n) for n in re.split(r"[\s,]+", match.group(1).strip()) if n]
        if len(nums) == 4 and nums[2] > 0 and nums[3] > 0:
            return nums[2], nums[3]
    return 1.0, 1.0


def _describe_aspect(width: float, height: float) -> str:
    ratio = width / height if height else 1.0
    if 0.95 <= ratio <= 1.05:
        shape = "square"
    elif ratio > 1:
        shape = "horizontal"
    else:
        shape = "vertical"
    pretty = f"{ratio:.2f}:1" if ratio >= 1 else f"1:{1 / ratio:.2f}"
    return f"{pretty} ({shape}, {int(width)}x{int(height)})"


def _source_path(source: Source, roots: dict[str, pathlib.Path]) -> pathlib.Path | None:
    if source.kind == "fallback":
        return None
    root = roots.get(source.kind)
    return root / source.filename if root else None


def _append_note(old: str, addition: str) -> str:
    old = old.strip()
    return old if addition in old else f"{old} {addition}".strip()


def apply(roots: dict[str, pathlib.Path], dry_run: bool) -> tuple[int, int]:
    with MASTER.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
        fields = rows[0].keys() if rows else []

    missing_sources: list[str] = []
    changed = 0
    fallbacks = 0
    for row in rows:
        path = row["figma_path"]
        source = SOURCES.get(path)
        if source is None:
            continue
        if row["status"].lower().startswith("flagged - excluded") or row["country"] == "mm":
            continue
        source_path = _source_path(source, roots)
        if source_path is not None and not source_path.exists():
            missing_sources.append(f"{path}: {source.kind}:{source.filename} ({source_path})")
            continue

        target_dir = ASSETS / path
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        for old in target_dir.parent.glob(target_dir.name + ".*"):
            if old.is_file() and old.suffix.lower() not in {".md", ".txt"}:
                if dry_run:
                    print(f"  remove {old.relative_to(ROOT)}")
                else:
                    old.unlink()

        if source.kind == "fallback":
            target = target_dir.with_suffix(".svg")
            payload = _fallback_svg(row["institution"], path).encode("utf-8")
            fallbacks += 1
        else:
            target = target_dir.with_suffix(source_path.suffix.lower())
            payload = source_path.read_bytes()

        if dry_run:
            print(f"  {'fallback' if source.kind == 'fallback' else 'replace'} {path} -> {target.name}")
        else:
            target.write_bytes(payload)

        if source.kind == "fallback":
            aspect = "3.33:1 (horizontal, 240x72)"
            variant = "fallback"
            reason = "Neutral name badge; no brand identity inferred"
            bg = "transparent"
            row["source_url"] = ""
            row["notes"] = _append_note(row["notes"], f"Asset audit 2026-08: neutral fallback badge only; {source.note} Use institution text alongside it; do not use this as a brand mark.")
        else:
            if target.suffix.lower() == ".svg":
                text = payload.decode("utf-8", "replace")
                width, height = _svg_dimensions(text)
            else:
                # The two official PNGs are known from their published native dimensions.
                width, height = (413, 74) if target.name == "kb-bank.png" else (2305, 834)
            aspect = _describe_aspect(width, height)
            variant = "wordmark" if width / height > 1.35 else "icon"
            reason = "Curated corporate vector/lockup for compact UI" if target.suffix.lower() == ".svg" else "Official corporate raster lockup; vector not available"
            bg = "transparent"
            row["source_url"] = source.url
            source_note = f"Asset audit 2026-08: replaced automated candidate with {source.kind} artwork ({source.licence})."
            if source.note:
                source_note += f" {source.note}"
            row["notes"] = _append_note(row["notes"], source_note)

        row["variant"] = variant
        row["variant_reason"] = reason
        row["aspect"] = aspect
        row["background"] = bg
        row["file_link"] = str(target.relative_to(ROOT))
        changed += 1

    if missing_sources:
        print("Missing source files:", file=sys.stderr)
        for line in missing_sources:
            print(f"  {line}", file=sys.stderr)
        return changed, fallbacks
    if not dry_run:
        with MASTER.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        with (ROOT / "data" / "master_list.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    return changed, fallbacks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write assets and master-list changes")
    ap.add_argument("--idn-root", type=pathlib.Path, required=True, help="idn-finlogos dist/icons directory")
    ap.add_argument("--global-root", type=pathlib.Path, required=True, help="global-bank-logos international-bank directory")
    ap.add_argument("--simple-icons-root", type=pathlib.Path, required=True, help="simple-icons icons directory")
    ap.add_argument("--official-root", type=pathlib.Path, required=True, help="directory containing kb-bank.png and kb-bank-syariah.png")
    args = ap.parse_args()
    roots = {
        "idn-finlogos": args.idn_root,
        "global-bank-logos": args.global_root,
        "simple-icons": args.simple_icons_root,
        "official": args.official_root,
    }
    changed, fallbacks = apply(roots, dry_run=not args.apply)
    print(f"planned/changed: {changed}; neutral fallbacks: {fallbacks}; mode: {'apply' if args.apply else 'dry-run'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
