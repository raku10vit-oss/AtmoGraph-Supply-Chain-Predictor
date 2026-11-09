"""
AtmoGraph – Neo4j Connectivity Test
Run this FIRST to confirm your database credentials work before importing data.

Usage (from repo root):
    cd backend
    python scripts/test_neo4j.py
"""
import sys
import os

# Allow importing from backend/app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.config import settings
from neo4j import GraphDatabase


def test_connection():
    print("=" * 55)
    print("  AtmoGraph — Neo4j Connection Test")
    print("=" * 55)
    print(f"  URI      : {settings.neo4j_uri}")
    print(f"  User     : {settings.neo4j_user}")
    print(f"  Password : {'*' * len(settings.neo4j_password)}")
    print("-" * 55)

    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        driver.verify_connectivity()

        with driver.session(database="neo4j") as session:
            result = session.run("RETURN 1 AS ping, 'AtmoGraph' AS app")
            record = result.single()
            print(f"  ✅ Connected!  ping={record['ping']}  app={record['app']}")

            # Neo4j version
            version_result = session.run("CALL dbms.components() YIELD name, versions")
            for r in version_result:
                print(f"  📦 {r['name']} {r['versions']}")

        driver.close()
        print("-" * 55)
        print("  ✅ All checks passed. Neo4j is ready.")
        print("=" * 55)
        return True

    except Exception as exc:
        print(f"\n  ❌ Connection FAILED: {exc}")
        print("\n  Troubleshooting tips:")
        print("  1. Is Neo4j Desktop / Aura running?")
        print("  2. Check your .env file: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")
        print("  3. For Aura, use  neo4j+s://  not  bolt://")
        print("=" * 55)
        return False


if __name__ == "__main__":
    ok = test_connection()
    sys.exit(0 if ok else 1)
