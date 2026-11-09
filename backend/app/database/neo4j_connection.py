"""
AtmoGraph – Neo4j Connection Manager
Manages a single driver instance shared across all requests.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, Driver
from app.config import settings

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Singleton wrapper around the Neo4j Python driver."""

    def __init__(self) -> None:
        self._driver: Optional[Driver] = None

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Open the driver and verify connectivity."""
        try:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            self._driver.verify_connectivity()
            logger.info("✅ Neo4j connected → %s", settings.neo4j_uri)
        except Exception as exc:
            logger.error("❌ Neo4j connection failed: %s", exc)
            raise

    def close(self) -> None:
        """Close the driver cleanly."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j driver closed")

    def is_connected(self) -> bool:
        if not self._driver:
            return False
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            return False

    # ── Query helper ───────────────────────────────────────────────────────────

    def query(
        self,
        cypher: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: str = "neo4j",
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return a list of dicts.
        Each dict corresponds to one result record.
        """
        if not self._driver:
            raise RuntimeError(
                "Neo4j driver is not connected. "
                "Start Neo4j and ensure .env credentials are correct."
            )
        with self._driver.session(database=database) as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]


# Single global instance imported throughout the application
neo4j_conn = Neo4jConnection()
