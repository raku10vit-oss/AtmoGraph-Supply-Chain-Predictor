"""
AtmoGraph – Graph Verification Script
Counts all nodes and relationships in Neo4j and
checks them against expected minimums from the datasets.

Usage (from repo root):
    cd backend
    python scripts/verify_graph.py

Exits with code 1 if any count is below the minimum threshold.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from neo4j import GraphDatabase
from app.config import settings

# Expected minimum counts after full import
EXPECTED = {
    # Node labels
    "Company":         6000,
    "Country":           90,
    "Industry":          20,
    "Port":               5,
    "AnonNode":        7000,
    # Relationship types
    "SUPPLIES_TO":    16000,
    "LOCATED_IN":      5000,
    "BELONGS_TO":      5000,
    "CONNECTS_TO":    43000,
}


def get_driver():
    return GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )


def run_checks(driver):
    failures = []

    with driver.session(database="neo4j") as session:
        # Node label counts
        node_rows = session.run(
            "MATCH (n) WITH labels(n)[0] AS lbl, count(n) AS cnt RETURN lbl, cnt"
        ).data()
        label_counts = {r["lbl"]: r["cnt"] for r in node_rows if r.get("lbl")}

        # Relationship type counts
        rel_rows = session.run(
            "MATCH ()-[r]->() WITH type(r) AS t, count(r) AS cnt RETURN t, cnt"
        ).data()
        rel_counts = {r["t"]: r["cnt"] for r in rel_rows if r.get("t")}

    all_counts = {**label_counts, **rel_counts}

    print("=" * 60)
    print("  AtmoGraph — Graph Verification")
    print("=" * 60)
    print(f"  {'Item':<30} {'Count':>10}  {'Min':>8}  {'Status'}")
    print(f"  {'-'*30} {'-'*10}  {'-'*8}  {'-'*6}")

    for key, min_val in EXPECTED.items():
        actual = all_counts.get(key, 0)
        status = "✅ OK" if actual >= min_val else "❌ LOW"
        if actual < min_val:
            failures.append((key, actual, min_val))
        print(f"  {key:<30} {actual:>10,}  {min_val:>8,}  {status}")

    # Also print any extra counts not in EXPECTED
    extra = {k: v for k, v in all_counts.items() if k not in EXPECTED}
    if extra:
        print(f"\n  Additional counts in database:")
        for k, v in sorted(extra.items()):
            print(f"  {k:<30} {v:>10,}")

    print("=" * 60)
    if failures:
        print(f"\n  ❌ {len(failures)} check(s) FAILED:")
        for key, actual, minimum in failures:
            print(f"     {key}: got {actual:,}, expected ≥ {minimum:,}")
        print("\n  → Run the import scripts first:")
        print("    python scripts/import_supply_chain.py")
        print("    python scripts/import_anonnet.py")
        print("    python scripts/import_port_disruptions.py")
        return False
    else:
        print("\n  ✅ All checks passed — graph is ready!")
        return True


def main():
    try:
        driver = get_driver()
        driver.verify_connectivity()
    except Exception as exc:
        print(f"  ❌ Cannot connect to Neo4j: {exc}")
        sys.exit(1)

    ok = run_checks(driver)
    driver.close()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
