#!/usr/bin/env python3
"""Merge approved GoPay catalogue rows into the existing master list.

Only named rows with confirmed-current catalogue evidence and an asset decision
are imported. Conditional rows (such as KMT, which needs current in-app
verification), generic categories, terms-only rows, legacy rows, and explicit
exclusions stay in data/gopay_catalog.tsv until their status is resolved.
"""
from __future__ import annotations

import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "master_list.tsv"
CATALOG = ROOT / "data" / "gopay_catalog.tsv"
MASTER_CSV = ROOT / "data" / "master_list.csv"

HEADERS = [
    "figma_path", "institution", "category", "region", "country", "website",
    "source_url", "variant", "variant_reason", "aspect", "background", "file_link",
    "status", "notes",
]

APPROVED_STATUSES = {"confirmed-current"}
APPROVED_DECISIONS = {"fetch-provider-mark", "review-source"}

CATEGORY_SLUGS = {
    "Telco & Data": "telco-data",
    "Internet & TV": "internet-tv",
    "Utilities & Bills": "utilities-bills",
    "E-money": "e-money",
    "Finance & Insurance": "finance-insurance",
    "Government & Public": "government-public",
    "Education & Invoicing": "education-invoicing",
    "Streaming & Subscriptions": "streaming-subscriptions",
    "Games & Vouchers": "games-vouchers",
    "Zakat & Donations": "zakat-donations",
}

MERCHANT_PATHS = {
    "alfamart": "minimarkets/indo/alfamart",
    "alfamidi": "minimarkets/indo/alfamidi",
    "indomaret": "minimarkets/indo/indomaret",
    "alfagift": "ecommerce/indo/alfagift",
    "klik-indomaret": "ecommerce/indo/klik-indomaret",
    "tokopedia": "ecommerce/indo/tokopedia",
}


def _field(value: str) -> str:
    value = value.strip()
    return "" if value == "-" else value


def _variant(service_category: str, subcategory: str) -> str:
    """Use a compact identity hint without turning it into an app-icon policy."""
    if service_category in {"E-money", "Games & Vouchers", "Government & Public"}:
        return "icon"
    if "Mobile game" in subcategory or "PC game" in subcategory or "Voucher" in subcategory:
        return "icon"
    return "wordmark"


def _row(catalogue: dict[str, str]) -> list[str]:
    category = catalogue["service_category"]
    slug = catalogue["slug"]
    component = catalogue["component_name"]
    if category == "Merchant & Retail":
        figma_path = MERCHANT_PATHS[slug]
        master_category = "minimarket" if figma_path.startswith("minimarkets/") else "ecommerce"
    else:
        path_category = CATEGORY_SLUGS[category]
        figma_path = f"payments/indo/{path_category}/{slug}"
        master_category = "payment"
    source_status = catalogue["catalogue_status"]
    decision = catalogue["logo_decision"]
    website = _field(catalogue["official_website"])
    notes = (
        f"GoPay catalogue status={source_status}; surface={catalogue['surface']}; "
        f"availability={catalogue['availability']}; evidence={catalogue['evidence_url']}; "
        f"evidence type={catalogue['evidence_type']}; source date={catalogue['source_date']}; "
        f"logo decision={decision}. {catalogue['notes']}"
    )
    return [
        figma_path,
        catalogue["display_name"],
        master_category,
        "Indonesia",
        "id",
        website,
        "",
        _variant(category, catalogue["subcategory"]),
        f"Canonical provider/product mark for {component}; never use an app-store tile or page image.",
        "",
        "",
        "",
        "Needs Review",
        notes,
    ]


def main() -> int:
    with MASTER.open(encoding="utf-8", newline="") as fh:
        master_rows = list(csv.reader(fh, delimiter="\t"))
    if master_rows[0] != HEADERS:
        raise SystemExit("master_list.tsv header does not match expected schema")

    existing_paths = {row[0] for row in master_rows[1:]}
    with CATALOG.open(encoding="utf-8", newline="") as fh:
        catalogue_rows = list(csv.DictReader(fh, delimiter="\t"))

    # Keep the merge idempotent while allowing a previously imported conditional
    # row to be withdrawn when verification is still outstanding.
    conditional_paths = set()
    for row in catalogue_rows:
        if row["catalogue_status"] in APPROVED_STATUSES or row["component_name"] == "-":
            continue
        if row["service_category"] in CATEGORY_SLUGS:
            conditional_paths.add(f"payments/indo/{CATEGORY_SLUGS[row['service_category']]}/{row['slug']}")
        elif row["service_category"] == "Merchant & Retail" and row["slug"] in MERCHANT_PATHS:
            conditional_paths.add(MERCHANT_PATHS[row["slug"]])
    master_rows = [master_rows[0]] + [
        row for row in master_rows[1:] if row and row[0] not in conditional_paths
    ]

    imported: list[list[str]] = []
    skipped: dict[str, int] = {}
    for row in catalogue_rows:
        if row["component_name"] == "-":
            skipped["generic-or-boundary"] = skipped.get("generic-or-boundary", 0) + 1
            continue
        if row["catalogue_status"] not in APPROVED_STATUSES:
            skipped[row["catalogue_status"]] = skipped.get(row["catalogue_status"], 0) + 1
            continue
        if row["logo_decision"] not in APPROVED_DECISIONS:
            skipped[row["logo_decision"]] = skipped.get(row["logo_decision"], 0) + 1
            continue
        if row["service_category"] not in CATEGORY_SLUGS and not (
            row["service_category"] == "Merchant & Retail" and row["slug"] in MERCHANT_PATHS
        ):
            raise SystemExit(f"unknown GoPay service category: {row['service_category']}")
        target_path = (
            MERCHANT_PATHS[row["slug"]]
            if row["service_category"] == "Merchant & Retail"
            else f"payments/indo/{CATEGORY_SLUGS[row['service_category']]}/{row['slug']}"
        )
        if target_path in existing_paths:
            skipped["already-in-master"] = skipped.get("already-in-master", 0) + 1
            continue
        imported.append(_row(row))
        existing_paths.add(target_path)

    master_rows.extend(imported)
    with MASTER.open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, delimiter="\t", lineterminator="\n").writerows(master_rows)
    with MASTER_CSV.open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, lineterminator="\n").writerows(master_rows)

    print(f"imported {len(imported)} approved GoPay rows into data/master_list.tsv")
    for key in sorted(skipped):
        print(f"skipped {key}: {skipped[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
