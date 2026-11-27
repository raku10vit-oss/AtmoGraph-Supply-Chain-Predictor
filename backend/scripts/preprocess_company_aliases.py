"""
AtmoGraph – Company Alias Preprocessing Script
===============================================
Reads data/raw/company_merges.csv (245 rows: variant → canonical)
and data/raw/company_attributes.csv (10 rows: canonical → country/industry override)
and builds two lookup dicts written to data/processed/company_aliases.json.

Outputs:
  data/processed/company_aliases.json

Run from project root or backend/:
    python backend/scripts/preprocess_company_aliases.py
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

MERGES_PATH  = os.path.join(_REPO_ROOT, "data", "raw", "company_merges.csv")
ATTRS_PATH   = os.path.join(_REPO_ROOT, "data", "raw", "company_attributes.csv")
OUT_PATH     = os.path.join(_REPO_ROOT, "data", "processed", "company_aliases.json")

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing: pandas")


def build_cache() -> dict:
    print(f"Loading merges:     {MERGES_PATH}")
    print(f"Loading attributes: {ATTRS_PATH}")

    # ── Alias table: variant → canonical ─────────────────────────
    aliases: dict[str, str] = {}
    if os.path.exists(MERGES_PATH):
        df_merges = pd.read_csv(MERGES_PATH)
        for _, row in df_merges.iterrows():
            variant   = str(row["variant"]).strip()
            canonical = str(row["canonical"]).strip()
            if variant and canonical and variant != canonical:
                aliases[variant.lower()] = canonical
        print(f"  Alias pairs loaded: {len(aliases)}")
    else:
        print(f"  WARNING: {MERGES_PATH} not found — alias table will be empty")

    # ── Attribute overrides: canonical → {field: value} ──────────
    overrides: dict[str, dict] = {}
    if os.path.exists(ATTRS_PATH):
        df_attrs = pd.read_csv(ATTRS_PATH)
        for _, row in df_attrs.iterrows():
            company = str(row["company"]).strip()
            field   = str(row["field"]).strip()
            value   = str(row["value"]).strip()
            if company not in overrides:
                overrides[company] = {}
            overrides[company][field] = value
        print(f"  Attribute overrides loaded: {len(overrides)} companies")
    else:
        print(f"  WARNING: {ATTRS_PATH} not found — attribute overrides will be empty")

    return {
        "version":    "1.0",
        "sources":    ["company_merges.csv", "company_attributes.csv"],
        "alias_count": len(aliases),
        "override_count": len(overrides),
        "aliases":    aliases,
        "overrides":  overrides,
    }


def main():
    print("=" * 60)
    print("  AtmoGraph – Company Alias Cache Builder")
    print("=" * 60)

    cache = build_cache()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"\n  ✅ Written → {OUT_PATH}")
    print(f"  Aliases:   {cache['alias_count']}")
    print(f"  Overrides: {cache['override_count']}")
    # Show a few examples
    sample_aliases = list(cache["aliases"].items())[:5]
    for variant, canonical in sample_aliases:
        print(f"    '{variant}' → '{canonical}'")
    print("=" * 60)


if __name__ == "__main__":
    main()
