# Checkpoint — 2026-08-13

Resume point for continuing this session tomorrow. Read this top to bottom before doing
anything else; the "Do this first" section at the bottom is the actual next step.

## Where things stand

- **Branch:** `claude/payment-retail-logo-research-9gxjfr`, pushed. Latest commit: `22be826`.
- **249/249 rows fetched:** 208 downloaded, 26 unusable, 9 unresolved, 6 skipped (see below).
  Real asset files are on the branch under `assets/`.
- **Master list:** 249 rows in `data/master_list.tsv` / `data/master_list.csv`.
- **Drive:**
  - Folder: https://drive.google.com/drive/folders/14iGABfKzcp5k5kbNE9wrIaZIABcFl3H2
  - Sheet: https://docs.google.com/spreadsheets/d/11TnjRb0cC3tbXxYi-OofEM9kX5xQ00OQNDXx1x-gD3s/edit
  - README doc: https://docs.google.com/document/d/1FfJ9O1CjdbSolCESIC38ogwp8gWXrTVoNIv97CbA_0w/edit
  - **The Sheet is stale** — it still has the row count from before the international expansion
    and the fetch-quality fixes. It needs a re-import from `data/master_list.csv` before it's
    trustworthy again (see "Do this first" below). The Sheet has no update-in-place API in this
    session's toolset, so it has to be manually re-imported each time the data changes
    meaningfully — this has not been done since the international-corridor expansion.
- **GitHub Actions "Fetch logos" workflow run #2** (id `31715978369`, commit `b7b5c82`,
  *before* the fetch-quality fixes) **finished but its final step failed**: the actual fetch
  step succeeded (ran ~80 min, downloaded real assets - shopeepay.png, alipay.png,
  wechat-pay.png, revolut.svg, alfamart.png, indomaret.png, and more), but the "Commit assets"
  step's `git push` was rejected as a non-fast-forward, because commits `71113c7` and `76f42e0`
  landed on the branch *while the run was executing* (the runner checked out the branch at
  15:32, the fix commits landed ~15:31-16:52 in this same session). The downloaded assets from
  that run are not lost - they're in the run's `logo-assets` artifact - but that artifact isn't
  worth recovering: it reflects the pre-fix 512px floor, not the current 128px one, so a fresh
  run beats it on both correctness (no push race) and quality (has the fixes).
  **Run #3 hit the identical failure** - this time because I pushed the checkpoint-update
  commit 5 minutes after triggering it, racing its own 87-minute fetch. Rather than lose real
  data a second time: fixed `fetch-logos.yml`'s commit step to retry-with-rebase (5 attempts,
  handles the branch moving mid-run automatically from now on), added
  `.github/workflows/recover-artifact.yml` (given a run ID, downloads that run's `logo-assets`
  artifact and commits it - no need to redo the fetch), and used it to recover run #3's results
  without re-paying the 87 minutes.

  **Result: 208 of 249 rows downloaded successfully (83.5%)** - a big jump from the ~50% seen
  before the fix commit. Already committed to this branch (commit `22be826`) and confirmed
  correct: e.g. `banks/indo/bca` resolved to a real vector logo pulled directly from BCA's own
  CDN, with measured aspect ratio and background type written back. No row is auto-marked
  `Verified` - that's still a human call, by design.

  Remaining 41 rows: 9 `unresolved` (no candidate found at all - all have no `website` filled
  in, e.g. `banks/indo/smbc-indonesia`, `banks/indo/mizuho-indonesia`,
  `banks/indo/anz-indonesia`, `minimarkets/indo/alfaexpress`, `ecommerce/indo/ralali` - these
  were left blank on purpose per their Notes, pending a human decision), 26 `unusable`
  (candidates found but none passed even the 128px floor - worth a look, since some rows like
  `banks/indo/bni` found 24 candidates and still came up empty, which smells systematic rather
  than "this bank just has no big logo" and hasn't been root-caused yet), 6 `skipped` (4
  `Flagged - Excluded` + the 2 Myanmar sanctioned rows, exactly as expected).

## Session narrative (why things are the way they are)

1. Built the initial 134-row master list + README + Drive scaffold + Sheet. Egress was blocked
   in that session (GitHub-only proxy policy), so no logos could actually be downloaded — every
   asset-dependent column was left empty/TBD rather than guessed.
2. User pointed out the Indonesia bank list wasn't exhaustive → expanded from 30 to 101 banks
   (private nationals, digital banks, sharia banks, foreign/JV banks, all BPDs). Total 134→205.
3. Built `scripts/fetch_logos.py` (multi-source resolver: brand-site scrape → app-store icon →
   domain-logo API → Wikimedia → favicon-service fallback) plus a `workflow_dispatch` GitHub
   Actions workflow (`.github/workflows/fetch-logos.yml`) so fetching can run somewhere with open
   network, since this session's sandbox can't reach the internet.
4. User asked to expand International to match what Wise/PandaRemit actually deliver to from
   Indonesia → added 44 bank rows + 3 e-wallet rows across 11 countries (US/GB/DE/FR/NL/CN/AU/
   CA/JP/KR/HK), converted the international bank path convention from flat to per-country
   (matching the SEA pattern). Total 205→249.
5. Caught and fixed a real bug myself: those 44 new rows had no `website` filled in, which two
   of the fetcher's resolvers require to do anything — fixed before it could matter.
6. First GitHub Actions run looked stuck at 30 minutes → investigated via the GitHub API,
   found it wasn't stuck (logs just aren't streamable mid-run through the API, and Python
   block-buffers stdout under Actions anyway — fixed with `PYTHONUNBUFFERED: "1"`), but it
   *was* running stale code (pre-dated the international expansion) — cancelled, restarted
   as run #2 on the current commit.
7. User reported run #2 was ~50% misses at ~203/249 rows, and separately noted the real
   on-screen logo size is only ~40-64px (not the brief's original 512px Figma-frame assumption).
   Root-caused three real problems by reading the resolver code (not guessing) and fixed all
   three, landing in `71113c7`:
   - Size floor was 512px, discarding perfectly good 180×180 `apple-touch-icon.png` assets and
     most brand-site favicons. Lowered default to 128px (still `--min-edge`-tunable) since
     40-64px CSS display only needs ~128px raw for 2x retina headroom.
   - Added `resolve_domain_logo` (Clearbit's `logo.clearbit.com/{domain}`) as a new source,
     for sites whose logo isn't a clean `<img>`/`<link rel=icon>` (inline-SVG headers, CSS
     background-image logos, JS-rendered chrome that plain scraping can't see).
   - App-store name matching was strict substring containment, which fails names shaped like
     "Bank Rakyat Indonesia (BRI)" against an app titled "BRI Mobile" — switched to
     stopword-stripped token-overlap matching.
   - Found a real scoring bug via a new test: "matches recommended variant" was checked before
     "official vs. aggregated source" in the ranking tuple, so a last-resort favicon-service hit
     could beat a genuinely better brand-site/domain-logo hit just because the weak source
     happened to carry a matching `kind` label. Reordered so source quality wins first.
   - Added 6 new offline tests (28 total, all passing) covering all of the above.
8. This checkpoint was written before triggering a fresh run against `71113c7` — that's
   tomorrow's first move.

## Do this first tomorrow

1. **Re-import the Sheet.** Open the Sheet link above → File → Import → Upload →
   `data/master_list.csv` → "Replace current sheet". Does not change the Sheet's URL. This
   hasn't been done since the fetch completed, so the Sheet still shows empty asset columns for
   208 rows that now actually have them.
2. **Spot-check a sample of the 208 `downloaded` rows** against the actual institution - the
   resolver is automated and nothing is marked `Verified`, by design. `banks/indo/bca` checked
   out correctly (real BCA-hosted SVG); worth eyeballing a handful more, especially any `icon`
   or `app-icon` variant picks, before trusting the batch.
3. **Root-cause the `unusable` rows before just raising `--min-edge` further** -
   `banks/indo/bni` found 24 candidates and still failed the 128px floor, which is suspicious
   for a major bank's own site. Worth pulling `data/fetch_report.csv`'s `detail` column for a
   few of these 26 rows to see what was actually being rejected (raw favicon.ico? blocked by
   robots.txt so only the weak fallback candidates got tried?) rather than assuming the floor
   is still too high.
4. **The 9 `unresolved` rows all have an empty `website` column on purpose** - each one's Notes
   explain why (pending a rebrand-domain confirmation for `smbc-indonesia`, "wholesale only,
   confirm scope" for `mizuho-indonesia`/`mufg-indonesia`/`anz-indonesia`/`bank-of-china-indonesia`,
   uncertain operating status for `alfaexpress`/`ralali`, plus `kb-bank-syariah` and
   `victoria-syariah`). Resolve the underlying question first (an actual human call, not
   something the fetcher can do), then fill in the site and re-run just that row with
   `--only <path> --force`.
5. **For anything that still misses after that**, use `data/source_overrides.tsv` — add a line
   `<figma_path><TAB><direct image URL>` and re-run with `--force`; overrides beat every
   automated resolver. Manual sourcing options already discussed: Wikipedia infobox images,
   Brandfetch.com, the institution's own press/investor-relations page.
6. **While a `commit: true` run is in flight, don't push to this branch.** The retry-with-rebase
   fix means a stray push won't lose the run's results anymore, but it'll still cost the ~5x25s
   worth of retry/rebase cycles for no reason - just avoid it.

## Useful references

- Fetcher: `scripts/fetch_logos.py` — run `--help` for all flags. Key ones: `--dry-run`,
  `--only <prefix>`, `--min-edge` (default 128), `--limit`, `--include-sanctioned` (for the two
  Myanmar rows, which are otherwise skipped per the brief's sanctions guardrail).
- Sheet-builder: `scripts/build_sheet.py` — regenerates `out/*.xlsx` (two-tab README + Master
  List) from `data/master_list.tsv`. Run this after any data edit.
- Offline test suite (not committed to the repo — lives in this session's scratchpad, so if
  starting a genuinely new session it needs rewriting, but the checks it covers are listed in
  step 7 above and worth re-deriving if `fetch_logos.py` changes again):
  `/tmp/claude-0/-home-user-logo-library/a5c75977-fc6f-5bdc-b571-eed546c32f60/scratchpad/test_fetch.py`
- Full commit history so far, oldest first:
  - `12153b9` Add multi-region payment & retail logo research index
  - `7d1870e` Condense row notes, publish to Drive, link deliverables
  - `724970a` Add logo fetcher and expand Indonesia bank coverage to 101
  - `087e697` Expand International to Wise/PandaRemit remittance corridors
  - `1a8b9ba` Fill missing website URLs on the new international rows
  - `b7b5c82` Unbuffer Python stdout in the fetch-logos workflow
  - `71113c7` Raise the fetch hit rate (size floor, domain-logo source, app-store matching,
    scoring bug)

## Known open items / not yet done

- Sheet not re-imported since the international expansion (see step 4 above).
- No fetch run has completed on the current (fixed) resolver code yet.
- Inline `<svg>` logos (embedded directly in a page's HTML, not referenced by URL) aren't
  harvested by `resolve_brand_site` — only `<img src>`, `<link rel=icon>`, and `og:image`. This
  is a known gap, not yet fixed; the domain-logo resolver added tonight covers some of this gap
  indirectly but not all of it.
- `Bank Commonwealth` (Indonesia) and `Bank Banten` were flagged in Notes as likely candidates
  for `Flagged - Excluded` (Commonwealth being absorbed into OCBC Indonesia; Banten's capital
  troubles) but not moved there — still `Needs Review`, needs a human call.
- Regional brand duplication (GrabPay/ShopeePay appearing once per SEA country = 4 rows each)
  was flagged as an open question in the README, not resolved either way.
- Indonesia's `indo` vs. `id` path-prefix inconsistency (vs. the ISO-alpha-2 codes used
  everywhere else) was flagged per the brief's own request but not changed.
