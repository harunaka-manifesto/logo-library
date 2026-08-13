#!/usr/bin/env python3
"""Build the 'Logo Library - Research Index' workbook from data/master_list.tsv.

Produces a two-tab .xlsx (README + Master List) that Google Drive converts to a
native Google Sheet on upload.
"""
import csv
import pathlib

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "master_list.tsv"
OUT = ROOT / "out" / "Logo Library - Research Index.xlsx"

HEADERS = [
    "Figma Path", "Institution Name", "Category", "Region", "Country",
    "Official Website", "Logo Source URL", "Variant Chosen", "Variant Reasoning",
    "Native Aspect Ratio", "Background Type", "Downloaded File Link", "Status", "Notes",
]
WIDTHS = [34, 32, 12, 12, 9, 34, 30, 14, 46, 30, 16, 22, 18, 78]

HEAD_FILL = PatternFill("solid", fgColor="1F3864")
HEAD_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(bold=True, size=14, color="1F3864")
SECT_FONT = Font(bold=True, size=11, color="1F3864")
WARN_FILL = PatternFill("solid", fgColor="FCE4D6")
EXCL_FILL = PatternFill("solid", fgColor="F2F2F2")
REVIEW_FILL = PatternFill("solid", fgColor="FFF2CC")

SCOPE = [
    ("1", "Banks", "Indonesia", "banks/indo/{name}"),
    ("2", "E-wallets", "Indonesia", "ewallets/indo/{name}"),
    ("3", "Minimarkets / convenience stores", "Indonesia", "minimarkets/indo/{name}"),
    ("4", "E-commerce platforms", "Indonesia", "ecommerce/indo/{name}"),
    ("5", "Banks", "SEA, per country", "banks/sea/{country}/{name}"),
    ("6", "E-wallets", "SEA, per country", "ewallets/sea/{country}/{name}"),
    ("7", "Banks", "International", "banks/international/{name}"),
    ("8", "E-wallets / remittance", "International", "ewallets/international/{name}"),
]

COLDEFS = [
    ("Figma Path", "The exact future layer name, e.g. banks/sea/sg/dbs"),
    ("Institution Name", "Common display name"),
    ("Category", "bank / ewallet / minimarket / ecommerce"),
    ("Region", "Indonesia / SEA / International"),
    ("Country", "ISO alpha-2 for SEA rows; blank for Indonesia/International"),
    ("Official Website", "Institution's own site. Compiled from research, NOT opened/confirmed this pass."),
    ("Logo Source URL", "Exact page the asset was pulled from. EMPTY this pass - nothing was pulled."),
    ("Variant Chosen", "icon / wordmark / app-icon. This pass records a RECOMMENDATION, not a chosen file."),
    ("Variant Reasoning", "1-line why this variant is recommended"),
    ("Native Aspect Ratio", "TBD this pass - cannot be measured without the asset. Expectation only."),
    ("Background Type", "TBD this pass - cannot be determined without the asset."),
    ("Downloaded File Link", "Link to the file in the Drive folder. EMPTY this pass."),
    ("Status", "Verified / Needs Review / Flagged - Excluded"),
    ("Notes", "Anything a human should know before the Figma pass"),
]

LEGEND = [
    ("Verified", "Institution confirmed against its regulator's register AND an official asset downloaded. "
                 "NOT USED in this pass - neither check was possible (see blocker above)."),
    ("Needs Review", "Row is a researched candidate. Regulator confirmation and asset sourcing still outstanding. "
                     "Per-row Notes give the specific reason."),
    ("Flagged - Excluded", "Do not source an asset. Entity is defunct, exited the market, or discontinued. "
                           "Reason given in Notes."),
]

BLOCKER = [
    "STATUS OF THIS PASS - READ FIRST",
    "",
    "Phase 1 (research / master list) is delivered. Phases 2 (download assets) is NOT, and Phase 3 is delivered "
    "with asset-dependent columns empty.",
    "",
    "Reason: the environment this ran in has an egress policy that allows GitHub only. Every other host - brand "
    "sites, press kits, app stores, Wikimedia Commons, regulator registries (OJK, BI, MAS, BNM, BOT, BSP, SBV) - "
    "was refused at the proxy with HTTP 403 on CONNECT. Both the shell and the page-fetch tool are subject to that "
    "same policy, so no logo file could be downloaded and no registry page could be opened. Web search was "
    "available and was used, which is how the market-status findings below were established.",
    "",
    "What that means for this sheet:",
    "  - No logo files exist yet. The Drive asset folders are an empty scaffold.",
    "  - 'Logo Source URL', 'Downloaded File Link', 'Native Aspect Ratio' and 'Background Type' are empty or TBD "
    "on every row. They were deliberately left blank rather than guessed - a plausible-looking but unopened URL "
    "would be worse than an empty cell.",
    "  - 'Official Website' is compiled from research and general knowledge. Treat as a starting point to confirm, "
    "not as verified fact.",
    "  - 'Variant Chosen' is a reasoned recommendation based on how each brand's mark is normally used. It was NOT "
    "chosen by comparing downloaded candidates, as Phase 2 step 2 intends.",
    "  - No row is marked 'Verified', because the verification the brief defines was not possible.",
    "",
    "To finish the job: re-run the sourcing pass in an environment whose egress policy permits brand/press-kit "
    "domains, app store endpoints, Wikimedia Commons and the regulator registries. This sheet is the worklist for "
    "that run - the institution list, paths, and variant guidance carry over unchanged.",
]

FINDINGS = [
    ("7-Eleven Indonesia", "Excluded. Operator PT Modern Internasional closed all remaining stores effective "
                           "30 June 2017."),
    ("JD.ID", "Excluded. Ceased Indonesian operations 31 March 2023, as the brief anticipated."),
    ("Moca (Vietnam)", "Excluded. Grab terminated the Moca e-wallet effective 1 July 2024. The brief still lists it "
                       "as a live candidate."),
    ("Sakuku (BCA)", "Excluded. BCA wound the wallet down; users migrated to myBCA. Confirm final closure date."),
    ("Lawson Indonesia", "Needs Review. Alfamart has acquired Lawson's Indonesian stores. The brand may be retained, "
                         "converted or retired - a human should decide before an asset is sourced."),
    ("Bukalapak", "Needs Review, still trading. Ceased physical-goods marketplace in Feb 2025 and now sells virtual "
                  "products and digital services only. Confirm it still belongs in an e-commerce grouping."),
    ("Bank BTPN", "Renamed PT Bank SMBC Indonesia Tbk effective 2 Oct 2024. Row is filed as banks/indo/smbc-indonesia. "
                  "Do not use a BTPN-era asset."),
    ("Singtel Dash", "Filed as ewallets/sea/sg/dash. Singtel agreed to sell Dash to Western Union (announced Oct 2024), "
                     "so the Singtel-badged asset is stale."),
    ("OCBC NISP / KB Bukopin", "Both rebranded (to OCBC Indonesia and KB Bank). Pre-rebrand assets are stale."),
    ("Maya (Philippines)", "Rebranded from PayMaya. Do not use a PayMaya-era asset."),
    ("ttb (Thailand)", "Post-merger identity of TMB + Thanachart. Legacy assets are stale."),
    ("Citibank Indonesia", "Consumer banking sold to UOB in 2023. Confirm it still belongs in a consumer payment UI."),
    ("Myanmar (KBZ Bank, KBZPay)", "Marked Needs Review with no asset, per the brief's sanctions instruction. Screen "
                                   "against current OFAC/EU/UK designations before any use."),
    ("Regional brand duplication", "GrabPay and ShopeePay appear once per country per the brief's per-country path "
                                   "convention. If one shared asset is preferred, collapse these rows before the "
                                   "Figma pass."),
    ("Indonesia path prefix", "Indonesia uses 'indo' while SEA countries use ISO alpha-2, per the brief. Flagging as "
                              "the brief asked: switching Indonesia to 'id' would make the whole tree consistent."),
]


def build_readme(ws):
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 26
    ws.column_dimensions["C"].width = 24
    ws.column_dimensions["D"].width = 60
    r = 1
    ws.cell(r, 1, "Logo Library - Research Index").font = TITLE_FONT
    r += 1
    ws.cell(r, 1, "Multi-region payment & retail logo research. Sheet + Drive scaffold pass.").font = Font(italic=True)
    r += 2

    for line in BLOCKER:
        c = ws.cell(r, 1, line)
        if line.startswith("STATUS OF THIS PASS"):
            c.font = Font(bold=True, size=12, color="C00000")
            c.fill = WARN_FILL
        elif line.endswith(":"):
            c.font = SECT_FONT
        r += 1
    r += 1

    ws.cell(r, 1, "Naming convention (scope overview)").font = SECT_FONT
    r += 1
    for i, h in enumerate(["#", "Category", "Region", "Naming path (for later Figma use)"], start=1):
        c = ws.cell(r, i, h)
        c.font = HEAD_FONT
        c.fill = HEAD_FILL
    r += 1
    for row in SCOPE:
        for i, v in enumerate(row, start=1):
            ws.cell(r, i, v)
        r += 1
    r += 1

    ws.cell(r, 1, "SEA country codes").font = SECT_FONT
    r += 1
    ws.cell(r, 1, "sg Singapore | my Malaysia | th Thailand | ph Philippines | vn Vietnam | "
                  "kh Cambodia | mm Myanmar | la Laos | bn Brunei. Indonesia keeps the 'indo' prefix.")
    r += 2

    ws.cell(r, 1, "Column definitions (Master List)").font = SECT_FONT
    r += 1
    for i, h in enumerate(["Column", "Purpose"], start=1):
        c = ws.cell(r, i, h)
        c.font = HEAD_FONT
        c.fill = HEAD_FILL
    r += 1
    for name, purpose in COLDEFS:
        ws.cell(r, 1, name)
        ws.cell(r, 2, purpose).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    r += 1

    ws.cell(r, 1, "Status legend").font = SECT_FONT
    r += 1
    for i, h in enumerate(["Status", "Meaning"], start=1):
        c = ws.cell(r, i, h)
        c.font = HEAD_FONT
        c.fill = HEAD_FILL
    r += 1
    for name, meaning in LEGEND:
        ws.cell(r, 1, name)
        ws.cell(r, 2, meaning).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    r += 1

    ws.cell(r, 1, "Market-status findings that change the brief's starting lists").font = SECT_FONT
    r += 1
    for i, h in enumerate(["Entity", "Finding"], start=1):
        c = ws.cell(r, i, h)
        c.font = HEAD_FONT
        c.fill = HEAD_FILL
    r += 1
    for name, finding in FINDINGS:
        ws.cell(r, 1, name)
        ws.cell(r, 2, finding).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1

    # merge the wide explanatory column for the B-column text blocks
    for row in range(1, r + 1):
        if ws.cell(row, 1).value and not ws.cell(row, 2).value:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        elif ws.cell(row, 2).value and not ws.cell(row, 3).value:
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)


def build_master(ws, rows):
    for i, h in enumerate(HEADERS, start=1):
        c = ws.cell(1, i, h)
        c.font = HEAD_FONT
        c.fill = HEAD_FILL
        c.alignment = Alignment(vertical="center", wrap_text=True)
    for i, w in enumerate(WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 30

    for r, row in enumerate(rows, start=2):
        for i, v in enumerate(row, start=1):
            c = ws.cell(r, i, v)
            c.alignment = Alignment(vertical="top", wrap_text=i in (9, 14))
        status = row[12]
        fill = EXCL_FILL if "Excluded" in status else REVIEW_FILL
        ws.cell(r, 13).fill = fill
        if row[5]:
            link = ws.cell(r, 6)
            link.hyperlink = row[5]
            link.font = Font(color="0563C1", underline="single")

    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:N{len(rows) + 1}"


def main():
    with open(SRC, encoding="utf-8") as fh:
        rows = list(csv.reader(fh, delimiter="\t"))[1:]
    for r in rows:
        assert len(r) == len(HEADERS), (r[0], len(r))

    wb = Workbook()
    build_readme(wb.active)
    wb.active.title = "README"
    build_master(wb.create_sheet("Master List"), rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"wrote {OUT}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
