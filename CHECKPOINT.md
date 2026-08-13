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
- **GitHub Actions "Fetch logos" workflow run #2** (id `31715978369`) was *still in_progress*
  as of the last check tonight, running on commit `b7b5c82` — i.e. **before** the fetch-quality
  fixes in `71113c7` (size floor, domain-logo resolver, app-store matching, scoring bug). Its
  result, whenever it finishes, reflects the old resolver behavior and is not representative of
  what the current code will produce. Don't be alarmed by a high miss rate in that run's report —
  it's expected, and already fixed in code that just hasn't been run yet.

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

1. **Check on run #2** (https://github.com/harunaka-manifesto/logo-library/actions/runs/31715978369).
   If it finished, its `fetch_report.csv` artifact is a useful *baseline* (old resolver code) but
   not the number to judge quality by — the real test is the next run.
2. **Trigger a fresh run** on the Actions tab → "Fetch logos" → "Run workflow" (a new dispatch,
   not "re-run", so it picks up `71113c7`). Recommend starting with `dry_run: true` and
   `only: banks/indo` to sanity-check the new hit rate on a fast slice before committing to the
   full ~249-row run. If that looks good, run for real with `commit: true` so the downloaded
   assets land back on this branch.
3. **Compare miss rates** between the two runs' `fetch_report.csv` (download as workflow
   artifacts) to confirm the fixes actually moved the needle. If misses are still high in a
   particular category, pull a few example rows and check `outcome`/`detail` columns for the
   actual reason (unresolved vs. unusable vs. skipped) rather than assuming.
4. **Re-import the Sheet.** Once you're happy with a fetch run's results (or even just to reflect
   the current 249-row list), open the Sheet link above → File → Import → Upload →
   `data/master_list.csv` → "Replace current sheet". This does not change the Sheet's URL.
5. **For any row that still misses**, use `data/source_overrides.tsv` — add a line
   `<figma_path><TAB><direct image URL>` and re-run; overrides beat every automated resolver.
   Manual sourcing options discussed: Wikipedia infobox images, Brandfetch.com, the institution's
   own press/investor-relations page.

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
