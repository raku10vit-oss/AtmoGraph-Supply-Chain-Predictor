"""
AtmoGraph – Port Disruption Preprocessing Script
=================================================
Reads Port-disruption-database.xlsx and computes per-country and
per-port historical risk statistics, then writes the results to
backend/app/data/port_risk_cache.json.

Run once (or whenever the source XLSX changes):
    cd backend
    python scripts/preprocess_port_disruptions.py

The JSON is loaded at server startup by prediction_service.py so that
no XLSX parsing happens on every API request.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from typing import Any, Dict

# ── Path bootstrap (allow running from project root or backend/) ──
REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
XLSX_PATH = os.path.join(
    REPO_ROOT, "data", "disruption_events", "Port-disruption-database.xlsx"
)
OUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "app", "data", "port_risk_cache.json"
)

try:
    import openpyxl
    import pandas as pd
except ImportError as exc:
    sys.exit(f"Missing dependency: {exc}. Run: pip install openpyxl pandas")


# ── Helper ────────────────────────────────────────────────────────

def _safe_float(v) -> float:
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _safe_int(v) -> int:
    try:
        return int(v) if v is not None else 0
    except (TypeError, ValueError):
        return 0


# ── Main ──────────────────────────────────────────────────────────

def build_cache() -> Dict[str, Any]:
    print(f"Loading: {XLSX_PATH}")
    if not os.path.exists(XLSX_PATH):
        sys.exit(f"File not found: {XLSX_PATH}")

    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    if not rows:
        sys.exit("XLSX appears to be empty.")

    headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(rows[0])]
    print(f"  Headers: {headers}")
    print(f"  Data rows: {len(rows) - 1}")

    # ── Normalise column names ────────────────────────────────────
    h_lower = {h.lower(): h for h in headers}

    def col(candidates: list[str]) -> str | None:
        for c in candidates:
            for lk, orig in h_lower.items():
                if c in lk:
                    return orig
        return None

    COL_EVENT    = col(["event", "storm", "hurricane"])
    COL_PORT     = col(["port_name", "port"])
    COL_COUNTRY  = col(["country"])
    COL_YEAR     = col(["year"])
    COL_SEVERITY = col(["severity"])
    COL_TAD      = col(["total", "tad", "affected"])
    COL_REDUCTION = col(["reduction"])
    COL_SHUTDOWN  = col(["shutdown"])
    COL_RECOVERY  = col(["recovery"])

    print(f"  Mapped columns: event={COL_EVENT}, port={COL_PORT}, "
          f"country={COL_COUNTRY}, severity={COL_SEVERITY}, tad={COL_TAD}")

    records = []
    for row in rows[1:]:
        d = dict(zip(headers, row))
        event    = str(d.get(COL_EVENT, "") or "").strip()
        port     = str(d.get(COL_PORT,  "") or "").strip()
        country  = str(d.get(COL_COUNTRY, "") or "").strip()
        year     = _safe_int(d.get(COL_YEAR))
        severity = _safe_int(d.get(COL_SEVERITY))
        tad      = _safe_float(d.get(COL_TAD))
        reduction = _safe_float(d.get(COL_REDUCTION))
        shutdown  = _safe_float(d.get(COL_SHUTDOWN))
        recovery  = _safe_float(d.get(COL_RECOVERY))

        if not event and not port:
            continue
        records.append({
            "event": event, "port": port, "country": country,
            "year": year, "severity": severity,
            "total_affected_days": tad,
            "reduction_days": reduction,
            "shutdown_days": shutdown,
            "recovery_days": recovery,
        })

    print(f"  Valid records: {len(records)}")

    # ── Per-country stats ─────────────────────────────────────────
    country_data: Dict[str, dict] = defaultdict(lambda: {
        "event_count": 0, "total_severity": 0, "total_days": 0,
        "severity_counts": defaultdict(int), "events": [],
    })

    for r in records:
        c = r["country"]
        if not c:
            continue
        cd = country_data[c]
        cd["event_count"] += 1
        cd["total_severity"] += r["severity"]
        cd["total_days"] += r["total_affected_days"]
        cd["severity_counts"][str(r["severity"])] += 1
        if r["event"] not in cd["events"]:
            cd["events"].append(r["event"])

    # Compute mean severity and normalised risk score (0–1)
    all_mean_severities = []
    for c, cd in country_data.items():
        n = cd["event_count"]
        cd["mean_severity"] = round(cd["total_severity"] / n, 3) if n else 0.0
        cd["mean_days"] = round(cd["total_days"] / n, 3) if n else 0.0
        all_mean_severities.append(cd["mean_severity"])

    # Min-max normalise severity → risk_score
    min_sev = min(all_mean_severities) if all_mean_severities else 0.0
    max_sev = max(all_mean_severities) if all_mean_severities else 1.0
    sev_range = max_sev - min_sev or 1.0

    for c, cd in country_data.items():
        cd["risk_score"] = round(
            (cd["mean_severity"] - min_sev) / sev_range, 4
        )
        # Convert defaultdict to plain dict
        cd["severity_counts"] = dict(cd["severity_counts"])

    # ── Per-port stats ────────────────────────────────────────────
    port_data: Dict[str, dict] = defaultdict(lambda: {
        "event_count": 0, "total_severity": 0, "total_days": 0,
        "country": "", "events": [],
    })

    for r in records:
        p = r["port"]
        if not p:
            continue
        pd_entry = port_data[p]
        pd_entry["event_count"] += 1
        pd_entry["total_severity"] += r["severity"]
        pd_entry["total_days"] += r["total_affected_days"]
        if not pd_entry["country"]:
            pd_entry["country"] = r["country"]
        if r["event"] not in pd_entry["events"]:
            pd_entry["events"].append(r["event"])

    for p, pd_entry in port_data.items():
        n = pd_entry["event_count"]
        pd_entry["mean_severity"] = round(pd_entry["total_severity"] / n, 3) if n else 0.0
        pd_entry["mean_days"] = round(pd_entry["total_days"] / n, 3) if n else 0.0

    # ── Top disruption events ─────────────────────────────────────
    # Aggregate by event name across all ports
    event_data: Dict[str, dict] = defaultdict(lambda: {
        "ports_affected": [], "countries_affected": [],
        "years": [], "total_severity": 0, "total_days": 0, "count": 0,
    })

    for r in records:
        ev = r["event"]
        if not ev:
            continue
        ed = event_data[ev]
        ed["count"] += 1
        ed["total_severity"] += r["severity"]
        ed["total_days"] += r["total_affected_days"]
        if r["port"] and r["port"] not in ed["ports_affected"]:
            ed["ports_affected"].append(r["port"])
        if r["country"] and r["country"] not in ed["countries_affected"]:
            ed["countries_affected"].append(r["country"])
        if r["year"] and r["year"] not in ed["years"]:
            ed["years"].append(r["year"])

    events_list = []
    for ev, ed in event_data.items():
        n = ed["count"]
        mean_sev = ed["total_severity"] / n if n else 0.0
        risk_score = round((mean_sev - min_sev) / sev_range, 4)
        risk_level = "High" if risk_score >= 0.65 else "Medium" if risk_score >= 0.35 else "Low"
        events_list.append({
            "event_name": ev,
            "ports_affected": ed["ports_affected"],
            "countries_affected": ed["countries_affected"],
            "years": sorted(ed["years"]),
            "ports_count": len(ed["ports_affected"]),
            "mean_severity": round(mean_sev, 3),
            "total_days": round(ed["total_days"], 1),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "record_count": n,
        })

    # Sort by risk_score descending
    events_list.sort(key=lambda x: x["risk_score"], reverse=True)

    # ── Industry vulnerability from KG ────────────────────────────
    # Map countries that had disruptions → extract which industries
    # have suppliers there (from supplychainKG_clean.csv)
    kg_path = os.path.join(REPO_ROOT, "data", "supply_network", "supplychainKG_clean.csv")
    industry_risk: Dict[str, dict] = {}

    if os.path.exists(kg_path):
        kg = pd.read_csv(kg_path)
        affected_countries = set(country_data.keys())

        # Normalize country names to handle minor mismatches
        # Port DB uses "U.S.A." while KG uses "United States"
        COUNTRY_MAP = {
            "U.S.A.": "United States",
            "U.S.A": "United States",
            "USA": "United States",
        }
        normalized_affected = set()
        for c in affected_countries:
            normalized_affected.add(COUNTRY_MAP.get(c, c))

        # Count how many suppliers per industry are in disrupted countries
        supplier_in_disrupted = kg[
            kg["Supplier Country"].isin(normalized_affected)
        ]["Supplier Industry"].value_counts().to_dict()

        total_suppliers = kg["Supplier Industry"].value_counts().to_dict()

        for industry, count_in_disrupted in supplier_in_disrupted.items():
            total = total_suppliers.get(industry, 1)
            exposure_ratio = count_in_disrupted / total
            industry_risk[industry] = {
                "suppliers_in_disrupted_countries": int(count_in_disrupted),
                "total_suppliers": int(total),
                "exposure_ratio": round(exposure_ratio, 4),
                "risk_score": round(min(exposure_ratio * 2, 1.0), 4),  # cap at 1.0
            }

    # Sort by risk_score
    industry_risk_sorted = dict(
        sorted(industry_risk.items(), key=lambda x: x[1]["risk_score"], reverse=True)
    )

    # ── Build final cache ─────────────────────────────────────────
    cache = {
        "version": "2.0",
        "source": "Port-disruption-database.xlsx",
        "total_records": len(records),
        "country_risk": {c: dict(v) for c, v in country_data.items()},
        "port_risk": {p: dict(v) for p, v in port_data.items()},
        "disruption_events": events_list,
        "industry_risk": industry_risk_sorted,
        "meta": {
            "countries_with_data": len(country_data),
            "ports_with_data": len(port_data),
            "unique_events": len(event_data),
            "severity_range": {"min": min_sev, "max": max_sev},
        },
    }

    return cache


def main():
    print("=" * 60)
    print("  AtmoGraph – Port Risk Cache Builder")
    print("=" * 60)

    cache = build_cache()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(cache, f, indent=2, default=str)

    print(f"\n  ✅ Cache written → {OUT_PATH}")
    print(f"  Countries: {cache['meta']['countries_with_data']}")
    print(f"  Ports:     {cache['meta']['ports_with_data']}")
    print(f"  Events:    {cache['meta']['unique_events']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
