# Logo Library — Agent Context Transfer

Last verified: **2026-08-14** (Asia/Jakarta)  
Repository: `/Users/nikanakamanifesto/Documents/GitHub/logo-library`  
Figma file: `Logos`  
Figma file key: `8M3VW9BPaSGTUHZBaH8KGg`

This document is the operational handoff for another agent continuing the logo-library work. It
records the current repository state, Figma structure, research decisions, asset provenance rules,
known failures and repairs, QA results, unresolved rows, and the safe procedure for the next
expansion. Read it before changing the catalogue, downloading assets, or editing Figma.

The row-level GoPay research source is [`data/gopay_catalog.tsv`](data/gopay_catalog.tsv). The
methodology and evidence notes are in [`GOPAY_CATALOG_RESEARCH.md`](GOPAY_CATALOG_RESEARCH.md).
The reusable import rules are in [`LOGO_LIBRARY_IMPORT_GUIDE.md`](LOGO_LIBRARY_IMPORT_GUIDE.md).

## 1. Current outcome

The Indonesia GoPay expansion is implemented in the existing Figma file:

- 159 dated GoPay catalogue rows.
- 87 payment components across the ten GoPay payment sections.
- 18 total merchant components in the pre-existing Merchant section; three were added in this
  pass: Alfamidi, Alfagift, and Klik Indomaret.
- Finance & Insurance, Government & Public, and Education & Invoicing are populated.
- Google Play and Xbox use corrected full-color brand vectors.
- Paper.id, CBN, Transvision, Samsat Jateng, Pegadaian, OTO, and BFI exceptional assets were
  cleaned or replaced before import.
- Figma light/dark screenshot QA was run for every GoPay section and the Merchant section.
- The corrected structural audit passed: zero geometry failures, zero resize failures, zero
  duplicate component names, and zero orphan upload nodes.
- 80×80 instance tests preserve proportional Logo/Artwork scaling.
- Temporary QA backgrounds and failed temporary uploads were removed from Figma.

The implementation intentionally does **not** claim that the GoPay catalogue is a permanent or
exhaustive directory. GoPay's provider list is dynamic and searchable in-app. The catalogue is a
dated snapshot and must be re-verified before a later expansion.

## 2. Scope and boundaries

### Included

- Indonesia GoPay, not international GoPay/WePay.
- GoTagihan bill categories and named providers.
- Pulsa, data packages, postpaid telecom, fixed-line telecom, internet, cable TV, utilities,
  e-money, finance, insurance, public services, education, e-invoicing, streaming,
  subscriptions, game vouchers, and zakat/donations.
- GoPay Games product brands, including mobile games, PC products, vouchers, entertainment,
  and Steam products.
- GoPay-linked merchant promotion surfaces when explicitly named in current GoPay material.
- Android-only products, when their platform condition is recorded in catalogue metadata.

### Excluded

- The open-ended QRIS merchant universe.
- Generic Gojek service marks that are not billers or products.
- Individual game/voucher denominations, price points, redemption codes, campaigns, or SKUs.
- Generic logos invented for categories such as PDAM, PBB, IPL, regional tax, regional retribution,
  or school directories.
- Historical/legacy providers until current availability is verified.

### Important PDAM decision

PDAM is confirmed as a GoPay bill-payment category, but GoPay directs the user to select a
regional PDAM type and enter a customer number. There is no single national PDAM provider mark
that can represent the directory accurately. Therefore:

- `gotagihan-pdam` exists in the catalogue as `confirmed-current` with
  `logo_decision=research-only-generic`.
- No guessed generic “PDAM” logo was placed in Figma.
- A future agent may add regional PDAM components only after recording the specific in-app biller,
  current-app date, official regional website, and exact official mark.

Reference: [GoPay PDAM payment guide](https://gopay.co.id/blog/cara-bayar-tagihan-pdam).

## 3. Repository state

### Master data totals

`data/master_list.tsv` currently contains 338 rows:

| Master category | Rows |
|---|---:|
| Bank | 181 |
| Payment | 87 |
| E-wallet | 48 |
| E-commerce | 14 |
| Minimarket | 8 |
| **Total** | **338** |

The master schema is:

```text
figma_path
institution
category
region
country
website
source_url
variant
variant_reason
aspect
background
file_link
status
notes
```

`data/master_list.csv` is the CSV mirror. Rebuild it through the scripts rather than editing it
independently.

### GoPay catalogue totals

`data/gopay_catalog.tsv` has this schema:

```text
component_name
display_name
slug
service_category
subcategory
surface
availability
official_website
evidence_url
evidence_type
source_date
catalogue_status
logo_decision
notes
```

Current status totals:

| `catalogue_status` | Rows | Meaning |
|---|---:|---|
| `confirmed-current` | 118 | Current GoPay/Gojek promo, help, or live-catalogue evidence exists. |
| `confirmed-conditional` | 1 | Confirmed only with a surface/platform/region condition. |
| `terms-only-review` | 34 | Named in static terms but not yet corroborated by current public/app evidence. |
| `legacy` | 4 | Historical, retired, or doubtful current status. |
| `excluded` | 2 | Explicitly outside the library boundary. |
| **Total** | **159** | Dated snapshot, not a permanent directory. |

The 25 generic taxonomy rows are mostly `confirmed-current` but have
`logo_decision=research-only-generic`. They document that a service category exists without
inventing a logo.

### Important repository files

| File | Purpose |
|---|---|
| [`data/gopay_catalog.tsv`](data/gopay_catalog.tsv) | Dated GoPay research catalogue and import gate. |
| [`GOPAY_CATALOG_RESEARCH.md`](GOPAY_CATALOG_RESEARCH.md) | Research methodology, evidence hierarchy, coverage, and decisions. |
| [`data/master_list.tsv`](data/master_list.tsv) | Canonical master rows used by the fetch/audit workflow. |
| [`data/source_overrides.tsv`](data/source_overrides.tsv) | Manual URL pins for ambiguous or incorrect automatic resolver results. |
| [`data/fetch_report.csv`](data/fetch_report.csv) | Last fetcher outcome/details by Figma path. |
| [`data/logo_audit.csv`](data/logo_audit.csv) | Last payment asset quality/provenance audit. |
| [`out/Logo Library - Research Index.xlsx`](out/Logo%20Library%20-%20Research%20Index.xlsx) | Generated workbook containing the current index. |
| [`scripts/import_gopay_catalog.py`](scripts/import_gopay_catalog.py) | Idempotently merges approved GoPay rows into the master list. |
| [`scripts/fetch_logos.py`](scripts/fetch_logos.py) | Candidate discovery/download workflow with provenance checks. |
| [`scripts/normalize_svg_assets.py`](scripts/normalize_svg_assets.py) | Adds missing SVG viewBoxes without changing artwork. |
| [`scripts/crop_transparent_padding.py`](scripts/crop_transparent_padding.py) | Crops known padded product rasters. |
| [`scripts/prepare_product_marks.py`](scripts/prepare_product_marks.py) | Exceptional asset cleanup and master metadata updates. |
| [`scripts/audit_assets.py`](scripts/audit_assets.py) | Asset structure, transparency, provenance, and duplicate audit. |
| [`scripts/build_sheet.py`](scripts/build_sheet.py) | Generates the XLSX workbook from the TSV. |
| [`tests/test_asset_audit.py`](tests/test_asset_audit.py) | Offline policy tests for bank/payment assets. |
| [`LOGO_LIBRARY_IMPORT_GUIDE.md`](LOGO_LIBRARY_IMPORT_GUIDE.md) | General Figma/component/asset QA rules. |
| [`README.md`](README.md) | Repository overview and deliverables. |

## 4. Figma target and current structure

### Access and page

- File URL: `https://www.figma.com/design/8M3VW9BPaSGTUHZBaH8KGg/Logos`
- Page name: `Assets`
- Page node ID: `0:1`
- File key: `8M3VW9BPaSGTUHZBaH8KGg`

### Section node IDs and counts

| Section | Node ID | Direct components |
|---|---:|---:|
| GoPay / Telco & Data / 40x40 | `63:2` | 8 |
| GoPay / Internet & TV / 40x40 | `63:3` | 8 |
| GoPay / Utilities & Bills / 40x40 | `63:4` | 3 |
| GoPay / E-money / 40x40 | `63:5` | 3 |
| GoPay / Finance & Insurance / 40x40 | `63:6` | 7 |
| GoPay / Government & Public / 40x40 | `63:7` | 5 |
| GoPay / Education & Invoicing / 40x40 | `63:8` | 2 |
| GoPay / Streaming & Subscriptions / 40x40 | `63:9` | 16 |
| GoPay / Games & Vouchers / 40x40 | `63:10` | 34 |
| GoPay / Zakat & Donations / 40x40 | `63:11` | 1 |
| Existing Merchant section | `45:3` | 18 |
| **Total** |  | **105** |

### Imported payment names by section

| Section | Imported named marks |
|---|---|
| Telco & Data | Telkomsel, Indosat (IM3), XL, AXIS, Tri, Smartfren, by.U, Telkom Fixed Line |
| Internet & TV | IndiHome, Biznet, MyRepublic, XL Satu, CBN, K-Vision, MNC Vision, Transvision |
| Utilities & Bills | PLN, BPJS Kesehatan, Pegadaian |
| E-money | Mandiri e-money, BNI TapCash, Flazz BCA |
| Finance & Insurance | AEON, BFI Finance, Home Credit, OTO Kredit Motor, OTO Kredit Mobil, Suzuki Finance, Prudential |
| Government & Public | SAMSAT JATIM, SAMSAT JATENG, SAMSAT JABAR, SAMSAT BANTEN, SAMSAT SUMUT |
| Education & Invoicing | SPIL, Paper.id |
| Streaming & Subscriptions | Existing 16 verified/current marks; see the master list and catalogue for exact slugs. |
| Games & Vouchers | 34 brand/product marks; no individual denominations or SKUs. |
| Zakat & Donations | BAZNAS |

### New Figma component IDs from the GoPay pass

These IDs are useful for inspection in the current file. Do not assume IDs will be identical in a
new Figma file or after a copy/branch operation.

| Node ID | Component slug |
|---:|---|
| `89:2` | `telco-data/telkom-fixed-line` |
| `89:5` | `internet-tv/transvision` |
| `89:8` | `internet-tv/cbn` |
| `89:11` | `internet-tv/k-vision` |
| `89:14` | `internet-tv/mnc-vision` |
| `89:17` | `utilities-bills/pegadaian` |
| `89:20` | `finance-insurance/aeon` |
| `89:23` | `finance-insurance/bfi-finance` |
| `89:26` | `finance-insurance/home-credit` |
| `89:29` | `finance-insurance/oto-kredit-motor` |
| `89:32` | `finance-insurance/oto-kredit-mobil` |
| `89:35` | `finance-insurance/suzuki-finance` |
| `89:38` | `finance-insurance/prudential` |
| `89:41` | `government-public/samsat-jatim` |
| `89:44` | `government-public/samsat-jateng` |
| `89:47` | `government-public/samsat-jabar` |
| `89:50` | `government-public/samsat-banten` |
| `89:53` | `government-public/samsat-sumut` |
| `89:56` | `education-invoicing/spil` |
| `89:59` | `education-invoicing/paper-id` |
| `89:62` | `Merchant / ID / minimarket / alfamidi` |
| `89:65` | `Merchant / ID / ecommerce / alfagift` |
| `89:68` | `Merchant / ID / ecommerce / klik-indomaret` |

Existing color corrections:

- Google Play component: `66:450`.
- Xbox component: `66:462`.

### Naming and geometry contract

New payment components use:

```text
Payment / ID / <service-category-slug> / <provider-or-product-slug>
```

New merchant components use:

```text
Merchant / ID / <merchant-category-slug> / <merchant-slug>
```

Every new component should satisfy:

```text
root component: 40 × 40, clipsContent=true, constraints=MIN/MIN
Logo frame: centered in root, each dimension ≤32, clipsContent=false, constraints=SCALE/SCALE
Artwork frame: inside Logo, clipsContent=true, max dimension ≤32
raster fills: scaleMode=FIT
vector source: recursively rescaled, no child bounds outside Artwork
```

The Logo frame is the reusable presentation wrapper used by this file. Do not place an app tile,
page screenshot, decorative background, or guessed category badge inside the Artwork source.
Existing legacy merchant components may put the vector directly under `Logo` without a nested
`Artwork` frame. They were intentionally left unchanged; their 40×40 root and proportional
Logo resize behavior passed the legacy compatibility check.

### Resize behavior

Users may resize an instance. The root component must remain square and the Logo/Artwork frames
must use `SCALE/SCALE` constraints. SVGs require recursive scaling because resizing only the
parent frame leaves native-size descendants behind and causes clipping.

Conceptual Figma plugin logic:

```js
const source = uploadOrVectorSource;
const factor = Math.min(32 / source.width, 32 / source.height);
source.rescale(factor); // scales nested vectors/groups, not only the parent frame
source.x = (artwork.width - source.width) / 2;
source.y = (artwork.height - source.height) / 2;
```

Do not use a 40×40 square distortion for a horizontal wordmark. Preserve the source ratio and
center the fitted mark inside the maximum 32×32 Artwork region.

## 5. Research evidence and availability rules

The evidence hierarchy is:

1. Current official GoPay/Gojek help, promotion pages, or live GoPay Games catalogue.
2. Current official GoPay/Gojek editorial or product material documenting a payment surface.
3. Static official GoTagihan terms for named providers not exposed publicly elsewhere. These
   rows require current in-app verification before import.
4. Official provider website for the canonical identity asset. A provider website alone does not
   prove that GoPay currently supports that provider.

The final availability source is the searchable in-app biller list. Static terms pages may contain
legacy providers. Record the source date, surface, availability condition, evidence URL, and
catalogue status in every imported row's notes/component description.

### Primary sources used

- [GoTagihan category list](https://www.gojek.com/id-id/help/gotagihan/apa-itu-gotagihan)
- [GoPay biller-directory guidance](https://gopay.co.id/bantuan/pulsa-tagihan/daftar-biller-di-pulsa-tagihan)
- [GoPulsa current promo catalogue](https://gopay.co.id/promo/gopulsa-gopay)
- [GoTagihan current promo catalogue](https://gopay.co.id/promo/gotagihan-gopay)
- [GoPay e-money help](https://gopay.co.id/bantuan/pulsa-tagihan/cara-isi-saldo-emoney)
- [GoPay Games](https://gopay.co.id/games)
- [GoTagihan terms](https://www.gojek.com/id-id/terms-and-conditions/gobills)
- [GoPay Alfamidi promotion](https://gopay.co.id/promo/alfamidi)
- [GoPay PDAM guide](https://gopay.co.id/blog/cara-bayar-tagihan-pdam)
- [Google Play visual identity](https://partnermarketinghub.withgoogle.com/brands/google-play/visual-identity/lockups-icons-badges/)
- [Home Credit GoPay payment guide](https://gopay.co.id/blog/cara-bayar-home-credit)
- [BFI official website](https://www.bfi.co.id/en?ver=eng)

## 6. Rows intentionally held out of Figma

Do not import these rows without new evidence and an explicit catalogue update.

### `confirmed-conditional`

- KMT / Kartu Multi Trip — appears in current GoPay promotion material but conflicts with the
  current e-money help list. Verify in-app before adding.

### `terms-only-review`

These are named in static GoTagihan terms or another limited source but were not approved for the
current Figma import:

- Telkomsel Halo, XL Postpaid, Indosat Postpaid, Smartfren Postpaid, Tri Postpaid.
- First Media, OkeVision, Skynindo, TOP TV / TOP Vision, WiFi.ID.
- PGN.
- Mega Finance, Mega Auto Finance, Mega Central Finance, Takaful.
- eKIR, SAMSAT SULSEL.
- Tinder, beIN SPORTS CONNECT, Genflix, Canva.
- PUBG PC.
- Baitul Maal Hidayatullah, Dompet Dhuafa, Griya Yatim dan Dhuafa, LAZISMU, LAZISNU,
  Rumah Yatim, Rumah Zakat, YDSF, LAZ Al Azhar, Inisiatif Zakat Indonesia, NH Zakat Kita,
  Laznas Yatim Mandiri.

Reasons include current-app verification still required, no exact clean canonical asset, blocked
or historical asset endpoint, or an automatic candidate that was visibly the wrong brand.

### `legacy`

- GoPlay.
- Gemscool.
- Global Zakat ACT.
- JD.ID.

### `excluded`

- QRIS merchant universe.
- Generic Gojek service logos.

### Generic taxonomy rows

These categories are retained as research metadata and must not become guessed logo components:

- Pulsa, data package, PLN token, PLN, PDAM, BPJS, Internet & Cable TV, phone postpaid,
  multifinance, e-invoicing, PGN gas, education, insurance, streaming, digital/game voucher,
  TELKOM, IPL, Pegadaian, eKIR, PBB, PKB, retribution, regional tax, zakat/donations.

Named provider rows can be added later when the in-app biller and official identity are both
verified.

## 7. Asset policy and provenance

### Preferred source order

1. Official brand/media asset from the provider or product owner.
2. Exact-match curated vector from a trusted authoritative source.
3. Clean official raster with sufficient resolution and transparency.
4. Manual vectorization only when the source is a clean, exact official mark and the result is
   documented. Never vectorize a page screenshot, app tile, social card, or cover image.

### Reject these assets

- App-store tiles and mobile app icons when the row is a business/product brand.
- Social cards, campaign art, page screenshots, banners, player/card/cover art, and favicons.
- HTML/error responses saved with an `.svg` extension.
- SVGs containing `<image>`, external references, embedded raster artwork, or unusable viewBox
  unless the specific row is explicitly documented as a controlled fallback.
- Empty vectors, broken clip paths, unused giant page/clip groups, and mislabeled marks.
- Opaque raster canvases that turn into white/black tiles without an intentional reason.
- Logos whose semantic search match is a different organization, game, sport, publisher, or
  entertainment property.

### Required provenance

For every imported row, retain:

- stable slug and Figma path;
- official website;
- exact `source_url` in `data/master_list.tsv` or `data/source_overrides.tsv`;
- evidence URL for GoPay availability;
- source date;
- surface and availability condition;
- catalogue status and logo decision;
- manual cleanup/vectorization notes;
- asset type, aspect ratio, transparency, and audit result.

`data/source_overrides.tsv` uses the Figma path as the key. Add an override when the automatic
resolver returns a wrong semantic match, an app tile, a poor variant, or an unusable endpoint.
Do not silently replace a file without recording why.

## 8. Known failures and repairs

These are regression cases. A future agent should compare new candidate assets against this list
before accepting them.

| Failure | Repair/decision |
|---|---|
| Free Fire resolved to Chicago Fire. | Reject semantic match; pin the exact Free Fire mark. |
| eFootball resolved to the Brazilian Football Confederation. | Compare visible identity, not filename; pin the eFootball mark. |
| Honor of Kings resolved to the Level Infinite publisher mark. | Use the product mark, not the publisher mark. |
| Skynindo resolved to an unrelated Haari Drama mark. | Demote to `terms-only-review`; do not import the false candidate. |
| XL resolved to an Android/app icon. | Use the canonical XL brand mark. |
| BIGO resolved to a mascot/app icon. | Use the standalone Bigo Live mark. |
| Apple Services resolved to an Apple Authorized Service Provider mark. | Use Apple Services identity, not a service-provider badge. |
| WeTV resolved to a fullscreen/social raster. | Use the standalone WeTV brand mark. |
| Football Dream arrived as player/card artwork. | Extract only the recognizable title lockup into a transparent asset. |
| Magic Chess arrived as a mascot icon. | Replace with the clean product title lockup. |
| Battlefield 6 and Dead by Daylight arrived as opaque tiles. | Use transparent title marks and crop excess transparent padding. |
| Mobile Legends/PUBG included white web canvases. | Remove the canvas and keep the exact title mark. |
| PUBG SVG lacked a usable viewBox. | Normalize the SVG before recursive Figma scaling. |
| CBN included a rounded light tile. | Remove the rounded border/canvas; retain the provider mark. |
| Transvision included a Superbrands badge. | Remove the award badge; retain only the provider wordmark. |
| Samsat Jateng source included seals and a mascot. | Crop to the central e-SAMSAT/SAMSAT regional lockup. |
| Pegadaian imported an unused giant Inkscape clip/page group. | Remove the unused clip group and audit descendant bounds. |
| OTO SVG wrapped an embedded raster. | Extract the high-resolution official mark to a transparent PNG. |
| BFI official raster had a white canvas and low headroom. | Trace the clean mark to a vector after removing the canvas; document the vectorization. |
| Paper.id light SVG rendered as a blank/white tile. | Remove the white rectangle and empty clip path; recolor only the official white wordmark paths to a readable dark variant. |
| Google Play was monochrome/wrong. | Replace with the current full-color Google Play vector. |
| Xbox was monochrome/wrong. | Replace with the current green Xbox horizontal vector. |

### Contrast rule

Black-only and white-only official variants can be legitimate. Do not arbitrarily recolor a brand
or add a decorative background inside the asset just to pass one QA surface. Run both light and
dark screenshots, record the chosen variant, and note when a mark requires a matching consumer
surface. The reusable Artwork source must remain free of invented backgrounds.

## 9. Safe future expansion workflow

### Step 0 — Preserve the working tree

Start with:

```bash
cd /Users/nikanakamanifesto/Documents/GitHub/logo-library
git status --short
rg --files | sort | sed -n '1,120p'
```

Assume existing modifications belong to the user. Do not use `git reset --hard`, `git checkout --`,
or broad destructive cleanup. Preserve unrelated bank/e-wallet/merchant work.

### Step 1 — Research before assets

1. Browse current official GoPay/Gojek pages and, when available, verify the live in-app biller
   search.
2. Add one row per named provider/product to `data/gopay_catalog.tsv`.
3. Use a stable lowercase hyphenated slug; do not include denominations or SKUs.
4. Record service category, surface, availability, official website, evidence URL, evidence type,
   source date, catalogue status, logo decision, and a short note.
5. Keep generic categories as `component_name=-` and `research-only-generic`.
6. Keep static-terms-only entries as `terms-only-review` until current-app verification.
7. Check for duplicate slugs and duplicate component paths before fetching.

The catalogue is the checkpoint. Do not fetch assets or edit Figma for rows that have not passed
the agreed review gate.

### Step 2 — Merge only approved rows

Run the idempotent importer after catalogue approval:

```bash
uv run --with requests --with beautifulsoup4 --with Pillow \\
  python scripts/import_gopay_catalog.py
```

The current importer accepts `confirmed-current` rows with `fetch-provider-mark` or
`review-source`, maps GoPay service categories to `payments/indo/...`, and maps the supported
merchant slugs to their existing `ecommerce/indo/...` or `minimarket/indo/...` paths.

The importer intentionally skips:

- generic/boundary rows;
- `confirmed-conditional` rows;
- `terms-only-review` rows;
- `legacy` rows;
- excluded rows;
- rows already present in the master list.

After merging, check that the target asset path is correct before downloading anything.

### Step 3 — Pin ambiguous sources

Add manual overrides to `data/source_overrides.tsv` before fetching when automatic discovery is
likely to return an app tile, a semantic false match, a page image, a publisher mark, or a poor
color variant.

Example:

```text
payments/indo/finance-insurance/example\thttps://example.com/brand-mark.svg
```

Keep the provider website in the master row and put the exact downloadable asset URL in the
override file when they differ.

### Step 4 — Fetch and normalize

Use a narrow prefix first:

```bash
uv run --with requests --with beautifulsoup4 --with Pillow \\
  python scripts/fetch_logos.py \\
  --only payments/indo/finance-insurance/ \\
  --delay 1.0
```

Useful options are `--dry-run`, `--limit`, `--max-candidates`, `--min-edge`, `--force`, and
`--no-robots`. Do not use `--include-sanctioned` unless the user explicitly authorizes it and the
required screening has been completed.

Then run the safe SVG normalization and targeted cleanup passes:

```bash
uv run --with requests --with beautifulsoup4 --with Pillow \\
  python scripts/normalize_svg_assets.py

uv run --with requests --with beautifulsoup4 --with Pillow \\
  python scripts/crop_transparent_padding.py

uv run --with requests --with beautifulsoup4 --with Pillow \\
  python scripts/prepare_product_marks.py
```

Review every changed asset locally. Never trust an automated candidate merely because it
downloaded successfully.

### Step 5 — Run asset policy checks

The payment audit is the authoritative current GoPay asset check:

```bash
uv run --with requests --with beautifulsoup4 --with Pillow \\
  python scripts/audit_assets.py --category payment --check
```

The current final payment audit result was:

```text
audited 87 payment row(s): accepted=69, review=18
```

The 18 reviews are nonblocking warnings such as low raster headroom or shared marks. A
`needs-replacement` result is a hard stop. The audit rejects missing files, opaque primary
rasters, invalid/embedded-raster/external-reference SVGs, app-store sources, and page/social
images for bank/payment rows.

Merchant/e-commerce legacy rows currently contain older known quality issues and were not
rewritten in this GoPay pass. Audit any new merchant asset individually and do not use the older
rows as a reason to weaken the payment policy.

### Step 6 — Rebuild data deliverables

```bash
uv run --with openpyxl python scripts/build_sheet.py
```

This rebuilds `data/master_list.csv` and `out/Logo Library - Research Index.xlsx` from the master
TSV. Do not hand-edit the generated workbook as the source of truth.

### Step 7 — Import into Figma

Before every `use_figma` call, load the Figma use/library guidance and pass:

```text
skillNames: "figma-use,figma-generate-library"
```

Figma write calls must be sequential. The safe upload sequence is:

1. Call `mcp__codex_apps__figma_upload_assets` for the required number of assets.
2. POST each returned `submitUrl` exactly once with the correct raw MIME type:
   `image/svg+xml` for SVG or `image/png` for PNG.
3. Read the returned `placedOnNodeId` and inspect the imported node.
4. For a raster, use `scaleMode=FIT` and fit it into the Artwork frame.
5. For an SVG, move/clone the editable vector tree into a `Source` child and recursively call
   `rescale(factor)` before centering it.
6. Set the component name and description with source/availability metadata.
7. Place the component in the correct existing section; do not create duplicate sections.

Keep Figma operations small enough to inspect the result. Do not leave failed upload frames,
temporary inspection nodes, or QA backgrounds in the final file.

### Step 8 — Visual QA with MCP screenshots

For each new/changed section, run `mcp__codex_apps__figma_get_screenshot` on both a light and a
dark QA background. Use `contentsOnly=true` and a sufficiently large `maxDimension` such as 1600.
Download the returned URL and inspect it with the image viewer when possible; base64 responses are
only needed when the environment cannot download the URL.

Inspect for:

- clipped vector descendants or partial wordmarks;
- giant out-of-frame clip/page groups;
- white/black canvases that are not intentional;
- app-store tiles, page screenshots, social cards, and product cover art;
- wrong business/product identity;
- wrong brand colors or monochrome substitutes;
- unreadable low-headroom marks;
- inconsistent centering or aspect-ratio distortion.

Use small screenshot batches so the images remain inspectable. Temporary QA backgrounds must be
removed after both passes.

### Step 9 — Structural and resize QA

The corrected audit should check:

- root is exactly 40×40 and `clipsContent=true`;
- root constraints are `MIN/MIN`;
- Logo is centered, max 32×32, `clipsContent=false`, `SCALE/SCALE`;
- Artwork is clipped to its own max-32 frame;
- every visible descendant remains inside Artwork;
- every vector/group descendant is scaled to fit;
- every raster image fill uses `FIT`;
- component names are unique;
- no top-level `Uploaded Image` nodes remain;
- an 80×80 instance doubles Logo/Artwork dimensions proportionally.

Do not use an overly strict audit that assumes every legacy Logo or Artwork is exactly 32×32.
Some older components preserve the source aspect ratio (for example 32×24), and some legacy
components put an image fill directly on Artwork. Test proportional scaling against the original
dimensions instead of demanding a square child.

### Step 10 — Finish and document

Before handoff:

```bash
uv run --with requests --with beautifulsoup4 --with Pillow \\
  python -m unittest discover -s tests -v

git diff --check
git status --short
```

Update all of the following when scope changes:

- `data/gopay_catalog.tsv`;
- `GOPAY_CATALOG_RESEARCH.md`;
- `LOGO_LIBRARY_IMPORT_GUIDE.md`;
- `data/source_overrides.tsv`;
- `data/master_list.tsv`/`.csv`;
- `data/logo_audit.csv`;
- `README.md` if totals or deliverables change;
- this context-transfer document if Figma IDs, counts, workflow, or known exceptions change.

## 10. Figma tool safety notes

These rules are important in the Codex desktop environment:

- Read the Figma `figma-use` skill before calling `mcp__codex_apps__figma_use_figma`.
- Pass `skillNames="figma-use,figma-generate-library"` on every Figma write call.
- Use `await figma.setCurrentPageAsync(page)` when changing pages; do not assign
  `figma.currentPage` directly.
- Do not call unsupported `loadAllPagesAsync`, `setPluginData`, or `createImageAsync`.
- Serialize Figma write operations. Parallel screenshot calls are acceptable, but keep batches
  small enough for visual review.
- Do not assume upload node IDs are stable. Only current component/section IDs are recorded here
  for convenience.
- Remove temporary nodes explicitly and verify that no `Uploaded Image` frame remains directly
  under page `0:1`.
- Preserve unrelated user changes in the dirty worktree.

## 11. Validation record for this handoff

The following checks were completed for the current state:

```text
GoPay catalogue: 159 rows
GoPay payment components: 87
Merchant section components: 18
Full sections in Figma: 10 GoPay payment sections + Merchant
Full wrapper audit checked: 90 payment/new-merchant components
Legacy merchant root/Logo audit checked: 18 components
Full wrapper failures: 0
Resize failures: 0
Duplicate names: 0
Orphan top-level uploads: 0
Payment asset audit: 69 accepted, 18 nonblocking review warnings, 0 hard failures
Unit tests: 6 passed
git diff --check: passed
Temporary QA backgrounds: removed
Temporary blank Paper.id upload: removed
```

The current Figma visual QA used both light and dark temporary backgrounds for all of these nodes:

```text
63:2  Telco & Data
63:3  Internet & TV
63:4  Utilities & Bills
63:5  E-money
63:6  Finance & Insurance
63:7  Government & Public
63:8  Education & Invoicing
63:9  Streaming & Subscriptions
63:10 Games & Vouchers
63:11 Zakat & Donations
45:3  Merchant
```

## 12. Handoff checklist

Before another agent starts implementation, confirm:

- [ ] The current date and GoPay snapshot date are recorded.
- [ ] The catalogue has been reviewed before importing new rows.
- [ ] Generic categories are not being converted into guessed logos.
- [ ] Terms-only rows are not silently promoted to current.
- [ ] New merchant rows are dated promotion surfaces, not a QRIS universe.
- [ ] Stable slugs and evidence URLs are present for every new row.
- [ ] Manual source overrides are recorded before fetching ambiguous assets.
- [ ] No app tiles, page screenshots, social cards, HTML-as-SVG, embedded-raster SVGs, or wrong
      semantic matches are accepted.
- [ ] Every new vector is recursively rescaled.
- [ ] Every raster fill uses FIT.
- [ ] Every new component is 40×40 with a centered max-32 source and proportional constraints.
- [ ] Light and dark MCP screenshots were reviewed.
- [ ] 80×80 instance tests passed.
- [ ] Temporary QA nodes and upload frames were removed.
- [ ] Audit, tests, workbook generation, documentation, and `git diff --check` passed.

If a future task conflicts with this document, follow the user's newer explicit instruction and
update this document so the next agent receives the new decision rather than the old one.
