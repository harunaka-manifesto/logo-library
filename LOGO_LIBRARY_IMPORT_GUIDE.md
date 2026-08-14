# Logo Library Import and QA Guide

This guide is the acceptance contract for adding logos to the Figma library. It applies to
banks, e-wallets, remittance services, minimarkets, marketplaces, merchants, and future
categories.

The library's reusable asset is a 40 × 40 component. The artwork is centered in a maximum
32 × 32 box so the component has 4 px of breathing room on every side at its default size.
The component itself must remain square and must scale uniformly when a user resizes an
instance.

## Non-negotiable acceptance rules

Do not publish a logo until all of these are true:

- It is the business's canonical mark or wordmark, not an app-store tile, phone-home-screen
  icon, social-media card, web-page screenshot, partner badge, or favicon stand-in.
- The source is traceable: record the exact URL, source type, retrieval date, file type, and
  any licence or attribution requirement.
- SVGs are real, self-contained vectors with a valid `viewBox`; reject HTML error pages,
  embedded raster images, external references, and empty or invisible paths.
- Raster sources have a clean transparent or intentionally documented background, enough
  resolution for the intended use, and no baked-in page/card chrome. Do not upscale a poor
  raster merely to meet a size target.
- The logo is visually recognizable at 40 × 40 on both a light and a dark QA background.
  A low-contrast color variant is a source/variant problem, not a reason to add a white
  rectangle to an otherwise transparent library component.
- The Figma component passes the geometry and resize checks below, and a screenshot review
  has been completed for the whole section.

When a canonical asset cannot be verified, hold the row for review or use a clearly labelled
neutral fallback. Never silently turn an app icon into the primary business logo.

## Naming convention

Use stable, slash-delimited names so Figma search and future additions remain predictable:

| Category | Figma component name |
|---|---|
| Indonesian e-wallet | `Ewallet / ID / <slug>` |
| Global/international e-wallet | `Ewallet / INT / <slug>` |
| Country-specific international wallet | `Ewallet / <ISO country> / <slug>` |
| Indonesian merchant/minimarket | `Merchant / ID / <subtype> / <slug>` |

Use lowercase kebab-case for `<slug>`. Keep the slug stable when the source changes. Do not
put file extensions, source names, size labels, or version numbers in the component name.

The repository path should mirror the category where possible, for example
`assets/ewallets/indo/gopay.svg` or `assets/ecommerce/indo/tokopedia.svg`. Keep the dataset
row, source URL, Figma component name, and asset filename aligned through a manifest or the
existing `data/master_list.tsv` / `data/source_overrides.tsv` records.

## Source selection and provenance

Use this order of preference:

1. The brand's official press, media, newsroom, developer, or brand-guidelines asset.
2. A clean asset served by the official brand website, if it is the canonical mark rather
   than a favicon or app tile.
3. A reputable curated logo repository containing an exact identity match, with its licence
   recorded. The Indonesian vector pass used the `idn-finlogos` package selectively; verify
   the package version and licence again when expanding the scope.
4. A clean official raster only when a trustworthy vector is unavailable.
5. A neutral review fallback when the identity or current artwork is unresolved.

For every accepted asset, record at least:

```text
figma path | component name | source URL | source type | retrieved at |
format | native width/height | measured aspect ratio | background type |
variant (wordmark/mark/lockup) | licence/attribution | review status | notes
```

Search results and image-search thumbnails are discovery aids, not provenance. Before import,
compare the candidate against the official site or brand media source. If an aggregated
vector is used, confirm the silhouette, colors, wordmark, and current/relevant variant.

## Canonical logo versus app icon

This distinction is mandatory for payment and merchant categories:

- A canonical business logo is the official wordmark, symbol, or lockup used in the brand's
  identity/website/press materials.
- An app icon is the square artwork used in an app store or on a phone. It may be a useful
  clue, but it is not the primary business logo unless the brand explicitly uses that icon as
  its standalone identity and the decision is documented.
- Reject images with app-store badges, device frames, ratings, promotional copy, rounded
  square tiles, social post chrome, or a screenshot around the mark.
- If a brand has both a wordmark and a symbol, choose the canonical variant that remains
  legible at 40 × 40. Do not redraw a wordmark as an icon without recording that it is a
  deliberate compact variant.
- If the only available candidate is an app icon, keep it in a review queue or label the
  component/metadata as `app-icon`; do not present it as a verified business logo.

## SVG import procedure

The most important Figma rule is: **never shrink only the imported SVG parent**.

When a source SVG is imported, Figma can create a frame/group whose child vectors retain
their native dimensions. Calling `resizeWithoutConstraints()` on that parent changes its
box but does not necessarily scale the nested vectors. The component then looks like a
clipped fragment at 40 × 40 even though the SVG file itself is valid.

Use this sequence for every imported vector:

1. Inspect the imported source tree and reject malformed files before placing it in a
   component.
2. Scale the source recursively with `source.rescale(factor)` so the nested paths/groups
   scale with the frame.
3. Fit the resulting artwork to a maximum dimension of 32 px while preserving its measured
   aspect ratio. For a horizontal wordmark, use `32 × (32 / ratio)`; for a tall mark, use
   `(32 × ratio) × 32`.
4. Recalculate the union of every descendant's `absoluteBoundingBox`. Resize/reposition the
   source frame so no child extends beyond it. Allow a small floating-point tolerance only;
   do not ignore a visible overflow.
5. Center the source frame inside the 40 × 40 component. Leave the source frame's
   `clipsContent` off; the component root is the final safety boundary.
6. Run the recursive overflow audit and inspect a screenshot at native size.

The invariant is:

```text
max(descendant width/height) <= 32 px
every descendant bounds is inside the Logo source frame
Logo is centered in the 40 × 40 root
```

### SVG rejection checks

Before import, check that the downloaded response is actually an SVG. A file with an `.svg`
extension can contain an HTML error page. Reject a source when any of these is true:

- the payload begins with HTML/error markup instead of `<svg` (an observed TikTok Shop
  failure);
- the SVG has no usable `viewBox` or has zero-size geometry;
- it relies on external files, remote fonts, or an embedded raster image;
- all visible fills/strokes are transparent, white-on-white, or otherwise absent in QA;
- the paths form a visibly different or mislabeled brand mark (an observed MoneyGram source
  was actually a TikTok-shaped white path).

If an SVG imports as a diagonal fragment or a partial word, inspect the child bounds and
source transforms first. Do not “fix” it by randomly enlarging the component or by masking
the fragment.

## Raster import procedure

Use raster artwork only when it is the best trustworthy source. Before upload:

- inspect the image at native resolution;
- remove page whitespace only when it is clearly accidental and the underlying mark is
  intact;
- remove baked social/meta-card backgrounds, taglines, promotional text, and app-store
  chrome only when the resulting crop still represents the official mark;
- preserve the source aspect ratio and use Figma `scaleMode: "FIT"`;
- verify the uploaded Figma image frame uses the image's real intrinsic ratio, not a default
  placeholder such as 400 × 300;
- never stretch a logo to fill a square frame.

If a PNG is an app tile or a social/meta card, replacing it with a clean official wordmark
or a carefully verified vector is preferred to tracing it blindly. Vectorization is allowed
only when the result is visually faithful and the source/licence decision is recorded.

## Figma component contract

Every published logo component must have this structure:

```text
Component: 40 × 40, square, clipsContent = true
└── Logo: centered source frame, max dimension 32, clipsContent = false
    └── one imported vector/raster source
```

Apply these constraints:

- component root: `MIN / MIN`, `clipsContent = true`, and proportions constrained;
- `Logo` source frame: `SCALE / SCALE` constraints;
- keep the source artwork as one editable vector tree or one image fill;
- do not add labels, backgrounds, or decorative masks inside the reusable logo component;
- do not leave temporary uploaded sources as unrelated top-level page assets.

Users can then resize any instance to 80 × 80, 120 × 120, or another square size while the
artwork remains proportional. The component root is the 1:1 contract; the logo's native
wordmark ratio is preserved inside it.

## Screenshot and visual QA

For each new or repaired section:

1. Select the entire section and run Figma MCP `get_screenshot` at a resolution large enough
   to inspect the smallest wordmarks.
2. Inspect the section on its normal background for clipping, missing paths, broken colors,
   and alignment.
3. Temporarily use a white or very light QA background to expose dark/black artwork and a
   dark QA background to expose white artwork. This is a QA-only change; restore the
   section's intended styling afterward.
4. Zoom into every suspicious mark and compare it with the fetched source and an official
   reference. A screenshot is required even when the structural audit passes.
5. Re-run the screenshot after repairs. Do not close the pass based only on the first
   screenshot or on the fact that a source file is technically valid.

The current library pass specifically found that several marks looked acceptable only after
the background was changed for contrast; this is why both background checks are now required.

## Automated acceptance audit

Run a structural audit against every component in the section. It should verify:

- exactly one `Logo` child and the expected component/root dimensions;
- 40 × 40 root, square proportions, root clipping, and `MIN / MIN` constraints;
- `SCALE / SCALE` constraints on the `Logo` frame;
- all descendant bounds are inside the source frame within a small tolerance;
- all descendant width/height values are at most 32 px after recursive scaling;
- no duplicate component names, missing names, or orphan top-level upload nodes;
- an 80 × 80 instance test produces a 2× logo box and preserves the source ratio;
- raster fills use FIT and vector sources contain real vector children.

Stop the import if any check fails. Do not hide a failure by turning clipping on inside the
source frame, flattening a broken vector, or adding an oversized mask.

## Findings recorded from the e-wallet and merchant pass

These are concrete failure modes that must not recur:

- **App-store tiles:** many initial PNG candidates for GoPay, OVO, DANA, ShopeePay,
  LinkAja, and merchant brands were app-store tiles rather than business marks. They were
  replaced with clean, editable brand vectors or held to the canonical source policy.
- **Parent-only SVG shrinking:** imported vectors were made 32 px by resizing only their
  parent frame. Their nested paths stayed at native size, so the 40 px component clipped
  partial words and symbols. Recursive `rescale()` plus descendant-bound auditing is now
  required.
- **Mislabeled SVG:** a MoneyGram file contained a white TikTok-like path. File extension and
  filename are not identity proof; compare the visible mark with a trusted reference.
- **HTML masquerading as SVG:** the TikTok Shop SVG payload was an HTML/error response. Check
  the payload and SVG structure before import.
- **Embedded-image SVG:** the first AstraPay source imported as a diagonal/fragmented pattern
  because it relied on embedded image content. Replace it with a self-contained vector.
- **Bad raster crops:** Orami arrived as a social/meta-style card and Sociolla as an
  app-icon-like raster. The accepted Figma sources were cleaned/cropped to the official
  wordmarks and fitted using their real aspect ratios.
- **Wrong/low-contrast variant:** a logo can be structurally correct but visually disappear
  on the section background. The white-background contrast pass exposed this; both light and
  dark screenshots are now part of QA while keeping the reusable component background-free.
- **Edge overflow after scaling:** LinkAja, AstraPay, DOKU, FamilyMart, and Revolut had
  small-to-visible descendant-bound overflows after the first scaling pass. Their source
  frames/content positions were corrected, and the final audit reported zero overflows.
- **WorldRemit raster quality:** the prior source was replaced with a clean official wordmark
  raster and fitted to the measured ratio rather than forcing it into a square.

The prior repaired e-wallet/merchant scope contains 34 components with 34 unique names. The
post-repair audit passed with zero geometry failures, and 80 × 80 resize tests preserved the
uniform scale behavior. The later GoPay expansion adds 87 payment components and three new
merchant components, bringing the existing Merchant section to 18 components.

## GoPay-specific catalogue and import rules

The GoPay expansion is an Indonesia-only, dated snapshot. The approved research source is
`data/gopay_catalog.tsv`, with its methodology and review gate in
`GOPAY_CATALOG_RESEARCH.md`. For every future scope, prepare and review this dated catalogue
before asset fetching or Figma edits.

- **Treat the in-app list as the final availability source.** GoPay's public help explains
  that the complete biller list is searchable inside the app. Public promo pages and static
  terms are evidence, not a permanent directory. Record the catalogue snapshot date and
  re-check the in-app result before importing a row.
- **Separate availability from identity.** A provider can have an official website and still
  be a legacy or unavailable GoPay biller. `terms-only-review` rows require current in-app
  confirmation; `legacy` rows are not fetched. Never promote a static terms entry directly to
  a component.
- **Label surface and platform conditions.** Keep `GoTagihan`, `GoPay Games`, direct GoPay
  integration, and other surfaces in the row metadata. Mark Android-only products explicitly;
  do not imply iOS availability from an Android-only GoTagihan category.
- **Use provider/product marks, not category or app tiles.** PDAM, PBB, IPL, regional tax,
  education, and similar directory categories do not have one universal logo. Keep generic
  categories as research metadata and import only named, verifiable operators. PDAM is a
  confirmed GoPay category, but it resolves to regional operators rather than one national
  provider mark; record the regional directory and do not invent a generic PDAM logo. A game or
  subscription's app-store icon is not its business/product mark unless the brand explicitly
  uses that mark as its canonical standalone identity.
- **Keep Games at brand level.** GoPay Games mixes mobile games, PC games, vouchers,
  entertainment, Steam titles, and denominations. Create one row/component per product brand,
  not per price, region, redemption code, campaign, or SKU. Deduplicate a brand that appears on
  more than one GoPay surface; record the additional surfaces in metadata.
- **Be conservative with game title artwork.** A cover image, promotional card, character
  art, or product screenshot is not automatically a logo. Use a clean official title mark only
  when it remains recognizable at 40 × 40; otherwise leave the row as `review-source` until a
  canonical asset is verified.
- **Record contradictions instead of smoothing them over.** KMT appears in current GoPay
  promo material while the current e-money help page names Mandiri e-money, BNI TapCash, and
  Flazz BCA. Keep KMT as a conditional review row until the current app resolves the conflict.
- **Assume terms pages can be stale.** The static GoTagihan terms page contains useful named
  billers, regional Samsat services, and historical entertainment/charity products. It also
  contains entries that may be retired or rebranded. Preserve the evidence URL, but require
  current-app verification before fetching any terms-only mark.
- **Do not infer missing provider websites.** If a named regional authority, product, or
  organisation has no verified official website, keep the field unresolved and use the GoPay
  evidence for availability. Do not replace it with a guessed domain or an image-search URL.
- **Keep scope boundaries explicit.** The open-ended QRIS merchant universe and generic Gojek
  service marks are excluded. Do not expand the payment catalogue into an unbounded merchant
  list simply because GoPay supports QRIS or many digital services. Merchant-promotion rows such
  as Alfamidi, Alfagift, and Klik Indomaret are dated surfaces, not an exhaustive QRIS directory.
- **Carry the research decision into provenance.** Every imported payment row must retain its
  slug, source date, surface, availability condition, evidence URL, catalogue status, and logo
  decision in the master data/source-overrides records. A logo asset without the availability
  decision is incomplete.

## GoPay implementation findings (2026-08-14)

The first GoPay implementation exposed several resolver and asset-cleanup failures that must be
treated as explicit regression cases in later expansions:

- **Semantic matches are not identity proof.** The resolver matched `Free Fire` to Chicago Fire,
  `eFootball` to the Brazilian Football Confederation, and `Honor of Kings` to the Level Infinite
  publisher mark. Those rows were pinned to manually checked product marks in
  `data/source_overrides.tsv`. Always compare the visible mark with the named product and its
  official reference; a plausible filename or search result is not enough.
- **App and service icons are not interchangeable with product marks.** XL first resolved to an
  Android/app icon, BIGO to a mascot/app icon, Apple Services to an Apple Authorized Service
  Provider mark, and WeTV to a fullscreen/social raster. These were rejected or replaced with
  canonical standalone brand marks. The no-app-tile policy applies to payment, subscription,
  and game rows just as it does to banks.
- **Game artwork needs a title-mark decision.** Football Dream initially arrived as promotional
  player/card artwork; only the recognizable title lockup was extracted into a transparent PNG.
  Magic Chess initially resolved to a mascot icon and was replaced with a clean title lockup.
  Cover art, character art, and campaign cards must never enter a reusable logo component.
- **Opaque raster tiles need a source replacement, not just a smaller frame.** Battlefield 6 and
  Dead by Daylight first used opaque 600x600 white tiles. The accepted sources are transparent
  wordmarks with transparent padding cropped by `scripts/crop_transparent_padding.py`.
  Mobile Legends and PUBG had white web canvases; `scripts/prepare_product_marks.py` removes the
  canvas and records the cleanup in the master list. PUBG's earlier SVG also lacked a usable
  `viewBox`; normalize the source before Figma import rather than relying on a parent resize.
- **Contrast is a source-selection check.** Biznet's full wordmark had poor dark-background
  headroom, so the official bright icon was used; MyRepublic was changed from a black-only mark
  to a colored vector; Mobile Legends, PUBG, and Genshin were pinned to colored exact-match
  marks. Black-only and white-only brand variants may still be intentionally background-specific:
  do not recolor or add a decorative background inside the reusable component. Run both light and
  dark screenshots, record the chosen variant, and tell consumers when a mark requires a matching
  surface.
- **Shared marks and source-size warnings are review metadata.** XL and XL Satu legitimately
  share the XL source, while several clean raster wordmarks are below the preferred 256px headroom.
  Record `exact-duplicate/shared-mark` or `low-headroom` as a review warning; do not “fix” either
  by inventing a different logo or upscaling a small source.
- **Populate named sections when evidence and identity are both ready.** Finance & Insurance,
  Government & Public, and Education & Invoicing are now populated with verified named marks:
  AEON/BFI/Home Credit/OTO/Suzuki Finance/Prudential; regional Samsat marks; and SPIL/Paper.id.
  Keep generic categories and unresolved terms-only rows in research metadata rather than filling
  them with guessed category logos.
- **Repair exceptional official assets before Figma.** CBN's rounded tile, Transvision's
  Superbrands badge, Samsat Jateng's surrounding seals/mascot, Pegadaian's unused Inkscape clip,
  and OTO's embedded-raster SVG were all cleaned or extracted before import. Paper.id's official
  light SVG had a white canvas and empty clip path; remove both and recolor only the white
  wordmark paths to a readable dark variant derived from the same official source.
- **Color corrections must be brand-accurate.** Google Play and Xbox were replaced with current
  full-color vectors after monochrome or wrong variants were found. Keep the exact source URL and
  reason in `data/source_overrides.tsv` whenever a resolver result is replaced.

The approved GoPay pass imported 87 payment marks. The importer accepts only `confirmed-current`
rows with an approved logo decision, so KMT (`confirmed-conditional`) and all `terms-only-review`,
`legacy`, generic, and excluded rows remain out of Figma until their availability and identity are
resolved. The repeatable cleanup order is: pin ambiguous sources, fetch, validate payload type,
normalize exceptional SVGs, crop or remove justified raster padding/canvases, run the asset audit,
then perform Figma recursive scaling, light/dark screenshots, and the 80 × 80 instance test.

## Expansion checklist

Before handing off a new category, confirm:

- [ ] dataset rows and slugs are unique and follow the path convention;
- [ ] every source has provenance, licence notes, and a current/relevant variant decision;
- [ ] no app-store tile, page screenshot, social card, favicon, HTML payload, or mislabeled
      vector is being used as the primary mark;
- [ ] every SVG was recursively scaled and its descendant bounds audited;
- [ ] every raster was inspected, cropped only when justified, and uploaded with FIT;
- [ ] every component is 40 × 40 with a centered max-32 Logo source and the correct constraints;
- [ ] light and dark section screenshots were reviewed through Figma MCP `get_screenshot`;
- [ ] the automated geometry/name/resize audit passes with zero failures;
- [ ] temporary QA backgrounds and any temporary inspection nodes were removed/restored;
- [ ] unresolved identity decisions are labelled for human review instead of guessed.
- [ ] GoPay rows are dated snapshots and current-app availability was checked for every
      terms-only or conditional provider;
- [ ] Android-only and surface-specific products are labelled in component metadata;
- [ ] generic bill categories were kept as research metadata rather than assigned guessed
      logos;
- [ ] GoPay Games products were deduplicated at brand level and denominations/SKUs were not
      imported;
- [ ] contradictions between current promo/help pages and static terms were recorded and
      resolved before import;
- [ ] QRIS merchant-universe and generic Gojek-service boundaries were not expanded silently.
