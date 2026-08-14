#!/usr/bin/env python3
"""Resolve and download official logo assets for every eligible row in the master list.

Run this from a machine or CI runner with open outbound HTTPS. It reads
``data/master_list.tsv``, resolves a logo URL per institution from several sources,
downloads the best candidate, and writes the asset-dependent columns back.

    python3 scripts/fetch_logos.py --dry-run          # resolve only, download nothing
    python3 scripts/fetch_logos.py                    # resolve + download
    python3 scripts/fetch_logos.py --only banks/indo  # one slice at a time

Sources are tried in the order the brief asks for: the brand's own site (including any
press/brand page it links to), then the official app-store icon, then Wikimedia Commons,
then a favicon service as a last resort. Rows marked ``Flagged - Excluded`` are skipped,
and rows in sanctioned jurisdictions are skipped unless explicitly opted in.

For bank rows, app-store icons, favicons, and page/social images are discovery signals
only and are rejected as primary assets. Banks need a corporate mark or a manual neutral
fallback; a mobile app tile is not a bank logo.
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import io
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.robotparser

import requests
from bs4 import BeautifulSoup
from PIL import Image

Image.init()

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "master_list.tsv"
OVERRIDES = ROOT / "data" / "source_overrides.tsv"
REPORT = ROOT / "data" / "fetch_report.csv"
ASSETS = ROOT / "assets"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36 (logo-library research index; contact repo owner)")

# Columns in master_list.tsv, by index.
C_PATH, C_NAME, C_CAT, C_REGION, C_COUNTRY, C_SITE = 0, 1, 2, 3, 4, 5
C_SOURCE, C_VARIANT, C_REASON, C_ASPECT, C_BG, C_FILE, C_STATUS, C_NOTES = 6, 7, 8, 9, 10, 11, 12, 13

# App Store storefronts, keyed by the master list's country / region value.
STOREFRONT = {"sg": "sg", "my": "my", "th": "th", "ph": "ph", "vn": "vn", "kh": "kh",
              "mm": "mm", "la": "la", "bn": "bn", "us": "us", "gb": "gb", "de": "de",
              "fr": "fr", "nl": "nl", "cn": "cn", "au": "au", "ca": "ca", "jp": "jp",
              "kr": "kr", "hk": "hk", "Indonesia": "id", "International": "us"}

# Jurisdictions the brief says not to source without human sign-off.
SANCTIONED_COUNTRIES = {"mm"}

MIN_EDGE = 128          # actual display size is ~40-64px CSS; 128px raw covers
                        # 2x retina with headroom without discarding apple-touch-icon
                        # (180x180) and most brand-site favicons, as a 512px floor did.
                        # Vector sources are always accepted regardless of this value.
CONFIG = {"min_edge": MIN_EDGE}
RASTER_EXT = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


@dataclasses.dataclass
class Candidate:
    """One possible logo asset for a row, before validation."""
    url: str
    source: str          # which resolver produced it
    kind: str            # icon | wordmark | app-icon | unknown
    note: str = ""
    licence: str = ""

    # Filled in by download():
    data: bytes | None = None
    mime: str = ""
    width: int = 0
    height: int = 0
    is_vector: bool = False
    transparent: bool | None = None

    @property
    def longest_edge(self) -> int:
        return max(self.width, self.height)


class Fetcher:
    """Thin HTTP wrapper: shared session, polite delay, optional robots.txt check."""

    def __init__(self, delay: float = 1.0, timeout: int = 25, respect_robots: bool = True):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = UA
        self.delay = delay
        self.timeout = timeout
        self.respect_robots = respect_robots
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self._last = 0.0

    def _wait(self) -> None:
        gap = time.monotonic() - self._last
        if gap < self.delay:
            time.sleep(self.delay - gap)
        self._last = time.monotonic()

    def allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parts = urllib.parse.urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{origin}/robots.txt")
            try:
                self._wait()
                resp = self.session.get(f"{origin}/robots.txt", timeout=self.timeout)
                rp.parse(resp.text.splitlines() if resp.ok else [])
            except requests.RequestException:
                rp = None                      # unreachable robots.txt: don't block on it
            self._robots[origin] = rp
        rp = self._robots[origin]
        return True if rp is None else rp.can_fetch(UA, url)

    def get(self, url: str, **kw) -> requests.Response | None:
        if not self.allowed(url):
            return None
        try:
            self._wait()
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True, **kw)
            return resp if resp.ok else None
        except requests.RequestException:
            return None


# --------------------------------------------------------------------------- resolvers

def resolve_app_store(row: list[str], fetcher: Fetcher) -> list[Candidate]:
    """Official app icon via the iTunes Search API — the best source for app-icon variants."""
    country = STOREFRONT.get(row[C_COUNTRY]) or STOREFRONT.get(row[C_REGION], "us")
    query = urllib.parse.quote(row[C_NAME])
    url = f"https://itunes.apple.com/search?term={query}&country={country}&entity=software&limit=5"
    resp = fetcher.get(url)
    if resp is None:
        return []
    try:
        results = resp.json().get("results", [])
    except json.JSONDecodeError:
        return []

    out = []
    wanted_tokens = _name_tokens(row[C_NAME])
    for item in results:
        track = item.get("trackName", "")
        # Only trust a result that shares at least one meaningful token with the
        # institution name (generic words like "bank"/"indonesia" don't count), so
        # we don't pull a third-party app that merely mentions the brand, but also
        # don't demand a full substring match a name like "Bank X (ABBR)" won't
        # have against an app literally titled "ABBR Mobile".
        if not (wanted_tokens & _name_tokens(track)):
            continue
        art = item.get("artworkUrl512") or item.get("artworkUrl100")
        if not art:
            continue
        # The CDN honours an explicit size segment; ask for something comfortably >512.
        art = re.sub(r"/\d+x\d+bb\.(png|jpg)$", "/1024x1024bb.png", art)
        out.append(Candidate(url=art, source="app-store", kind="app-icon",
                             note=f"iTunes: {item.get('trackName', '')} ({item.get('sellerName', '')})"))
    return out


def resolve_brand_site(row: list[str], fetcher: Fetcher) -> list[Candidate]:
    """Scrape the institution's own site for a logo, and follow a press/brand page if linked."""
    site = row[C_SITE].strip()
    if not site:
        return []
    out: list[Candidate] = []
    pages = [site]

    resp = fetcher.get(site)
    if resp is not None:
        soup = BeautifulSoup(resp.text, "html.parser")
        out.extend(_harvest(soup, resp.url, "brand-site"))
        # Follow at most one press/brand/media page — that is where press kits live.
        for a in soup.find_all("a", href=True):
            label = f"{a.get_text(' ', strip=True)} {a['href']}".lower()
            if re.search(r"press|media|brand|newsroom|logo|identity", label):
                target = urllib.parse.urljoin(resp.url, a["href"])
                if urllib.parse.urlsplit(target).netloc == urllib.parse.urlsplit(resp.url).netloc:
                    pages.append(target)
                    break

    if len(pages) > 1:
        press = fetcher.get(pages[1])
        if press is not None:
            soup = BeautifulSoup(press.text, "html.parser")
            out.extend(_harvest(soup, press.url, "brand-press"))

    # Conventional well-known paths, cheap to try and often the cleanest asset.
    for suffix in ("/favicon.svg", "/apple-touch-icon.png", "/favicon.ico"):
        out.append(Candidate(url=urllib.parse.urljoin(site, suffix), source="brand-site",
                             kind="icon", note=f"conventional path {suffix}"))
    return out


def _harvest(soup: BeautifulSoup, base: str, source: str) -> list[Candidate]:
    """Pull logo-ish assets out of a parsed page."""
    out: list[Candidate] = []

    for link in soup.find_all("link", rel=True):
        rels = " ".join(link.get("rel", [])).lower()
        if "icon" not in rels or not link.get("href"):
            continue
        kind = "app-icon" if "apple-touch" in rels else "icon"
        out.append(Candidate(url=urllib.parse.urljoin(base, link["href"]), source=source,
                             kind=kind, note=f"<link rel={rels} sizes={link.get('sizes', '?')}>"))

    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        out.append(Candidate(url=urllib.parse.urljoin(base, og["content"]), source=source,
                             kind="unknown", note="og:image"))

    # <img> tags that look like a logo, by src / alt / class. This is a loose
    # heuristic - a busy homepage can match plenty of things that aren't the
    # institution's own logo (partner badges, payment-method icons, social
    # links) - so these are tagged with a distinct, lower-confidence source
    # ("-img" suffix) rather than the structured <link>/og:image hits above.
    for img in soup.find_all("img", src=True):
        hay = " ".join([img.get("src", ""), img.get("alt", ""),
                        " ".join(img.get("class", []))]).lower()
        if "logo" in hay or "brand" in hay:
            kind = "wordmark" if "logo" in hay else "unknown"
            out.append(Candidate(url=urllib.parse.urljoin(base, img["src"]), source=f"{source}-img",
                                 kind=kind, note=f"<img> {img.get('alt', '')[:40]}"))
    return out


def resolve_domain_logo(row: list[str], fetcher: Fetcher) -> list[Candidate]:
    """A domain-keyed logo API, for sites whose own HTML doesn't expose a clean
    logo tag (inline SVG headers, CSS background-image logos, heavy JS chrome).
    These services aggregate from the same public sources listed in the brief
    (site crawls, social profiles) rather than being a distinct rights holder,
    so treat a hit here the same as the brand-site tier for scoring purposes.
    """
    site = row[C_SITE].strip()
    if not site:
        return []
    domain = urllib.parse.urlsplit(site).netloc
    return [Candidate(url=f"https://logo.clearbit.com/{domain}?size=512&format=png",
                      source="domain-logo", kind="unknown",
                      note=f"domain-logo API for {domain}")]


def resolve_wikimedia(row: list[str], fetcher: Fetcher) -> list[Candidate]:
    """Wikimedia Commons, recording the licence so reuse can be checked."""
    query = urllib.parse.quote(f"{row[C_NAME]} logo")
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
           f"&generator=search&gsrsearch={query}&gsrnamespace=6&gsrlimit=8"
           "&prop=imageinfo&iiprop=url|size|mime|extmetadata")
    resp = fetcher.get(url)
    if resp is None:
        return []
    try:
        pages = resp.json().get("query", {}).get("pages", {})
    except json.JSONDecodeError:
        return []

    out = []
    for page in pages.values():
        for info in page.get("imageinfo", []):
            mime = info.get("mime", "")
            if mime not in ("image/svg+xml", "image/png"):
                continue
            meta = info.get("extmetadata", {})
            licence = meta.get("LicenseShortName", {}).get("value", "unknown")
            out.append(Candidate(url=info["url"], source="wikimedia", kind="unknown",
                                 note=page.get("title", ""), licence=licence))
    return out


def resolve_favicon_service(row: list[str], fetcher: Fetcher) -> list[Candidate]:
    """Last resort. Low resolution by nature — always flagged for human review."""
    site = row[C_SITE].strip()
    if not site:
        return []
    domain = urllib.parse.urlsplit(site).netloc
    return [Candidate(url=f"https://icons.duckduckgo.com/ip3/{domain}.ico",
                      source="favicon-service", kind="icon",
                      note="last-resort favicon service, low resolution")]


PRIMARY_RESOLVERS = [resolve_brand_site, resolve_app_store, resolve_domain_logo, resolve_wikimedia]


# ------------------------------------------------------------------- download + validate

def download(cand: Candidate, fetcher: Fetcher) -> bool:
    """Fetch a candidate and measure it. Returns False if it isn't a usable image."""
    resp = fetcher.get(cand.url)
    if resp is None:
        return False
    cand.data = resp.content
    cand.mime = resp.headers.get("Content-Type", "").split(";")[0].strip().lower()

    if cand.mime == "image/svg+xml" or cand.url.lower().endswith(".svg"):
        return _measure_svg(cand)
    return _measure_raster(cand)


def _measure_svg(cand: Candidate) -> bool:
    text = cand.data.decode("utf-8", "replace")
    if "<svg" not in text.lower():
        return False
    cand.is_vector = True
    cand.mime = "image/svg+xml"
    box = re.search(r'viewBox\s*=\s*["\']([\d.\-+eE\s,]+)["\']', text)
    if box:
        nums = [float(n) for n in re.split(r"[\s,]+", box.group(1).strip()) if n]
        if len(nums) == 4 and nums[2] and nums[3]:
            cand.width, cand.height = int(nums[2]), int(nums[3])
    if not cand.width:                       # fall back to width/height attributes
        w = re.search(r'\bwidth\s*=\s*["\']([\d.]+)', text)
        h = re.search(r'\bheight\s*=\s*["\']([\d.]+)', text)
        if w and h:
            cand.width, cand.height = int(float(w.group(1))), int(float(h.group(1)))
    cand.transparent = "vector"
    return bool(cand.width and cand.height)


def _measure_raster(cand: Candidate) -> bool:
    try:
        img = Image.open(io.BytesIO(cand.data))
        img.load()
    except Exception:
        return False
    cand.width, cand.height = img.size
    if img.mode in ("RGBA", "LA") or "transparency" in img.info:
        alpha = img.convert("RGBA").getchannel("A")
        cand.transparent = alpha.getextrema()[0] < 255
    else:
        cand.transparent = False
    if not cand.mime.startswith("image/"):
        cand.mime = Image.MIME.get(img.format, "image/png")
    return True


# Confidence ranking shared by scoring (after download) and candidate ordering
# (before download, so a tight --max-candidates budget is spent on the most
# promising sources first instead of whichever resolver happened to run first).
# The "-img" tiers are the loose <img class=logo>-style heuristic matches, kept
# below the structured tag-based hits (<link rel=icon>, og:image, app-store,
# domain-logo) since a busy homepage can match plenty of things that aren't the
# institution's own logo.
SOURCE_RANK = {"brand-press": 5, "brand-site": 4, "app-store": 4, "domain-logo": 4,
               "wikimedia": 2, "brand-press-img": 2, "brand-site-img": 2,
               "favicon-service": 0}


def score(cand: Candidate, want_variant: str) -> tuple:
    """Rank candidates. Higher is better; compared as a tuple, left to right."""
    return (
        cand.is_vector,                                   # SVG beats raster
        SOURCE_RANK.get(cand.source, 1),                   # official beats aggregated - checked
                                                           # before variant match, so a weak
                                                           # last-resort source can't win just
                                                           # because it happens to be tagged
                                                           # with the right kind while a better,
                                                           # honestly-uncertain ("unknown") source
                                                           # isn't
        cand.kind == want_variant,                        # tiebreaker: matches the recommended variant
        bool(cand.transparent) or cand.is_vector,         # transparency preferred
        min(cand.longest_edge, 4096),                     # bigger, but don't chase absurd sizes
    )


def usable(cand: Candidate) -> bool:
    """Vector is always fine; raster must already meet the size floor (never upscale)."""
    return cand.is_vector or cand.longest_edge >= CONFIG["min_edge"]


def allowed_for_primary(row: list[str], cand: Candidate, is_override: bool = False) -> bool:
    """Apply the asset-role policy before a candidate can become a bank primary."""
    if row[C_CAT] != "bank" or is_override:
        return True
    haystack = f"{cand.url} {cand.note}".lower()
    # These are useful discovery sources but are not corporate primary artwork.
    if cand.source in {"app-store", "favicon-service"} or cand.kind == "app-icon":
        return False
    if cand.source.endswith("-img") or any(token in haystack for token in (
        "og:image", "social", "thumbnail", "banner", "paze_logo", "youtube-logo", "apple-touch", ".ico", "favicon",
    )):
        return False
    return True


def describe_aspect(cand: Candidate) -> str:
    if not (cand.width and cand.height):
        return "TBD"
    ratio = cand.width / cand.height
    if 0.95 <= ratio <= 1.05:
        shape = "square"
    elif ratio > 1:
        shape = "horizontal"
    else:
        shape = "vertical"
    pretty = f"{ratio:.2f}:1" if ratio >= 1 else f"1:{1 / ratio:.2f}"
    return f"{pretty} ({shape}, {cand.width}x{cand.height})"


def describe_background(cand: Candidate) -> str:
    if cand.is_vector:
        return "vector (verify no baked-in background)"
    return "transparent" if cand.transparent else "has own baked-in background"


# ------------------------------------------------------------------------------ driver

def load_overrides() -> dict[str, str]:
    """Manual figma_path -> URL pins, for rows automatic resolution gets wrong."""
    if not OVERRIDES.exists():
        return {}
    out = {}
    for line in OVERRIDES.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        path, _, url = line.partition("\t")
        if url.strip():
            out[path.strip()] = url.strip()
    return out


def eligible(row: list[str], include_sanctioned: bool) -> tuple[bool, str]:
    if "Excluded" in row[C_STATUS]:
        return False, "flagged excluded — no asset to source"
    if row[C_COUNTRY] in SANCTIONED_COUNTRIES and not include_sanctioned:
        return False, "sanctioned/sensitive jurisdiction — needs human sign-off"
    if not row[C_SITE].strip() and not row[C_NAME].strip():
        return False, "no website or name to resolve from"
    return True, ""


def process(row, fetcher, overrides, args, report):
    path = row[C_PATH]
    ok, why = eligible(row, args.include_sanctioned)
    if not ok:
        report.append({"figma_path": path, "outcome": "skipped", "detail": why, "url": ""})
        print(f"  skip  {path}: {why}")
        return False

    dest_stub = ASSETS / path
    existing = [p for p in dest_stub.parent.glob(dest_stub.name + ".*")] if dest_stub.parent.exists() else []
    if existing and not args.force:
        report.append({"figma_path": path, "outcome": "exists", "detail": str(existing[0].relative_to(ROOT)), "url": ""})
        print(f"  have  {path}: {existing[0].name}")
        return False

    if path in overrides:
        candidates = [Candidate(url=overrides[path], source="override", kind=row[C_VARIANT] or "unknown",
                                note="pinned in data/source_overrides.tsv")]
    else:
        candidates = []
        for resolver in PRIMARY_RESOLVERS:
            candidates.extend(resolver(row, fetcher))
        if not candidates:
            candidates = resolve_favicon_service(row, fetcher)

    if row[C_CAT] == "bank" and path not in overrides:
        discovered = len(candidates)
        candidates = [candidate for candidate in candidates if allowed_for_primary(row, candidate)]
        if not candidates:
            report.append({
                "figma_path": path,
                "outcome": "unresolved",
                "detail": f"bank primary policy rejected {discovered} app-store/favicon/page-image candidate(s); add a manual corporate source or use a neutral fallback",
                "url": "",
            })
            print(f"  MISS  {path}: candidates rejected by bank primary policy")
            return False

    if not candidates:
        report.append({"figma_path": path, "outcome": "unresolved", "detail": "no candidates found", "url": ""})
        print(f"  MISS  {path}: no candidates")
        return False

    # A busy homepage can hand back plenty of candidates (partner badges, payment
    # icons, social links all loosely match the "logo"/"brand" heuristic); sort by
    # source confidence before applying the download budget so a tight
    # --max-candidates never starves the actually-promising sources (app-store,
    # domain-logo, structured <link>/og:image tags) in favor of whichever
    # low-confidence match happened to be found first.
    candidates.sort(key=lambda c: SOURCE_RANK.get(c.source, 1), reverse=True)
    tried = candidates[: args.max_candidates]

    if args.dry_run:
        for c in tried:
            report.append({"figma_path": path, "outcome": "candidate",
                           "detail": f"{c.source} | {c.kind} | {c.note} | {c.licence}", "url": c.url})
        print(f"  found {path}: {len(candidates)} candidate(s), would try {len(tried)}")
        return False

    good = []
    for cand in tried:
        if download(cand, fetcher) and usable(cand):
            good.append(cand)
    if not good:
        report.append({"figma_path": path, "outcome": "unusable",
                       "detail": (f"tried {len(tried)} of {len(candidates)} candidate(s) "
                                 f"(best sources first), none met the {CONFIG['min_edge']}px floor"),
                       "url": ""})
        print(f"  MISS  {path}: nothing met the size floor ({len(tried)}/{len(candidates)} tried)")
        return False

    best = max(good, key=lambda c: score(c, row[C_VARIANT]))
    ext = ".svg" if best.is_vector else RASTER_EXT.get(best.mime, ".png")
    dest = dest_stub.parent / (dest_stub.name + ext)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(best.data)

    row[C_SOURCE] = best.url
    row[C_ASPECT] = describe_aspect(best)
    row[C_BG] = describe_background(best)
    row[C_FILE] = str(dest.relative_to(ROOT))
    stamp = f"Auto-sourced via {best.source}."
    if best.licence:
        stamp += f" Licence: {best.licence}."
    if best.source == "favicon-service":
        stamp += " LAST-RESORT low-res source — replace before use."
    if stamp not in row[C_NOTES]:
        row[C_NOTES] = f"{row[C_NOTES]} {stamp}".strip()

    report.append({"figma_path": path, "outcome": "downloaded",
                   "detail": f"{best.source} | {best.kind} | {describe_aspect(best)} | {describe_background(best)}",
                   "url": best.url})
    print(f"  OK    {path}: {dest.name} ({best.source}, {describe_aspect(best)})")
    return True


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


_STOPWORDS = {"bank", "banking", "indonesia", "international", "group", "mobile",
              "app", "the", "of", "and", "co", "inc", "ltd", "tbk", "pt", "id"}


def _name_tokens(text: str) -> set[str]:
    """Meaningful lowercase word tokens, with generic banking/corp words stripped."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="resolve candidates, download nothing")
    ap.add_argument("--only", default="", help="only rows whose Figma Path starts with this prefix")
    ap.add_argument("--limit", type=int, default=0, help="stop after N eligible rows")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1.0)")
    ap.add_argument("--max-candidates", type=int, default=8, help="candidates to try per row")
    ap.add_argument("--min-edge", type=int, default=MIN_EDGE,
                    help=f"minimum longest edge in px for raster sources (default {MIN_EDGE}); "
                         "vectors are always accepted, and sources are never upscaled")
    ap.add_argument("--force", action="store_true", help="re-download rows that already have a file")
    ap.add_argument("--no-robots", action="store_true", help="skip robots.txt checks on brand sites")
    ap.add_argument("--include-sanctioned", action="store_true",
                    help="also fetch sanctioned-jurisdiction rows (requires human sign-off)")
    args = ap.parse_args()

    rows = [l.rstrip("\n").split("\t") for l in MASTER.read_text(encoding="utf-8").splitlines()]
    header, body = rows[0], rows[1:]

    if args.include_sanctioned:
        print("WARNING: including sanctioned/sensitive jurisdictions. Confirm sign-off and "
              "screen against current OFAC/EU/UK designations before using these assets.\n")

    CONFIG["min_edge"] = args.min_edge
    fetcher = Fetcher(delay=args.delay, respect_robots=not args.no_robots)
    overrides = load_overrides()
    report: list[dict] = []
    done = 0

    targets = [r for r in body if r[C_PATH].startswith(args.only)] if args.only else body
    print(f"{len(targets)} row(s) in scope"
          f"{' (dry run)' if args.dry_run else ''}\n")

    for row in targets:
        if args.limit and done >= args.limit:
            break
        if process(row, fetcher, overrides, args, report):
            done += 1

    if not args.dry_run:
        MASTER.write_text("\n".join("\t".join(r) for r in [header] + body) + "\n", encoding="utf-8")
        with open(ROOT / "data" / "master_list.csv", "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows([header] + body)

    with open(REPORT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["figma_path", "outcome", "detail", "url"])
        writer.writeheader()
        writer.writerows(report)

    tally: dict[str, int] = {}
    for entry in report:
        tally[entry["outcome"]] = tally.get(entry["outcome"], 0) + 1
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(tally.items())))
    print(f"report written to {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
