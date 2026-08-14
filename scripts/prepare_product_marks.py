#!/usr/bin/env python3
"""Prepare exceptional product marks that are published inside larger artwork.

The GoPay catalogue occasionally exposes a current product only through its
official launch artwork. This script keeps the source URL in the master list,
but extracts the actual title lockup into a transparent raster before import;
player photography, card art, and baked backgrounds never enter the library.
"""
from __future__ import annotations

import csv
import base64
import io
import pathlib
import re
import subprocess
import warnings

from PIL import Image, ImageFilter
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "master_list.tsv"
FOOTBALL = ROOT / "assets/payments/indo/games-vouchers/football-dream-be-a-pro.png"
BIZNET = ROOT / "assets/payments/indo/internet-tv/biznet.png"
MLBB = ROOT / "assets/payments/indo/games-vouchers/mobile-legends.png"
PUBG = ROOT / "assets/payments/indo/games-vouchers/pubg-mobile.png"
CBN = ROOT / "assets/payments/indo/internet-tv/cbn.png"
TRANSVISION = ROOT / "assets/payments/indo/internet-tv/transvision.png"
PEGADAIAN = ROOT / "assets/payments/indo/utilities-bills/pegadaian.svg"
HOME_CREDIT = ROOT / "assets/payments/indo/finance-insurance/home-credit.svg"
BFI = ROOT / "assets/payments/indo/finance-insurance/bfi-finance.png"
BFI_SVG = ROOT / "assets/payments/indo/finance-insurance/bfi-finance.svg"
OTO_MOTOR = ROOT / "assets/payments/indo/finance-insurance/oto-kredit-motor.png"
OTO_MOBIL = ROOT / "assets/payments/indo/finance-insurance/oto-kredit-mobil.png"
SUZUKI_FINANCE = ROOT / "assets/payments/indo/finance-insurance/suzuki-finance.png"
SAMSAT_JATENG = ROOT / "assets/payments/indo/government-public/samsat-jateng.png"
SAMSAT_JATIM = ROOT / "assets/payments/indo/government-public/samsat-jatim.png"
SPIL = ROOT / "assets/payments/indo/education-invoicing/spil.svg"
PAPER_ID = ROOT / "assets/payments/indo/education-invoicing/paper-id.svg"
ALFAMIDI = ROOT / "assets/minimarkets/indo/alfamidi.png"

warnings.filterwarnings("ignore", message="Unverified HTTPS request")


def _update_master(
    target: str,
    asset: pathlib.Path,
    note: str,
    *,
    source_url: str | None = None,
    background: str | None = None,
) -> None:
    with MASTER.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
    header = rows[0]
    idx = {name: index for index, name in enumerate(header)}
    if asset.suffix.lower() == ".svg":
        svg = asset.read_text(encoding="utf-8", errors="replace")
        box = re.search(r'''viewBox\s*=\s*["']([\d.\-+eE\s,]+)["']''', svg)
        if box:
            nums = [float(n) for n in re.split(r"[\s,]+", box.group(1).strip()) if n]
            width, height = int(nums[2]), int(nums[3])
        else:
            width = int(float(re.search(r'''\bwidth\s*=\s*["']([\d.]+)''', svg).group(1)))
            height = int(float(re.search(r'''\bheight\s*=\s*["']([\d.]+)''', svg).group(1)))
    else:
        image = Image.open(asset).convert("RGBA")
        width, height = image.width, image.height
    ratio = width / height
    shape = "square" if 0.95 <= ratio <= 1.05 else "horizontal" if ratio > 1 else "vertical"
    for row in rows[1:]:
        if row[idx["figma_path"]] != target:
            continue
        row[idx["aspect"]] = f"{ratio:.2f}:1 ({shape}, {width}x{height})"
        row[idx["background"]] = background or "transparent"
        row[idx["source_url"]] = source_url or row[idx["source_url"]]
        row[idx["file_link"]] = str(asset.relative_to(ROOT))
        if note not in row[idx["notes"]]:
            row[idx["notes"]] = f"{row[idx['notes']]} {note}".strip()
        break
    with MASTER.open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, delimiter="\t", lineterminator="\n").writerows(rows)
    with (ROOT / "data/master_list.csv").open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(rows)


def _get(url: str) -> bytes:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "logo-library-research/1.0"},
            timeout=30,
            verify=False,
        )
        response.raise_for_status()
        return response.content
    except requests.RequestException:
        return subprocess.check_output(
            ["/usr/bin/curl", "-k", "-L", "--retry", "2", "--retry-all-errors",
             "-fsSL", "-A", "logo-library-research/1.0", url],
            timeout=45,
        )


def _remove_light_pixels(image: Image.Image, threshold: int = 245) -> Image.Image:
    """Remove light raster canvas pixels while preserving enclosed white logo details."""
    image = image.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a and min(r, g, b) >= threshold and max(r, g, b) - min(r, g, b) <= 18:
                pixels[x, y] = (r, g, b, 0)
    bbox = image.getchannel("A").getbbox()
    return image.crop(bbox) if bbox else image


def _write_raster(target: str, asset: pathlib.Path, data: bytes, note: str, source_url: str) -> None:
    asset.parent.mkdir(parents=True, exist_ok=True)
    asset.write_bytes(data)
    _update_master(target, asset, note, source_url=source_url)


def cbn_wordmark() -> None:
    image = Image.open(CBN)
    # The official raster is a rounded tile with a light-grey border rather
    # than a genuinely transparent wordmark. Remove that border as well as
    # the white canvas; the CBN mark itself is blue and dark charcoal.
    cleaned = _remove_light_pixels(image, threshold=200)
    cleaned.save(CBN, format="PNG", optimize=True)
    _update_master(
        "payments/indo/internet-tv/cbn",
        CBN,
        "Manual cleanup: removed the rounded white app-style canvas from the official CBN mark; retained the provider symbol and wordmark.",
    )


def home_credit_wordmark() -> None:
    """Extract the official inline SVG wordmark from Home Credit's current site shell."""
    html = _get("https://www.homecredit.co.id").decode("utf-8", "replace")
    match = re.search(r"data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)\" alt=\"logo\"", html)
    if not match:
        raise RuntimeError("Home Credit inline SVG wordmark was not found")
    HOME_CREDIT.parent.mkdir(parents=True, exist_ok=True)
    HOME_CREDIT.write_bytes(base64.b64decode(match.group(1)))
    _update_master(
        "payments/indo/finance-insurance/home-credit",
        HOME_CREDIT,
        "Manual source override: extracted the official current Home Credit SVG wordmark from the brand site; replaced a raster/logo-card candidate.",
        source_url="https://www.homecredit.co.id",
    )


def bfi_wordmark() -> None:
    """Keep the official BFI logo symbol without its white raster canvas."""
    # The official site exposes a compact 60px raster. A traced vector derived
    # from that exact cleaned mark is checked in for the library, so never
    # switch the master row back to the low-headroom raster on reruns.
    if BFI_SVG.exists():
        _update_master(
            "payments/indo/finance-insurance/bfi-finance",
            BFI_SVG,
            "Manual vectorization: traced the clean official BFI raster wordmark after removing its white canvas; no app tile or page chrome was added.",
            source_url="https://www.bfi.co.id/static/images/logo-bfi.png",
        )
        return
    image = Image.open(io.BytesIO(_get("https://www.bfi.co.id/static/images/logo-bfi.png"))).convert("RGBA")
    image = _remove_light_pixels(image, threshold=242)
    BFI.parent.mkdir(parents=True, exist_ok=True)
    image.save(BFI, format="PNG", optimize=True)
    _update_master(
        "payments/indo/finance-insurance/bfi-finance",
        BFI,
        "Manual cleanup: removed the white raster canvas from the official BFI mark so it does not become a dark-background tile.",
        source_url="https://www.bfi.co.id/static/images/logo-bfi.png",
    )


def transvision_wordmark() -> None:
    """Remove the award badge bundled beside the official Transvision mark."""
    image = Image.open(TRANSVISION).convert("RGBA")
    # The official site asset places a Superbrands award badge beside the
    # actual wordmark. The badge is campaign/editorial artwork, not part of
    # the provider identity used in a biller picker.
    image = image.crop((0, 0, min(image.width, 321), image.height))
    bbox = image.getchannel("A").getbbox()
    if bbox:
        image = image.crop(bbox)
    image.save(TRANSVISION, format="PNG", optimize=True)
    _update_master(
        "payments/indo/internet-tv/transvision",
        TRANSVISION,
        "Manual cleanup: removed the Superbrands award badge from the official Transvision site asset; retained only the provider wordmark.",
        source_url="https://www.transvision.co.id/img/icons/transvision_color.png",
    )


def pegadaian_vector_cleanup() -> None:
    """Remove an unused Inkscape page clip that Figma imports as giant artwork."""
    text = PEGADAIAN.read_text(encoding="utf-8", errors="replace")
    cleaned = re.sub(r"\s*<g\b[^>]*id=\"g224\"[^>]*>.*?</g>\s*</g>\s*</g>", "", text, count=1, flags=re.DOTALL)
    cleaned = re.sub(r"\s*<clipPath\b.*?</clipPath>", "", cleaned, count=1, flags=re.DOTALL)
    if cleaned != text:
        PEGADAIAN.write_text(cleaned, encoding="utf-8")
    _update_master(
        "payments/indo/utilities-bills/pegadaian",
        PEGADAIAN,
        "Manual SVG cleanup: removed an unused Inkscape page clip that imported as a giant out-of-frame descendant; provider artwork remains vector-only.",
    )


def oto_wordmarks() -> None:
    """Extract the high-resolution official OTO logo raster from its SVG wrapper."""
    svg = _get("https://asset.oto.co.id/external/cfind/source/images/general/oto-logo.svg").decode("utf-8", "replace")
    match = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", svg)
    if not match:
        raise RuntimeError("OTO embedded logo raster was not found")
    data = base64.b64decode(match.group(1))
    for target, asset in [
        ("payments/indo/finance-insurance/oto-kredit-motor", OTO_MOTOR),
        ("payments/indo/finance-insurance/oto-kredit-mobil", OTO_MOBIL),
    ]:
        _write_raster(
            target,
            asset,
            data,
            "Manual cleanup: extracted the high-resolution official OTO provider mark from its SVG wrapper; embedded raster was rejected as an SVG source.",
            "https://asset.oto.co.id/external/cfind/source/images/general/oto-logo.svg",
        )


def suzuki_finance_wordmark() -> None:
    cleaned = _remove_light_pixels(Image.open(SUZUKI_FINANCE), threshold=245)
    cleaned.save(SUZUKI_FINANCE, format="PNG", optimize=True)
    _update_master(
        "payments/indo/finance-insurance/suzuki-finance",
        SUZUKI_FINANCE,
        "Manual cleanup: removed the white site canvas from the official Suzuki Finance wordmark.",
    )


def samsat_marks() -> None:
    """Use only the official regional wordmark crop, not the Jateng page mascot/banner."""
    source = Image.open(io.BytesIO(_get(
        "https://samsat.jatengprov.go.id/codebase/assets/img/logo_instansi.png?p=20260814133213"
    ))).convert("RGBA")
    # The source contains three government seals at the top and a Sakpole
    # mascot at the right. Keep the central e-SAMSAT/SAMSAT lockup only.
    crop = source.crop((0, 175, 560, 327))
    bbox = crop.getchannel("A").getbbox()
    if bbox:
        crop = crop.crop(bbox)
    crop.save(SAMSAT_JATENG, format="PNG", optimize=True)
    _update_master(
        "payments/indo/government-public/samsat-jateng",
        SAMSAT_JATENG,
        "Manual cleanup: cropped the official regional SAMSAT Jateng wordmark from the source page artwork; removed the unrelated mascot and surrounding seals.",
    )
    if not SAMSAT_JATIM.exists():
        SAMSAT_JATIM.parent.mkdir(parents=True, exist_ok=True)
        SAMSAT_JATIM.write_bytes(_get("https://bapenda.jatimprov.go.id/themes/tailwind/bapenda/images/logo-1.png"))
    _update_master(
        "payments/indo/government-public/samsat-jatim",
        SAMSAT_JATIM,
        "Manual source override: used the official Bapenda Jawa Timur mark; no generic PKB icon was guessed.",
        source_url="https://bapenda.jatimprov.go.id/themes/tailwind/bapenda/images/logo-1.png",
    )


def spil_wordmark() -> None:
    _write_raster(
        "payments/indo/education-invoicing/spil",
        SPIL,
        _get("https://www.spil.co.id/spil_logo.svg"),
        "Manual source override: used the official SPIL wordmark published by the provider site.",
        "https://www.spil.co.id/spil_logo.svg",
    )


def paper_id_wordmark() -> None:
    """Turn Paper.id's official light lockup into a transparent dark lockup.

    The provider publishes a light SVG containing a white canvas and white
    wordmark. That is valid for a dark website header but becomes an invisible
    app-tile-like square in a transparent 40px logo library frame.
    """
    text = _get("https://paper.id/assets/images/seo/paper-logo-light.svg").decode("utf-8", "replace")
    text = re.sub(r"\s*<rect\b[^>]*/>\s*", "", text, count=1)
    text = re.sub(r'fill\s*=\s*["\']white["\']', 'fill="#1F2937"', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*clip-path\s*=\s*["\']url\(#clip0_191_514\)["\']', "", text)
    text = re.sub(r"\s*<clipPath\b[^>]*>\s*</clipPath>\s*", "", text)
    PAPER_ID.parent.mkdir(parents=True, exist_ok=True)
    PAPER_ID.write_text(text, encoding="utf-8")
    _update_master(
        "payments/indo/education-invoicing/paper-id",
        PAPER_ID,
        "Manual cleanup: converted the provider's official light lockup to a transparent dark wordmark; removed its white canvas so it remains readable on light and dark QA surfaces.",
        source_url="https://paper.id/assets/images/seo/paper-logo-light.svg",
    )


def alfamidi_wordmark() -> None:
    _write_raster(
        "minimarkets/indo/alfamidi",
        ALFAMIDI,
        _get("https://www.alfamidiku.com/assets/images/logo.png"),
        "Manual source override: used the official Alfamidi site wordmark; app tiles remain prohibited for merchant rows.",
        "https://www.alfamidiku.com/assets/images/logo.png",
    )


def football_dream_title() -> None:
    image = Image.open(FOOTBALL).convert("RGB")
    # The fetch step restores the 512px source. Skip an already prepared mark
    # so rerunning the normalization workflow is safe and idempotent.
    if image.size != (512, 512):
        return
    # The official title lockup is printed on the jersey in the source artwork.
    # Crop only the title area; the player, FIFPRO mark, and adjacent promo icon
    # are deliberately outside this box.
    # Keep the two-line title at this small library size; the tiny "BE A PRO"
    # subline becomes unreadable noise inside a 40px component.
    crop = image.crop((204, 330, 378, 404))
    mask = Image.new("L", crop.size, 0)
    pixels = crop.load()
    mask_pixels = mask.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b = pixels[x, y]
            # The lockup is white/grey against a saturated blue/red jersey.
            if min(r, g, b) >= 95 and max(r, g, b) - min(r, g, b) <= 95:
                mask_pixels[x, y] = 255
    # Close tiny holes and add a restrained dark outline so the white title
    # remains readable on both light and dark QA backgrounds.
    mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    outline = mask.filter(ImageFilter.MaxFilter(5))
    output = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    output.paste((17, 24, 39, 255), mask=outline)
    output.paste((255, 255, 255, 255), mask=mask)
    output = output.resize((crop.width * 2, crop.height * 2), Image.Resampling.LANCZOS)
    output.save(FOOTBALL, format="PNG", optimize=True)

    _update_master(
        "payments/indo/games-vouchers/football-dream-be-a-pro",
        FOOTBALL,
        "Manual cleanup: extracted the official title lockup from product artwork; player/card background removed.",
    )


def biznet_icon() -> None:
    image = Image.open(BIZNET).convert("RGBA")
    image.crop((0, 0, 145, 150)).save(BIZNET, format="PNG", optimize=True)
    _update_master(
        "payments/indo/internet-tv/biznet",
        BIZNET,
        "Manual cleanup: used the official Biznet brand icon so the mark remains legible on both light and dark surfaces.",
    )


def remove_white_canvas(asset: pathlib.Path, target: str, note: str) -> None:
    image = Image.open(asset).convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if min(r, g, b) > 235 and max(r, g, b) - min(r, g, b) < 22:
                pixels[x, y] = (r, g, b, 0)
    bbox = image.getchannel("A").getbbox()
    if bbox:
        pad = max(4, round(max(image.size) * 0.02))
        bbox = (
            max(0, bbox[0] - pad), max(0, bbox[1] - pad),
            min(image.width, bbox[2] + pad), min(image.height, bbox[3] + pad),
        )
        image = image.crop(bbox)
    image.save(asset, format="PNG", optimize=True)
    _update_master(target, asset, note)


if __name__ == "__main__":
    football_dream_title()
    biznet_icon()
    remove_white_canvas(
        MLBB,
        "payments/indo/games-vouchers/mobile-legends",
        "Manual cleanup: removed the white web canvas from the curated exact-match title mark.",
    )
    remove_white_canvas(
        PUBG,
        "payments/indo/games-vouchers/pubg-mobile",
        "Manual cleanup: removed the white web canvas from the curated exact-match title mark.",
    )
    cbn_wordmark()
    transvision_wordmark()
    pegadaian_vector_cleanup()
    home_credit_wordmark()
    bfi_wordmark()
    oto_wordmarks()
    suzuki_finance_wordmark()
    samsat_marks()
    spil_wordmark()
    paper_id_wordmark()
    alfamidi_wordmark()
    print(f"prepared {FOOTBALL.relative_to(ROOT)}")
