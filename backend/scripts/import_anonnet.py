"""
AtmoGraph – AnonNet Import Script
Imports nodes_anon.csv + edges_anon.csv into Neo4j as:
  - AnonNode nodes (node_id, location, products)
  - CONNECTS_TO relationships

Usage (from repo root):
    cd backend
    python scripts/import_anonnet.py

Safe to re-run (uses MERGE). Batch size 1000 for performance.
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

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
NODES_CSV = os.path.join(REPO_ROOT, "data", "supply_network", "nodes_anon.csv")
EDGES_CSV = os.path.join(REPO_ROOT, "data", "supply_network", "edges_anon.csv")
BATCH_SIZE = 1000


def get_driver():
    driver = GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    driver.verify_connectivity()
    return driver


def print_progress(label: str, done: int, total: int, created: int):
    pct = int(done / total * 100)
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    print(f"\r  {label:<28} [{bar}] {pct:3d}%  ({created:,})", end="", flush=True)


def import_anon_nodes(session, df: pd.DataFrame) -> int:
    cypher = """
    UNWIND $rows AS row
    MERGE (n:AnonNode {node_id: row.node_id})
    ON CREATE SET
        n.location       = row.location,
        n.products       = row.products,
        n.source_dataset = 'anonnet'
    """
    rows = df.rename(columns={"id": "node_id"}).to_dict("records")
    total_created = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        result = session.run(cypher, {"rows": batch})
        total_created += result.consume().counters.nodes_created
        print_progress("Importing AnonNode nodes", min(i + BATCH_SIZE, len(rows)),
                       len(rows), total_created)
    print()
    return total_created


def import_connects_to(session, df: pd.DataFrame) -> int:
    cypher = """
    UNWIND $rows AS row
    MATCH (s:AnonNode {node_id: row.source})
    MATCH (t:AnonNode {node_id: row.target})
    MERGE (s)-[r:CONNECTS_TO]->(t)
    ON CREATE SET r.source_dataset = 'anonnet'
    """
    rows = df.to_dict("records")
    total_created = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        result = session.run(cypher, {"rows": batch})
        total_created += result.consume().counters.relationships_created
        print_progress("Importing CONNECTS_TO", min(i + BATCH_SIZE, len(rows)),
                       len(rows), total_created)
    print()
    return total_created


def main():
    print("=" * 60)
    print("  AtmoGraph — AnonNet Import")
    print("=" * 60)
    for path in [NODES_CSV, EDGES_CSV]:
        if not os.path.exists(path):
            print(f"  ❌ File not found: {path}")
            sys.exit(1)

    t0 = time.time()
    nodes_df = pd.read_csv(NODES_CSV)
    edges_df = pd.read_csv(EDGES_CSV)
    nodes_df = nodes_df.fillna("")
    print(f"  Nodes: {len(nodes_df):,} | Edges: {len(edges_df):,}")
    print("-" * 60)

    driver = get_driver()
    with driver.session(database="neo4j") as session:
        print("  Step 1/2 — AnonNode nodes …")
        n = import_anon_nodes(session, nodes_df)
        print(f"  ✓ {n:,} AnonNode nodes created")

        print("  Step 2/2 — CONNECTS_TO relationships …")
        n = import_connects_to(session, edges_df)
        print(f"  ✓ {n:,} CONNECTS_TO relationships created")

    driver.close()
    elapsed = time.time() - t0
    print("-" * 60)
    print(f"  ✅ AnonNet import complete in {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
