"""
AtmoGraph – SynDelay Preprocessing Script
==========================================
Reads data/raw/syndelay_v1.csv (155,489 rows, 54 MB) and computes
per-country and per-market shipping delay rates from the binary label column.

label values: 0 = unknown/other, 1 = on-time, 2 = delayed

Outputs:
  data/processed/syndelay_country_risk.json

Run from project root or backend/:
    python backend/scripts/preprocess_syndelay.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

# ── Path setup ────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

RAW_PATH = os.path.join(_REPO_ROOT, "data", "raw", "syndelay_v1.csv")
OUT_PATH  = os.path.join(_REPO_ROOT, "data", "processed", "syndelay_country_risk.json")

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency: pandas. Run: pip install pandas")


def _normalise_country(c: str) -> str:
    """Normalise a few known variants so they match the KG."""
    MAP = {
        "United States": "United States",
        "USA":           "United States",
        "US":            "United States",
    }
    return MAP.get(str(c).strip(), str(c).strip())


def build_cache() -> dict:
    print(f"Loading: {RAW_PATH}")
    if not os.path.exists(RAW_PATH):
        sys.exit(
            f"File not found: {RAW_PATH}\n"
            "Copy syndelay_v1.csv from ~/Desktop/syndelay-main/data/ "
            "to data/raw/ first:\n"
            "  cp ~/Desktop/syndelay-main/data/syndelay_v1.csv data/raw/"
        )

    df = pd.read_csv(RAW_PATH)
    print(f"  Rows: {len(df):,}  |  Columns: {len(df.columns)}")

    # label: 1 = on-time, 2 = delayed (0 and other values treated as unknown)
    df = df[df["label"].isin([1, 2])].copy()
    df["delayed"] = (df["label"] == 2).astype(int)
    print(f"  Rows with valid label (1 or 2): {len(df):,}")

    # ── Per order_country delay rate ──────────────────────────────
    country_col = "order_country"
    country_stats = (
        df.groupby(country_col)["delayed"]
        .agg(["count", "sum"])
        .rename(columns={"count": "total_orders", "sum": "delayed_orders"})
        .reset_index()
    )
    country_stats["delay_rate"] = (
        country_stats["delayed_orders"] / country_stats["total_orders"]
    ).round(4)

    # Normalise to [0, 1] risk score
    min_r = float(country_stats["delay_rate"].min())
    max_r = float(country_stats["delay_rate"].max())
    rng = max_r - min_r or 1.0
    country_stats["risk_score"] = (
        (country_stats["delay_rate"] - min_r) / rng
    ).round(4)

    country_risk = {}
    for _, row in country_stats.iterrows():
        c = _normalise_country(row[country_col])
        country_risk[c] = {
            "total_orders":   int(row["total_orders"]),
            "delayed_orders": int(row["delayed_orders"]),
            "delay_rate":     float(row["delay_rate"]),
            "risk_score":     float(row["risk_score"]),
        }

    # ── Per shipping_mode delay rate ──────────────────────────────
    mode_stats = (
        df.groupby("shipping_mode")["delayed"]
        .agg(["count", "sum"])
        .rename(columns={"count": "total_orders", "sum": "delayed_orders"})
        .reset_index()
    )
    mode_stats["delay_rate"] = (
        mode_stats["delayed_orders"] / mode_stats["total_orders"]
    ).round(4)
    min_m = float(mode_stats["delay_rate"].min())
    max_m = float(mode_stats["delay_rate"].max())
    rng_m = max_m - min_m or 1.0
    mode_stats["risk_score"] = (
        (mode_stats["delay_rate"] - min_m) / rng_m
    ).round(4)

    shipping_mode_risk = {
        str(row["shipping_mode"]): {
            "total_orders":   int(row["total_orders"]),
            "delayed_orders": int(row["delayed_orders"]),
            "delay_rate":     float(row["delay_rate"]),
            "risk_score":     float(row["risk_score"]),
        }
        for _, row in mode_stats.iterrows()
    }

    # ── Per market delay rate ─────────────────────────────────────
    market_stats = (
        df.groupby("market")["delayed"]
        .agg(["count", "sum"])
        .rename(columns={"count": "total_orders", "sum": "delayed_orders"})
        .reset_index()
    )
    market_stats["delay_rate"] = (
        market_stats["delayed_orders"] / market_stats["total_orders"]
    ).round(4)

    market_risk = {
        str(row["market"]): {
            "total_orders":   int(row["total_orders"]),
            "delayed_orders": int(row["delayed_orders"]),
            "delay_rate":     float(row["delay_rate"]),
        }
        for _, row in market_stats.iterrows()
    }

    # ── Overall stats ─────────────────────────────────────────────
    total = len(df)
    total_delayed = int(df["delayed"].sum())
    overall_rate = round(total_delayed / total, 4) if total else 0.0

    cache = {
        "version":           "1.0",
        "source":            "syndelay_v1.csv",
        "source_rows":       total,
        "overall_delay_rate": overall_rate,
        "countries_with_data": len(country_risk),
        "country_risk":      country_risk,
        "shipping_mode_risk": shipping_mode_risk,
        "market_risk":       market_risk,
        "meta": {
            "label_definition": "1=on-time, 2=delayed",
            "risk_score_note":   "Min-max normalised delay rate per country (0=lowest delay, 1=highest delay)",
        },
    }
    return cache


def main():
    print("=" * 60)
    print("  AtmoGraph – SynDelay Country Risk Builder")
    print("=" * 60)

    cache = build_cache()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"\n  ✅ Written → {OUT_PATH}")
    print(f"  Overall delay rate:  {cache['overall_delay_rate']:.1%}")
    print(f"  Countries with data: {cache['countries_with_data']}")
    print(f"  Shipping modes:")
    for mode, v in cache["shipping_mode_risk"].items():
        print(f"    {mode:20s} delay={v['delay_rate']:.1%}  score={v['risk_score']:.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
