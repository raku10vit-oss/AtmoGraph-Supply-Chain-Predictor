"""
AtmoGraph – Ground Truth Preprocessing Script
=============================================
Reads all 30 JSON files from data/raw/ground_truth/
(BMW_SC001–010, MERC_SC001–010, TSLA_SC001–010)
and builds a flat, indexed structure for use in the scenarios endpoint.

Each source file contains:
  disruption_analysis: { ongoing_disruption, type, scope, involved: {countries, industries, companies} }
  kg_results:          { tier_1: [...], tier_2: [...], tier_3: [...] }

Outputs:
  data/processed/ground_truth_index.json

Run from project root or backend/:
    python backend/scripts/preprocess_ground_truth.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

GT_DIR   = os.path.join(_REPO_ROOT, "data", "raw", "ground_truth")
OUT_PATH = os.path.join(_REPO_ROOT, "data", "processed", "ground_truth_index.json")

# Map filename prefix to monitored company
PREFIX_TO_COMPANY = {
    "BMW":  "Bayerische Motoren Werke AG",
    "MERC": "Mercedes-Benz Group AG",
    "TSLA": "Tesla Inc",
}


def _flatten_tier(tier_entries: list) -> list[dict]:
    """
    tier entries can be either:
      - a list of company dicts  (single chain)
      - a list of such lists     (multiple chains)
    Normalise to flat list of unique company dicts.
    """
    seen = set()
    result = []
    for entry in tier_entries:
        if isinstance(entry, list):
            # Multiple chains: recurse one level
            for item in entry:
                if isinstance(item, dict) and "company" in item:
                    key = item["company"]
                    if key not in seen:
                        seen.add(key)
                        result.append(item)
        elif isinstance(entry, dict) and "company" in entry:
            key = entry["company"]
            if key not in seen:
                seen.add(key)
                result.append(entry)
    return result


def build_cache() -> dict:
    gt_dir = Path(GT_DIR)
    if not gt_dir.exists():
        sys.exit(f"Ground truth directory not found: {GT_DIR}\nRun data copy first.")

    json_files = sorted(gt_dir.glob("*.json"))
    # Exclude index.json from source (we're building our own)
    scenario_files = [f for f in json_files if f.stem != "index"]
    print(f"  Ground truth files found: {len(scenario_files)}")

    scenarios = []
    for fpath in scenario_files:
        stem = fpath.stem           # e.g. "TSLA_SC003"
        prefix = stem.split("_")[0] # e.g. "TSLA"

        with open(fpath) as f:
            raw = json.load(f)

        da = raw.get("disruption_analysis", {})
        kg = raw.get("kg_results", {})
        involved = da.get("involved", {})

        monitored = PREFIX_TO_COMPANY.get(prefix, prefix)

        # Flatten tiers
        tier1 = _flatten_tier(kg.get("tier_1", []))
        tier2 = _flatten_tier(kg.get("tier_2", []))
        tier3 = _flatten_tier(kg.get("tier_3", []))

        entry = {
            "scenario_id":          stem,
            "monitored_company":    monitored,
            "disruption_type":      da.get("type", ""),
            "ongoing":              da.get("ongoing_disruption", False),
            "scope":                da.get("scope", ""),
            "involved_countries":   involved.get("countries", []),
            "involved_industries":  involved.get("industries", []),
            "involved_companies":   involved.get("companies", []),
            "tier_1_affected":      tier1,
            "tier_2_affected":      tier2,
            "tier_3_affected":      tier3,
            "total_tier_1":         len(tier1),
            "total_tier_2":         len(tier2),
            "total_tier_3":         len(tier3),
            "source_file":          fpath.name,
        }
        scenarios.append(entry)
        print(f"    {stem}: T1={len(tier1)} T2={len(tier2)} T3={len(tier3)}")

    # Build lookup by scenario_id for O(1) access
    by_id = {s["scenario_id"]: s for s in scenarios}

    # Build lookup by monitored company
    by_company: dict[str, list] = {}
    for s in scenarios:
        co = s["monitored_company"]
        by_company.setdefault(co, []).append(s["scenario_id"])

    cache = {
        "version":          "1.0",
        "source":           "data/raw/ground_truth/",
        "total_scenarios":  len(scenarios),
        "monitored_companies": list(by_company.keys()),
        "scenarios":        scenarios,
        "by_id":            by_id,
        "by_company":       by_company,
    }
    return cache


def main():
    print("=" * 60)
    print("  AtmoGraph – Ground Truth Index Builder")
    print("=" * 60)

    cache = build_cache()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"\n  ✅ Written → {OUT_PATH}")
    print(f"  Total scenarios: {cache['total_scenarios']}")
    print(f"  Monitored companies: {', '.join(cache['monitored_companies'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()
