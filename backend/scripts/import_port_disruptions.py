"""
AtmoGraph – Port Disruption Import Script
Imports Port-disruption-database.xlsx into Neo4j as:
  - Port nodes
  - Country nodes (merged with existing)
  - DisruptionEvent nodes
  - PORT_IN  (Port → Country)
  - AFFECTED_BY (Port → DisruptionEvent)

Usage (from repo root):
    cd backend
    python scripts/import_port_disruptions.py
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import openpyxl
from neo4j import GraphDatabase
from app.config import settings

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
XLSX_PATH = os.path.join(REPO_ROOT, "data", "disruption_events", "Port-disruption-database.xlsx")


def get_driver():
    driver = GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    driver.verify_connectivity()
    return driver


def load_xlsx() -> list[dict]:
    """Load the XLSX and return a list of row dicts."""
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    if not rows:
        return []

    # First row = header
    headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(rows[0])]
    print(f"  Columns found: {headers}")

    data = []
    for row in rows[1:]:
        if all(v is None for v in row):
            continue   # skip empty rows
        data.append(dict(zip(headers, row)))
    return data


def infer_columns(data: list[dict]) -> dict:
    """
    Try to identify the right column names regardless of exact header text.
    Returns a mapping of semantic role → actual header name.
    """
    all_keys = list(data[0].keys()) if data else []
    lower_keys = {k.lower(): k for k in all_keys}

    def find(candidates):
        for c in candidates:
            for lk, orig in lower_keys.items():
                if c in lk:
                    return orig
        return None

    return {
        "event":    find(["event", "storm", "hurricane", "disruption"]),
        "country":  find(["country"]),
        "port":     find(["port"]),
        "year":     find(["year"]),
        "date":     find(["date"]),
        "severity": find(["severity"]),
        "tad":      find(["total", "tad", "affected day"]),
        "days_red": find(["reduction"]),
        "days_shut":find(["shutdown"]),
        "days_rec": find(["recovery"]),
    }


def main():
    print("=" * 60)
    print("  AtmoGraph — Port Disruption Import")
    print("=" * 60)
    if not os.path.exists(XLSX_PATH):
        print(f"  ❌ File not found: {XLSX_PATH}")
        sys.exit(1)

    t0 = time.time()
    data = load_xlsx()
    if not data:
        print("  ⚠️  No data rows found in XLSX.")
        sys.exit(0)

    print(f"  Rows loaded: {len(data)}")
    cols = infer_columns(data)
    print(f"  Column mapping: {cols}")
    print("-" * 60)

    # Build structured records
    ports_seen = set()
    countries_seen = set()
    events = []

    for i, row in enumerate(data):
        event_name = str(row.get(cols["event"], "") or "").strip()
        port_name  = str(row.get(cols["port"],  "") or "").strip()
        country    = str(row.get(cols["country"],"") or "").strip()
        year       = row.get(cols["year"])
        severity   = row.get(cols["severity"])
        tad        = row.get(cols["tad"])

        if not event_name or not port_name:
            continue

        ports_seen.add((port_name, country))
        if country:
            countries_seen.add(country)
        events.append({
            "event_id":   f"event_{i}",
            "event_name": event_name,
            "port_name":  port_name,
            "country":    country,
            "year":       int(year) if year else None,
            "severity":   int(severity) if severity is not None else None,
            "total_affected_days": float(tad) if tad is not None else None,
        })

    print(f"  Ports           : {len(ports_seen)}")
    print(f"  Countries (new) : {len(countries_seen)}")
    print(f"  Events          : {len(events)}")
    print("-" * 60)

    driver = get_driver()
    with driver.session(database="neo4j") as session:
        # Country nodes (merge with existing)
        if countries_seen:
            session.run(
                "UNWIND $rows AS row MERGE (:Country {name: row.name})",
                {"rows": [{"name": c} for c in countries_seen]},
            )
            print(f"  ✓ Country nodes merged")

        # Port nodes
        for port_name, country in ports_seen:
            session.run(
                """
                MERGE (p:Port {name: $name})
                ON CREATE SET p.country = $country, p.source_dataset = 'port_disruption'
                WITH p
                MATCH (co:Country {name: $country})
                MERGE (p)-[:PORT_IN]->(co)
                """,
                {"name": port_name, "country": country},
            )
        print(f"  ✓ {len(ports_seen)} Port nodes created/merged")

        # DisruptionEvent nodes + AFFECTED_BY
        for ev in events:
            session.run(
                """
                MERGE (e:DisruptionEvent {event_id: $event_id})
                ON CREATE SET
                    e.event_name         = $event_name,
                    e.year               = $year,
                    e.source_dataset     = 'port_disruption'
                WITH e
                MATCH (p:Port {name: $port_name})
                MERGE (p)-[r:AFFECTED_BY]->(e)
                ON CREATE SET
                    r.severity            = $severity,
                    r.total_affected_days = $tad
                """,
                {
                    "event_id":   ev["event_id"],
                    "event_name": ev["event_name"],
                    "year":       ev["year"],
                    "port_name":  ev["port_name"],
                    "severity":   ev["severity"],
                    "tad":        ev["total_affected_days"],
                },
            )
        print(f"  ✓ {len(events)} DisruptionEvent nodes + AFFECTED_BY relationships created")

    driver.close()
    elapsed = time.time() - t0
    print("-" * 60)
    print(f"  ✅ Port disruption import complete in {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
