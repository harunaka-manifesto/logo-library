# Checkpoint — 2026-08-13

Resume point for continuing this session tomorrow. Read this top to bottom before doing
anything else; the "Do this first" section at the bottom is the actual next step.

## Where things stand

- **Branch:** `claude/payment-retail-logo-research-9gxjfr`, pushed. Latest commit: `71113c7`.
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
  **Run #3 was triggered** (`workflow_dispatch` with `commit: true`) immediately after
  diagnosing this, on the stable head `76f42e0` with nothing else queued to push mid-run. Check
  its status first when resuming - it may have finished successfully overnight. If it also
  failed to push (unlikely now, but possible if you or I push something to this branch while
  it's running), the fix is the same: don't push to this branch while a `commit: true` run is
  in flight, and re-trigger.

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

1. **Check on run #3** (Actions tab → "Fetch logos" → latest run, triggered tonight with
   `commit: true` on the stable head `76f42e0`). This is the one that actually matters — it has
   every fetch-quality fix (128px floor, domain-logo resolver, token matching, scoring fix) and
   nothing should have raced its push this time. Expect it to take roughly the same ~80 minutes
   run #2 did (249 rows, ~1 request/sec with politeness delay).
   - If it succeeded: the assets are already committed to this branch. Skip to step 3.
   - If it failed on the same "Commit assets" push step: check whether anything else pushed to
     this branch while it ran (`git log --oneline -5`) - that's the only way this specific
     failure mode recurs. Its `logo-assets` artifact still has everything even if the commit
     step failed; either re-trigger, or `git fetch`+manually apply the artifact's `assets/`,
     `data/master_list.tsv`, `data/master_list.csv` and `data/fetch_report.csv` on top of current
     head yourself if you don't want to re-spend the ~80 minutes.
   - If it failed somewhere else (not the commit step): that's a genuinely new failure mode,
     not one that's already been diagnosed - read the actual step logs before assuming anything.
2. **Read `data/fetch_report.csv`** (now on the branch, or from the artifact) for the real
   outcome breakdown - counts of `downloaded` / `unresolved` / `unusable` / `skipped` / `exists`.
   This is the number that tells you whether the fixes actually moved the needle, not a guess.
   If a particular category still misses a lot, pull a few example rows and check the `detail`
   column for the actual reason rather than assuming.
3. **Re-import the Sheet.** Open the Sheet link above → File → Import → Upload →
   `data/master_list.csv` → "Replace current sheet". This does not change the Sheet's URL. Worth
   doing regardless of the fetch outcome, just to reflect the current 249-row list.
4. **For any row that still misses**, use `data/source_overrides.tsv` — add a line
   `<figma_path><TAB><direct image URL>` and re-run; overrides beat every automated resolver.
   Manual sourcing options discussed: Wikipedia infobox images, Brandfetch.com, the institution's
   own press/investor-relations page.
5. **While a `commit: true` run is in flight, don't push to this branch** — that's exactly what
   caused run #2's push failure. If you want to make code changes while a run is executing,
   queue them and push only after it finishes (or after cancelling it).

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
