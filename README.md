# Logo Library — Research Index

Multi-region payment & retail logo research: Indonesia, SEA (per country) and international
banks, e-wallets, minimarkets and e-commerce platforms.

## Status of this pass — read first

**Phase 1 (research / master list) is delivered. Phase 2 (source & download logo assets) is
not. Phase 3 (the sheet) is delivered with asset-dependent columns empty.**

The environment this ran in enforces an egress policy that permits **GitHub only**. Every
other host — brand sites, press kits, app-store endpoints, Wikimedia Commons, and the
regulator registries (OJK, BI, MAS, BNM, BOT, BSP, SBV) — was refused at the proxy with
`HTTP 403` on `CONNECT`. Both the shell and the page-fetch tool go through that same policy,
so **no logo file could be downloaded and no registry page could be opened**. Web search was
available and was used; that is how the market-status findings below were established.

Consequences for the data in this repo:

- No logo files exist yet. The Google Drive asset folders are an empty scaffold.
- `source_url`, `file_link`, `aspect` and `background` are empty or `TBD` on every row. They
  were deliberately left blank rather than guessed — a plausible-looking but never-opened URL
  is worse than an empty cell.
- `website` is compiled from research and general knowledge. Treat it as a starting point to
  confirm, not as verified fact.
- `variant` is a reasoned recommendation based on how each brand's mark is normally used. It
  was **not** chosen by comparing downloaded candidates, as the brief's Phase 2 intends.
- **No row is marked `Verified`**, because the verification the brief defines was not possible.

**`scripts/fetch_logos.py` is the fix.** Run it anywhere with open outbound HTTPS and it
fills in everything this pass could not. See "Fetching the images" below.

## Where the deliverables live

| Artifact | Link |
|---|---|
| Drive folder (root) | https://drive.google.com/drive/folders/14iGABfKzcp5k5kbNE9wrIaZIABcFl3H2 |
| Master List sheet | https://docs.google.com/spreadsheets/d/11TnjRb0cC3tbXxYi-OofEM9kX5xQ00OQNDXx1x-gD3s/edit |
| README doc | https://docs.google.com/document/d/1FfJ9O1CjdbSolCESIC38ogwp8gWXrTVoNIv97CbA_0w/edit |

The brief asked for one sheet with two tabs. This session had Google Drive file-creation only
and no Sheets API, so tabs cannot be added to an existing spreadsheet — the README is a
separate Doc and the Master List is the sheet. `scripts/build_sheet.py` generates a genuine
two-tab `.xlsx` that merges them, for whoever runs the next pass with fuller tooling.

The Drive folder also contains the empty asset scaffold: 30 folders mirroring the naming
convention (`banks/indo`, `banks/sea/{sg,my,th,ph,vn,kh,la,bn,mm}`, `ewallets/...`,
`minimarkets/indo`, `ecommerce/indo`), ready for the sourcing pass to drop files into.

## Layout

| Path | What it is |
|---|---|
| `data/master_list.tsv` | Canonical dataset, 134 rows, tab-separated |
| `data/master_list.csv` | Same data, CSV (this is what is uploaded to Google Sheets) |
| `scripts/build_sheet.py` | Builds the two-tab `.xlsx` workbook from the TSV |
| `scripts/fetch_logos.py` | Resolves and downloads the logo assets |
| `data/source_overrides.tsv` | Manual URL pins for rows the resolver gets wrong |
| `data/fetch_report.csv` | Per-row outcome of the last fetch run |
| `assets/` | Downloaded logo files, laid out as `assets/{figma path}.{ext}` |
| `out/` | Generated workbook |

## Fetching the images

Two ways to run it. Neither needs anything from the session that built this index.

### Option A — GitHub Actions (no local setup)

Actions tab -> **Fetch logos** -> **Run workflow**. Runners have open network access, so it
just works. Options: `only` to limit to a path prefix, `dry_run` to resolve without
downloading, `commit` to push the assets back to the branch. Results are always attached to
the run as a `logo-assets` artifact, and the run summary shows an outcome tally.

Start with `dry_run: true` and `only: banks/indo` to see what it resolves before committing
to a full run.

### Option B — locally

```bash
pip install -r requirements.txt

python3 scripts/fetch_logos.py --dry-run --only banks/indo   # look before you leap
python3 scripts/fetch_logos.py --only banks/indo             # fetch one slice
python3 scripts/fetch_logos.py                               # fetch everything
```

Useful flags: `--limit N`, `--delay` (default 1.0s between requests), `--force` to
re-download rows that already have a file, `--min-edge` to change the size floor (default
128px - see below),
`--no-robots` to skip robots.txt checks, `--include-sanctioned` to opt Myanmar rows in.

### How it resolves a logo

Each row has no source URL, so the script tries several sources in the order the brief
prefers, then scores every candidate it found:

1. **The brand's own site** — `<link rel=icon>`, `apple-touch-icon`, `og:image`, and any
   `<img>` whose src/alt/class looks like a logo. It also follows one press/brand/newsroom
   link if the homepage has one, since that is where press kits live.
2. **The official app-store icon** via the iTunes Search API, matched against the
   institution name so a third-party app can't slip through. This is the best source for
   the `app-icon` variant.
3. **A domain-keyed logo API** ([Clearbit](https://clearbit.com/logo)), for sites whose logo
   isn't exposed as a clean `<img>`/`<link rel=icon>` - increasingly common with inline-SVG
   headers, CSS background-image logos, or heavy client-side rendering that plain HTML
   scraping can't see through.
4. **Wikimedia Commons**, recording the licence on each candidate so reuse can be checked.
5. **A favicon service**, only if everything above found nothing, and always flagged in
   Notes as a low-resolution stand-in to replace.

Scoring prefers, in order: vector over raster, official sources over aggregated ones, a
match for the row's recommended variant (as a tiebreaker within a source tier - so a
last-resort source can't win outright just because it happens to be labeled with the right
kind), transparency, then size. Raster candidates below the
size floor are rejected rather than upscaled - never upscale, per the brief - but the floor
itself is 128px by default, not the original brief's 512px. Actual on-screen size for these
logos is ~40-64px CSS, so 128px raw already covers 2x retina with headroom; the 512px figure
was quietly discarding perfectly good assets, including the common 180x180
`apple-touch-icon.png` most sites publish. Raise it with `--min-edge` if you do need
higher-resolution source material for something other than a 40-64px chip.

After a successful download it writes back `Logo Source URL`, `Native Aspect Ratio`
(measured, e.g. `3.00:1 (horizontal, 900x300)`), `Background Type` (transparency actually
detected from the alpha channel), and `Downloaded File Link`, and appends the source and
licence to Notes.

**Candidate ordering.** Only the first `--max-candidates` (default 8) candidates found are
actually downloaded, to bound runtime - a busy homepage can produce plenty of low-value
matches (payment-method icons, partner badges, social links all loosely match the "logo"/
"brand" heuristic used to scan `<img>` tags). Candidates are sorted by source confidence
before that budget is applied, so structured hits (`<link rel=icon>`, `og:image`, the
app-store icon, the domain-logo API) always get tried ahead of those loose `<img>` guesses,
regardless of which resolver happened to find them first or how many low-value matches a
given page has. Without this, a bank with a cluttered homepage could exhaust its entire
budget on partner-logo images before ever reaching its own app-store icon - which is exactly
what happened to `banks/indo/bni` before this fix (24 candidates found, all 8 tried were
`<img>` guesses, 0 usable; the real fix, not raising the size floor further).

### What it will not touch

Rows marked `Flagged - Excluded` are skipped — those brands are defunct. Myanmar rows are
skipped unless you pass `--include-sanctioned`, which prints a warning reminding you to
screen against current designations first. Existing files are never overwritten without
`--force`.

### When it gets one wrong

Some rows will resolve to the wrong asset — a favicon instead of a wordmark, a partner's
logo, a stale pre-rebrand file. Put the correct direct URL in `data/source_overrides.tsv`
(one `figma path<TAB>URL` per line) and re-run; overrides beat every resolver. Check
`data/fetch_report.csv` after each run to see what landed and what needs a pin.

Nothing the script writes is marked `Verified`. Auto-resolution is a strong starting point,
not the human confirmation the brief defines — the rebrand traps listed below are exactly
the cases a machine will get wrong.

## Naming convention

| # | Category | Region | Naming path (for later Figma use) |
|---|---|---|---|
| 1 | Banks | Indonesia | `banks/indo/{name}` |
| 2 | E-wallets | Indonesia | `ewallets/indo/{name}` |
| 3 | Minimarkets | Indonesia | `minimarkets/indo/{name}` |
| 4 | E-commerce | Indonesia | `ecommerce/indo/{name}` |
| 5 | Banks | SEA, per country | `banks/sea/{country}/{name}` |
| 6 | E-wallets | SEA, per country | `ewallets/sea/{country}/{name}` |
| 7 | Banks | International, per country | `banks/international/{country}/{name}` |
| 8 | E-wallets / remittance | International, per country or global | `ewallets/international/{country}/{name}` or `ewallets/international/{name}` |

SEA country codes are ISO 3166-1 alpha-2, lowercase: `sg` `my` `th` `ph` `vn` `kh` `mm` `la`
`bn`. Indonesia keeps the `indo` prefix for continuity. **Flagged as the brief asked:**
switching Indonesia to `id` would make the whole tree consistent.

International banks now use the same per-country pattern (`us` `gb` `de` `fr` `nl` `cn` `au`
`ca` `jp` `kr` `hk`), scoped to where Wise and PandaRemit can actually deliver a transfer sent
from Indonesia — not an exhaustive SWIFT enumeration, per the brief's original guardrail. The
three banks originally filed flat (`banks/international/hsbc` etc.) were renamed to
`banks/international/gb/hsbc`, `banks/international/us/citibank` and
`banks/international/gb/standard-chartered` for consistency, since nothing has been imported
into Figma yet and the paths were safe to fix. International e-wallets stay flat
(`ewallets/international/{name}`) for the genuinely global remittance platforms (PayPal, Wise,
Western Union, etc.), and gain a country segment only for wallets tied to one market
(`ewallets/international/cn/alipay`, `.../cn/wechat-pay`, `.../gb/revolut`).

## Status legend

| Status | Meaning |
|---|---|
| `Verified` | Institution confirmed against its regulator's register **and** an official asset downloaded. **Not used in this pass** — neither check was possible. |
| `Needs Review` | Researched candidate. Regulator confirmation and asset sourcing still outstanding. Per-row `notes` give the specific reason. |
| `Flagged - Excluded` | Do not source an asset. Entity is defunct, exited the market, or discontinued. Reason in `notes`. |

## Why International grew past the brief's original cap

The brief's original guardrail was to keep International banks to roughly 15-20 entries and
not enumerate every SWIFT member. That held for the first pass. It was then explicitly
widened at the user's request to match what **Wise** (160+ countries) and **PandaRemit**
(40+ corridors, explicitly including Indonesia as a send market) actually let someone
transfer to from Indonesia — United States, United Kingdom, Germany, France, Netherlands,
China, Australia, Canada, Japan, South Korea and Hong Kong. Within each country the banks
listed are the major consumer institutions a recipient is actually likely to hold an account
at, not a SWIFT enumeration — still bounded, just against a different, source-backed
criterion than the original page count.

## Market-status findings that change the brief's starting lists

- **7-Eleven Indonesia** — excluded. Operator PT Modern Internasional closed all remaining
  stores effective 30 June 2017.
- **JD.ID** — excluded. Ceased Indonesian operations 31 March 2023, as the brief anticipated.
- **Moca (Vietnam)** — excluded. Grab terminated the wallet effective 1 July 2024. The brief
  still lists it as a live candidate.
- **Sakuku (BCA)** — excluded. Wound down; users migrated to myBCA. Confirm final closure date.
- **Lawson Indonesia** — needs review. Alfamart has acquired Lawson's Indonesian stores; the
  brand may be retained, converted or retired. Human decision needed before sourcing.
- **Bukalapak** — needs review, still trading. Ceased its physical-goods marketplace in
  Feb 2025; virtual products and digital services only. Confirm the e-commerce grouping fit.
- **Bank BTPN** — renamed **PT Bank SMBC Indonesia Tbk** effective 2 Oct 2024. Filed as
  `banks/indo/smbc-indonesia`. Do not use a BTPN-era asset.
- **Singtel Dash** — filed as `ewallets/sea/sg/dash`. Singtel agreed to sell Dash to Western
  Union (announced Oct 2024), so the Singtel-badged asset is stale.
- **OCBC NISP → OCBC Indonesia**, **KB Bukopin → KB Bank**, **PayMaya → Maya**,
  **TMB + Thanachart → ttb** — all rebranded; pre-rebrand assets are stale.
- **Citibank Indonesia** — consumer banking sold to UOB in 2023. Confirm it still belongs in a
  consumer payment UI.
- **Myanmar (KBZ Bank, KBZPay)** — marked `Needs Review` with no asset, per the brief's
  sanctions instruction. Screen against current OFAC/EU/UK designations before any use.
- **Regional brand duplication** — GrabPay and ShopeePay appear once per country, following the
  brief's per-country path convention. If one shared asset is preferred, collapse those rows
  before the Figma pass.

## Row counts

| Category | Rows |
|---|---|
| bank | 181 |
| ewallet | 48 |
| ecommerce | 12 |
| minimarket | 8 |
| **Total** | **249** |

Indonesia 132 (101 banks, 11 e-wallets, 12 e-commerce, 8 minimarkets), SEA 62,
International 56 (44 banks across 11 countries, 12 e-wallets — 3 country-scoped, 9 global).

The Indonesian bank list aims to cover the commercial banks (*bank umum*) a transfer or
virtual-account picker actually needs — the big four, private nationals, digital banks,
sharia banks, foreign and joint-venture banks, and all the regional development banks
(BPD). Rural banks (BPR) are deliberately out of scope; there are thousands and they do not
appear in consumer payment UIs.

Of these, 246 are `Needs Review` and 4 are `Flagged - Excluded`.

## Licensing note

These are third-party trademarks across many jurisdictions. Intended for internal reference
and UI design work only, not redistribution.
