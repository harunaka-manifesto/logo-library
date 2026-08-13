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

To finish the job, re-run the sourcing pass in an environment whose egress policy permits
brand/press-kit domains, app-store endpoints, Wikimedia Commons and the regulator registries.
This dataset is the worklist for that run: institution list, paths and variant guidance all
carry over unchanged.

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
| `out/` | Generated workbook |

## Naming convention

| # | Category | Region | Naming path (for later Figma use) |
|---|---|---|---|
| 1 | Banks | Indonesia | `banks/indo/{name}` |
| 2 | E-wallets | Indonesia | `ewallets/indo/{name}` |
| 3 | Minimarkets | Indonesia | `minimarkets/indo/{name}` |
| 4 | E-commerce | Indonesia | `ecommerce/indo/{name}` |
| 5 | Banks | SEA, per country | `banks/sea/{country}/{name}` |
| 6 | E-wallets | SEA, per country | `ewallets/sea/{country}/{name}` |
| 7 | Banks | International | `banks/international/{name}` |
| 8 | E-wallets / remittance | International | `ewallets/international/{name}` |

SEA country codes are ISO 3166-1 alpha-2, lowercase: `sg` `my` `th` `ph` `vn` `kh` `mm` `la`
`bn`. Indonesia keeps the `indo` prefix for continuity. **Flagged as the brief asked:**
switching Indonesia to `id` would make the whole tree consistent.

## Status legend

| Status | Meaning |
|---|---|
| `Verified` | Institution confirmed against its regulator's register **and** an official asset downloaded. **Not used in this pass** — neither check was possible. |
| `Needs Review` | Researched candidate. Regulator confirmation and asset sourcing still outstanding. Per-row `notes` give the specific reason. |
| `Flagged - Excluded` | Do not source an asset. Entity is defunct, exited the market, or discontinued. Reason in `notes`. |

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
| bank | 69 |
| ewallet | 45 |
| ecommerce | 12 |
| minimarket | 8 |
| **Total** | **134** |

Of these, 130 are `Needs Review` and 4 are `Flagged - Excluded`.

## Licensing note

These are third-party trademarks across many jurisdictions. Intended for internal reference
and UI design work only, not redistribution.
