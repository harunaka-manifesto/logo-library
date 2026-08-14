# GoPay billers and digital products catalogue

Research snapshot: **2026-08-14** (Asia/Jakarta)

This is the Phase 0 source-of-truth catalogue for the Indonesia GoPay billers and digital
products logo expansion. It is intentionally a dated snapshot: GoPay's complete biller list
is searchable inside the app and is not published as one stable public directory.

The row-level catalogue is [data/gopay_catalog.tsv](data/gopay_catalog.tsv). It contains 159
rows across the GoTagihan taxonomy, named GoTagihan providers, current GoPay Games products,
direct GoPay payment integrations, current GoPay merchant-promotion surfaces, and explicit
scope-boundary records.

## Review gate and implementation status

The Phase 0 catalogue checkpoint was approved on **2026-08-14**. Phase 1 then fetched and audited
the approved current rows and added the resulting named marks to the existing Figma file. The
implementation imports only `confirmed-current` rows with an approved logo decision; the remaining
conditional, terms-only, legacy, generic, and excluded rows stay research-only until current-app
availability and canonical identity are resolved.

Current implementation result: **87 GoPay payment components** across the ten GoPay sections,
plus **18 merchant components** in the existing merchant section. Finance & Insurance now has 7
verified marks, Government & Public has 5 regional marks, and Education & Invoicing has 2
verified e-invoicing marks. The implementation is intentionally narrower than the catalogue:
generic categories and terms-only rows remain research metadata until the dated in-app biller
search confirms a named provider and a canonical mark.

## Scope and boundaries

Included:

- GoTagihan categories and named billers for Indonesia.
- GoPay Games product brands currently exposed by the public catalogue, without individual
  denominations, price points, or SKUs.
- Direct GoPay payment/subscription surfaces documented in official GoPay/Gojek help.
- Android-only products, with the limitation recorded in `availability`.
- Named zakat and donation organisations found in current official material or the official
  GoTagihan terms page.

Excluded:

- The open-ended QRIS merchant universe.
- Generic Gojek service marks that are not a biller or product provider.
- Individual game/voucher denominations and campaign variants.
- A generic logo for a directory category such as PDAM, PBB, IPL, or regional retribution.
  These categories remain in the catalogue as research metadata; only named, verifiable
  operators can become Figma components.

PDAM is a confirmed GoPay bill-payment category, but it is a regional directory: the user
selects a local PDAM type and enters a customer number. There is no single national PDAM
provider mark to import, so `gotagihan-pdam` remains catalogue metadata rather than a guessed
logo. Regional PDAM operators can be added later when the current in-app directory and an
official provider mark are both recorded.

## Source hierarchy

The catalogue uses the following evidence order:

1. Current official GoPay/Gojek help, promo, or live GoPay Games catalogue evidence.
2. Current official GoPay/Gojek product or editorial material that describes a payment
   integration.
3. The official GoTagihan terms page for named providers that are not exposed by the current
   public promo pages. These rows are not automatically current and require an in-app check.
4. Official provider websites for identity and later asset provenance. The provider website
   is not, by itself, proof that GoPay currently supports the provider.

The final availability source is the searchable in-app biller list. The official directory
guidance explains that users should open Pulsa/Tagihan, choose **Lihat semua**, and search
there for the biller. This means the catalogue should be re-dated whenever the Figma library
is expanded rather than treated as a timeless directory.

## Official evidence used

- [GoTagihan category list](https://www.gojek.com/id-id/help/gotagihan/apa-itu-gotagihan) —
  current taxonomy: top-ups/data, bills, public services, e-money, finance, insurance,
  education, e-invoicing, streaming, and digital/game vouchers; several are labelled
  Android-only.
- [GoPay biller-directory guidance](https://gopay.co.id/bantuan/pulsa-tagihan/daftar-biller-di-pulsa-tagihan) —
  the full provider list is searched in-app, not copied from a static web table.
- [Current GoPulsa promo catalogue](https://gopay.co.id/promo/gopulsa-gopay) — current
  examples for Telkomsel, Indosat, XL, AXIS, Tri, Smartfren, and by.U.
- [Current GoTagihan promo catalogue](https://gopay.co.id/promo/gotagihan-gopay) — current
  examples for PLN, PLN Pascabayar, PDAM, BPJS, Mandiri e-money, Flazz BCA, KMT, BNI
  TapCash, IndiHome, XL Satu, MyRepublic, Biznet, PBB, PKB JABAR, phone postpaid, and
  multifinance.
- [GoPay e-money help](https://gopay.co.id/bantuan/pulsa-tagihan/cara-isi-saldo-emoney) —
  explicitly names Mandiri e-money, BNI TapCash, and Flazz BCA. KMT is deliberately flagged
  for verification because it appears in current promo material but not in this help page.
- [GoPay Games](https://gopay.co.id/games) and [all games](https://gopay.co.id/games/semua-game) —
  current product-brand catalogue for mobile games, PC games, vouchers, entertainment, and
  Steam products. Product denominations are not rows.
- [Official GoTagihan terms](https://www.gojek.com/id-id/terms-and-conditions/gobills) —
  named provider evidence for static terms rows, including regional Samsat, utilities,
  internet/TV, postpaid telecom, finance, insurance, education, e-invoicing, and zakat.
  Static terms may contain historical entries, so they are not treated as current by default.
- [GoPay/Gojek GoPay help index](https://www.gojek.com/id-id/help/gopay) plus the direct
  pages for [Netflix](https://www.gojek.com/id-id/help/gopay/pembayaran-di-netflix),
  [Spotify](https://www.gojek.com/id-id/help/gopay/pembayaran-di-aplikasi-spotify),
  [Google Play](https://www.gojek.com/id-id/help/gopay/pembayaran-di-google-play-store),
  YouTube Premium/Music, Disney+, and Apple Services — direct payment integrations.
- [GoPay subscription fallback article](https://gopay.co.id/blog/metode-pembayaran-cadangan) —
  current article evidence for subscription transactions such as Canva; Canva remains
  review-only until the live payment flow is verified.
- [GoPay BAZNAS article](https://gopay.co.id/blog/gopay-kembali-raih-penghargaan-dari-baznas-ri) —
  current evidence that GoPay's Zakat/Donations feature remains accessible and that BAZNAS
  is a named provider.
- [GoPay digital-services page](https://gopay.co.id/bayar) — supports the boundary decision
  that a broad digital-service/merchant universe must not be silently treated as a finite
  logo list.

## Catalogue status meanings

| Status | Meaning | Figma consequence |
|---|---|---|
| `confirmed-current` | Current official GoPay/Gojek promo, help, or live catalogue evidence exists. | Eligible for asset research after approval and provenance checks. |
| `confirmed-conditional` | Reserved for a product confirmed only for a surface, region, or platform condition. | Eligible only with the condition written into component metadata. |
| `terms-only-review` | Named in static official terms but not corroborated by current public catalogue/help evidence. | Do not fetch until the current in-app biller search confirms it. |
| `legacy` | Historical/possibly retired entry or a product whose current status is doubtful. | Do not import; retain as a warning for future re-check. |
| `excluded` | Explicitly outside this library's boundary. | Never import. |

Current row totals:

- `confirmed-current`: 118
- `terms-only-review`: 34
- `confirmed-conditional`: 1
- `legacy`: 4
- `excluded`: 2

The 25 taxonomy rows use `logo_decision=research-only-generic`; they document the available
service category without inventing a provider logo. Named rows use one of
`fetch-provider-mark`, `review-source`, or `exclude`.

## Category coverage

| Figma section | Catalogue rows | Imported components | Notes |
|---|---:|---:|---|
| `GoPay / Telco & Data / 40x40` | 17 | 8 | Prepaid providers plus postpaid/fixed-line names. |
| `GoPay / Internet & TV / 40x40` | 14 | 8 | Current promo examples plus verified named provider marks. |
| `GoPay / Utilities & Bills / 40x40` | 10 | 3 | PLN, BPJS, and Pegadaian; PDAM/PGN remain regional or review-only metadata. |
| `GoPay / E-money / 40x40` | 5 | 3 | Mandiri e-money, BNI TapCash, and Flazz BCA; KMT remains conditional. |
| `GoPay / Finance & Insurance / 40x40` | 14 | 7 | AEON, BFI, Home Credit, OTO, Suzuki Finance, and Prudential; terms-only rows remain review metadata. |
| `GoPay / Government & Public / 40x40` | 12 | 5 | Named regional Samsat marks; generic tax/public-service categories remain metadata. |
| `GoPay / Education & Invoicing / 40x40` | 4 | 2 | SPIL and Paper.id; generic school rows remain metadata. |
| `GoPay / Streaming & Subscriptions / 40x40` | 22 | 16 | Direct integrations and current entertainment brands. |
| `GoPay / Games & Vouchers / 40x40` | 37 | 34 | Current game/product brands; no denominations or SKUs. |
| `GoPay / Zakat & Donations / 40x40` | 15 | 1 | BAZNAS is verified; other named providers remain terms-only. |
| Existing `Merchant / ID / … / 40x40` | 6 GoPay promo rows | 18 total | Alfamidi, Alfagift, and Klik Indomaret were added alongside existing Alfamart, Indomaret, and Tokopedia marks. |

The category counts include generic taxonomy and terms-only rows where applicable; the TSV
`catalogue_status` and `logo_decision` columns are the import filters. The merchant rows are a
dated promotion snapshot, not a claim to enumerate every QRIS or GoPay merchant.

## Implementation addenda and regression findings

The following findings came from the first GoPay import and are now part of the repeatable
workflow:

- A resolver's semantic match can be wrong even when the filename looks plausible. The
  `skynindo` candidate resolved to an unrelated Haari Drama mark, so it was rejected and left
  `terms-only-review`.
- The CBN source included a rounded light tile; the border was removed before import. The
  Transvision source included a Superbrands award badge; only the provider wordmark was kept.
- The official Samsat Jateng artwork included seals and a mascot around the actual lockup; the
  source was cropped to the regional e-SAMSAT/SAMSAT wordmark. Pegadaian's unused Inkscape clip
  group was removed because it imported as a giant out-of-frame descendant.
- OTO's official SVG wrapped an embedded raster, so the high-resolution official mark was
  extracted to a transparent PNG. BFI's clean official raster was vectorized after its white
  canvas was removed.
- Paper.id's official light SVG contained a white rectangle and an empty clip path. The
  transparent dark wordmark is derived from that exact official source and is now checked in
  with the cleanup recorded in the master data.
- Google Play and Xbox were replaced with current full-color brand vectors. App-store tiles,
  cover art, social cards, and generic app icons remain prohibited even when they are visually
  convenient.

## Product deduplication decisions

- Prepaid and postpaid products are one provider mark when the canonical brand is shared;
  product-specific rows remain when GoPay names a distinct service or current mark.
- `PUBG Mobile` covers both the mobile-game and voucher catalogue entries.
- `Point Blank` covers both the PC game and Voucher Cash entries.
- `Steam`, `Google Play`, `PSN`, `Vidio`, `Spotify`, and `Viu` are one brand row even when
  they appear on more than one GoPay surface.
- Historical Vidio FIFA offers and all game/voucher denominations are product variants, not
  separate logo components.
- `Free Fire` and `Free Fire MAX` remain separate because GoPay exposes them as separate
  product brands.
- Steam catalogue titles are retained as product rows, but their `review-source` decision
  requires a clean, recognizable title mark; a game-cover screenshot is not an acceptable
  logo asset.

## Logo decision rules for the next phase

Only rows with a named provider/product and an approved availability decision can become
components. Asset research must follow the existing
[Logo Library Import and QA Guide](LOGO_LIBRARY_IMPORT_GUIDE.md):

- fetch the canonical business/product mark, not an app-store tile, social card, page
  screenshot, or favicon;
- prefer official brand/media assets, then exact-match curated vectors, then clean official
  rasters;
- reject HTML disguised as SVG, embedded-raster SVGs, empty vectors, mislabeled marks, and
  visually clipped imports;
- use the existing 40x40 wrapper with a centered maximum 32x32 `Logo` source frame;
- recursively scale SVG descendants before fitting, preserve the source aspect ratio, and
  verify light/dark screenshots plus 80x80 instance resizing;
- record the exact asset URL and availability evidence in the master data and provenance
  records.

## Review questions before Phase 1

1. Approve or remove any rows marked `terms-only-review` after checking the current GoPay
   in-app biller search.
2. Confirm whether the library should include the Steam Game title rows as title marks, or
   keep them research-only until a canonical identity asset is found.
3. Confirm the desired treatment of `KMT`: include after in-app confirmation, or keep it out
   because the current e-money help page does not list it.
4. Confirm whether current GoPay Games entertainment products should live in the Streaming
   section (the proposed grouping) rather than the Games & Vouchers section.

The approved implementation extended the fetcher, audit, sheet builder, and tests, then imported
the approved rows into the Figma sections in small batches with light/dark `get_screenshot` QA.
The resolver findings and exceptional cleanup decisions are recorded in
`LOGO_LIBRARY_IMPORT_GUIDE.md`; existing bank, e-wallet, and merchant sections remain unchanged.
