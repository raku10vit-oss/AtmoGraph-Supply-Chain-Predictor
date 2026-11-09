"""
AtmoGraph – Supply Chain KG Import Script
Imports supplychainKG_clean.csv into Neo4j as:
  - Company nodes (supplier + customer)
  - Country nodes
  - Industry nodes
  - SUPPLIES_TO relationships
  - LOCATED_IN relationships
  - BELONGS_TO relationships

Usage (from repo root):
    cd backend
    python scripts/import_supply_chain.py

The script uses MERGE so it is safe to re-run — it will not create duplicates.
Batch size is 500 rows per transaction for memory efficiency.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import pandas as pd
from neo4j import GraphDatabase
from app.config import settings

# ── Path to dataset ────────────────────────────────────────────────────────────
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_PATH = os.path.join(REPO_ROOT, "data", "supply_network", "supplychainKG_clean.csv")

BATCH_SIZE = 500


def get_driver():
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    driver.verify_connectivity()
    return driver


def run_batch(session, cypher: str, rows: list[dict]) -> int:
    result = session.run(cypher, {"rows": rows})
    summary = result.consume()
    return summary.counters.nodes_created + summary.counters.relationships_created


def print_progress(step: str, done: int, total: int, created: int):
    pct = int(done / total * 100)
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    print(f"\r  {step:<30} [{bar}] {pct:3d}%  ({created:,} created)", end="", flush=True)


def import_countries(session, countries: list[str]) -> int:
    cypher = """
    UNWIND $rows AS row
    MERGE (c:Country {name: row.name})
    """
    rows = [{"name": c} for c in countries if c]
    result = session.run(cypher, {"rows": rows})
    return result.consume().counters.nodes_created


def import_industries(session, industries: list[str]) -> int:
    cypher = """
    UNWIND $rows AS row
    MERGE (i:Industry {name: row.name})
    """
    rows = [{"name": i} for i in industries if i]
    result = session.run(cypher, {"rows": rows})
    return result.consume().counters.nodes_created


def import_companies(session, companies: list[dict]) -> int:
    """
    companies: list of dicts with keys name, country, industry, role
    Role = Supplier | Customer | Both
    """
    cypher = """
    UNWIND $rows AS row
    MERGE (c:Company {name: row.name})
    ON CREATE SET
        c.country  = row.country,
        c.industry = row.industry,
        c.type     = row.role,
        c.source_dataset = 'supplychainKG'
    ON MATCH SET
        c.type = CASE
            WHEN c.type <> row.role AND row.role <> c.type
            THEN 'Both'
            ELSE c.type
        END
    """
    total_created = 0
    for i in range(0, len(companies), BATCH_SIZE):
        batch = companies[i : i + BATCH_SIZE]
        result = session.run(cypher, {"rows": batch})
        total_created += result.consume().counters.nodes_created
        print_progress("Importing companies", min(i + BATCH_SIZE, len(companies)),
                       len(companies), total_created)
    print()
    return total_created


def import_supplies_to(session, df: pd.DataFrame) -> int:
    cypher = """
    UNWIND $rows AS row
    MATCH (s:Company {name: row.supplier})
    MATCH (c:Company {name: row.customer})
    MERGE (s)-[r:SUPPLIES_TO]->(c)
    ON CREATE SET r.source_dataset = 'supplychainKG'
    """
    rows = df[["Supplier", "Customer"]].rename(
        columns={"Supplier": "supplier", "Customer": "customer"}
    ).to_dict("records")

    total_created = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        result = session.run(cypher, {"rows": batch})
        total_created += result.consume().counters.relationships_created
        print_progress("Importing SUPPLIES_TO", min(i + BATCH_SIZE, len(rows)),
                       len(rows), total_created)
    print()
    return total_created


def import_located_in(session, df: pd.DataFrame) -> int:
    # For each company, link to its country
    cypher = """
    UNWIND $rows AS row
    MATCH (c:Company {name: row.company})
    MATCH (co:Country {name: row.country})
    MERGE (c)-[:LOCATED_IN]->(co)
    """
    rows = (
        pd.concat([
            df[["Supplier", "Supplier Country"]].rename(
                columns={"Supplier": "company", "Supplier Country": "country"}),
            df[["Customer", "Customer Country"]].rename(
                columns={"Customer": "company", "Customer Country": "country"}),
        ])
        .drop_duplicates()
        .dropna()
        .query("company != '' and country != ''")
        .to_dict("records")
    )

    total_created = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        result = session.run(cypher, {"rows": batch})
        total_created += result.consume().counters.relationships_created
        print_progress("Importing LOCATED_IN", min(i + BATCH_SIZE, len(rows)),
                       len(rows), total_created)
    print()
    return total_created


def import_belongs_to(session, df: pd.DataFrame) -> int:
    cypher = """
    UNWIND $rows AS row
    MATCH (c:Company {name: row.company})
    MATCH (i:Industry {name: row.industry})
    MERGE (c)-[:BELONGS_TO]->(i)
    """
    rows = (
        pd.concat([
            df[["Supplier", "Supplier Industry"]].rename(
                columns={"Supplier": "company", "Supplier Industry": "industry"}),
            df[["Customer", "Customer Industry"]].rename(
                columns={"Customer": "company", "Customer Industry": "industry"}),
        ])
        .drop_duplicates()
        .dropna()
        .query("company != '' and industry != ''")
        .to_dict("records")
    )

    total_created = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        result = session.run(cypher, {"rows": batch})
        total_created += result.consume().counters.relationships_created
        print_progress("Importing BELONGS_TO", min(i + BATCH_SIZE, len(rows)),
                       len(rows), total_created)
    print()
    return total_created


def main():
    print("=" * 60)
    print("  AtmoGraph — Supply Chain KG Import")
    print("=" * 60)
    print(f"  CSV: {CSV_PATH}")

    if not os.path.exists(CSV_PATH):
        print(f"  ❌ CSV not found: {CSV_PATH}")
        sys.exit(1)

    t0 = time.time()
    df = pd.read_csv(CSV_PATH)
    # Strip whitespace from string columns
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    df = df.dropna(subset=["Supplier", "Customer"])
    df = df[df["Supplier"] != ""].copy()
    print(f"  Loaded {len(df):,} rows")

    # Identify company roles
    suppliers = set(df["Supplier"].unique())
    customers = set(df["Customer"].unique())
    both = suppliers & customers
    supplier_only = suppliers - both
    customer_only = customers - both

    companies = []
    for name in both:
        row_s = df[df["Supplier"] == name].iloc[0]
        companies.append({"name": name, "country": row_s.get("Supplier Country", ""),
                           "industry": row_s.get("Supplier Industry", ""), "role": "Both"})
    for name in supplier_only:
        row_s = df[df["Supplier"] == name].iloc[0]
        companies.append({"name": name, "country": row_s.get("Supplier Country", ""),
                           "industry": row_s.get("Supplier Industry", ""), "role": "Supplier"})
    for name in customer_only:
        row_c = df[df["Customer"] == name].iloc[0]
        companies.append({"name": name, "country": row_c.get("Customer Country", ""),
                           "industry": row_c.get("Customer Industry", ""), "role": "Customer"})

    all_countries = list(
        set(df["Supplier Country"].dropna().unique()) |
        set(df["Customer Country"].dropna().unique())
    )
    all_industries = list(
        set(df["Supplier Industry"].dropna().unique()) |
        set(df["Customer Industry"].dropna().unique())
    )
    all_countries = [c for c in all_countries if c]
    all_industries = [i for i in all_industries if i]

    print(f"  Companies  : {len(companies):,} ({len(supplier_only):,} supplier-only, "
          f"{len(customer_only):,} customer-only, {len(both):,} both)")
    print(f"  Countries  : {len(all_countries)}")
    print(f"  Industries : {len(all_industries)}")
    print("-" * 60)

    driver = get_driver()
    with driver.session(database="neo4j") as session:
        print("  Step 1/6 — Countries …")
        n = import_countries(session, all_countries)
        print(f"  ✓ {n:,} country nodes created")

        print("  Step 2/6 — Industries …")
        n = import_industries(session, all_industries)
        print(f"  ✓ {n:,} industry nodes created")

        print("  Step 3/6 — Companies …")
        n = import_companies(session, companies)
        print(f"  ✓ {n:,} company nodes created")

        print("  Step 4/6 — SUPPLIES_TO relationships …")
        n = import_supplies_to(session, df)
        print(f"  ✓ {n:,} SUPPLIES_TO relationships created")

        print("  Step 5/6 — LOCATED_IN relationships …")
        n = import_located_in(session, df)
        print(f"  ✓ {n:,} LOCATED_IN relationships created")

        print("  Step 6/6 — BELONGS_TO relationships …")
        n = import_belongs_to(session, df)
        print(f"  ✓ {n:,} BELONGS_TO relationships created")

    driver.close()
    elapsed = time.time() - t0
    print("-" * 60)
    print(f"  ✅ Import complete in {elapsed:.1f}s")
    print("  Run  python scripts/verify_graph.py  to check counts.")
    print("=" * 60)


if __name__ == "__main__":
    main()
