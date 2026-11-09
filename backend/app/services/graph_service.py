"""
AtmoGraph – Graph Service
All Cypher query logic lives here. Routes call these functions.
Uses id(n) (integer) as the stable node identifier exposed in the API.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.database.neo4j_connection import neo4j_conn
from app.models.schemas import (
    GraphModel,
    NodeModel,
    RelationshipModel,
    SearchResultModel,
    StatisticsModel,
)

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_node(record: Dict[str, Any], prefix: str = "") -> NodeModel:
    """Build a NodeModel from a flat query result dict."""
    p = prefix
    return NodeModel(
        id=record[f"{p}id"],
        label=record.get(f"{p}label") or "Unknown",
        properties=record.get(f"{p}props") or {},
    )


def _make_rel(record: Dict[str, Any]) -> Optional[RelationshipModel]:
    if not record.get("rel_id"):
        return None
    return RelationshipModel(
        id=record["rel_id"],
        source_id=record["src_id"],
        target_id=record["tgt_id"],
        type=record.get("rel_type") or "UNKNOWN",
        properties={},
    )


def _build_graph(records: List[Dict[str, Any]]) -> GraphModel:
    """
    Convert raw query records into a GraphModel.
    Records must have keys: src_id, src_label, src_props,
                             tgt_id, tgt_label, tgt_props (optional),
                             rel_id (optional), rel_type (optional).
    """
    nodes: Dict[int, NodeModel] = {}
    relationships: List[RelationshipModel] = []

    for rec in records:
        # source node
        sid = rec.get("src_id")
        if sid is not None and sid not in nodes:
            nodes[sid] = NodeModel(
                id=sid,
                label=rec.get("src_label") or "Unknown",
                properties=rec.get("src_props") or {},
            )
        # target node (may be None for isolated nodes)
        tid = rec.get("tgt_id")
        if tid is not None and tid not in nodes:
            nodes[tid] = NodeModel(
                id=tid,
                label=rec.get("tgt_label") or "Unknown",
                properties=rec.get("tgt_props") or {},
            )
        # relationship
        rel = _make_rel(rec)
        if rel:
            relationships.append(rel)

    node_list = list(nodes.values())
    return GraphModel(
        nodes=node_list,
        relationships=relationships,
        total_nodes=len(node_list),
        total_relationships=len(relationships),
    )


# ── Public service functions ───────────────────────────────────────────────────

def get_statistics() -> StatisticsModel:
    """Return counts for every node label and relationship type."""
    # Node label counts
    label_q = """
    MATCH (n)
    WITH labels(n)[0] AS lbl, count(n) AS cnt
    RETURN lbl, cnt
    ORDER BY cnt DESC
    """
    # Relationship type counts
    rel_q = """
    MATCH ()-[r]->()
    WITH type(r) AS rtype, count(r) AS cnt
    RETURN rtype, cnt
    ORDER BY cnt DESC
    """
    label_rows = neo4j_conn.query(label_q)
    rel_rows = neo4j_conn.query(rel_q)

    label_counts: Dict[str, int] = {
        r["lbl"]: r["cnt"] for r in label_rows if r.get("lbl")
    }
    rel_counts: Dict[str, int] = {
        r["rtype"]: r["cnt"] for r in rel_rows if r.get("rtype")
    }
    total_nodes = sum(label_counts.values())
    total_rels = sum(rel_counts.values())

    return StatisticsModel(
        total_nodes=total_nodes,
        total_relationships=total_rels,
        companies=label_counts.get("Company", 0),
        countries=label_counts.get("Country", 0),
        industries=label_counts.get("Industry", 0),
        ports=label_counts.get("Port", 0),
        anon_nodes=label_counts.get("AnonNode", 0),
        disruption_events=label_counts.get("DisruptionEvent", 0),
        label_counts=label_counts,
        relationship_counts=rel_counts,
    )


def get_graph(limit: int = 150, label: Optional[str] = None) -> GraphModel:
    """
    Return a subgraph suitable for browser rendering.

    Default strategy: top-N Company nodes ranked by out-degree,
    then all SUPPLIES_TO edges that exist *between* those N nodes.
    If label is specified, return nodes of that label (up to limit).
    """
    if label and label != "Company":
        # For non-Company labels, return nodes + their SUPPLIES_TO edges
        q = f"""
        MATCH (n:`{label}`)
        WITH n LIMIT $limit
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN
            id(n)          AS src_id,
            labels(n)[0]   AS src_label,
            properties(n)  AS src_props,
            id(m)          AS tgt_id,
            labels(m)[0]   AS tgt_label,
            properties(m)  AS tgt_props,
            id(r)          AS rel_id,
            type(r)        AS rel_type
        """
        rows = neo4j_conn.query(q, {"limit": limit})
        return _build_graph(rows)

    # Default: top Company nodes by degree
    q = """
    MATCH (n:Company)
    WITH n, size((n)-[:SUPPLIES_TO]->()) AS out_deg
    ORDER BY out_deg DESC
    LIMIT $limit
    WITH collect(n) AS top_nodes
    UNWIND top_nodes AS n
    OPTIONAL MATCH (n)-[r:SUPPLIES_TO]->(m:Company)
    WHERE m IN top_nodes
    RETURN
        id(n)          AS src_id,
        labels(n)[0]   AS src_label,
        properties(n)  AS src_props,
        id(m)          AS tgt_id,
        labels(m)[0]   AS tgt_label,
        properties(m)  AS tgt_props,
        id(r)          AS rel_id,
        type(r)        AS rel_type
    """
    rows = neo4j_conn.query(q, {"limit": limit})
    return _build_graph(rows)


def get_node(node_id: int) -> Optional[NodeModel]:
    """Return full properties of a single node by its integer id."""
    q = """
    MATCH (n)
    WHERE id(n) = $node_id
    RETURN id(n) AS nid, labels(n)[0] AS lbl, properties(n) AS props
    """
    rows = neo4j_conn.query(q, {"node_id": node_id})
    if not rows:
        return None
    r = rows[0]
    return NodeModel(id=r["nid"], label=r["lbl"], properties=r["props"])


def get_node_connections(node_id: int) -> GraphModel:
    """
    Return the 1-hop neighbourhood of a node:
    the node itself + all directly connected nodes + the edges between them.
    """
    q = """
    MATCH (n)
    WHERE id(n) = $node_id
    OPTIONAL MATCH (n)-[r]-(m)
    RETURN
        id(n)                                   AS src_id,
        labels(n)[0]                            AS src_label,
        properties(n)                           AS src_props,
        id(m)                                   AS tgt_id,
        labels(m)[0]                            AS tgt_label,
        properties(m)                           AS tgt_props,
        id(r)                                   AS rel_id,
        type(r)                                 AS rel_type,
        CASE WHEN startNode(r) = n THEN id(n) ELSE id(m) END AS actual_src,
        CASE WHEN startNode(r) = n THEN id(m) ELSE id(n) END AS actual_tgt
    LIMIT 60
    """
    rows = neo4j_conn.query(q, {"node_id": node_id})

    nodes: Dict[int, NodeModel] = {}
    relationships: List[RelationshipModel] = []

    for rec in rows:
        sid, tid = rec["src_id"], rec.get("tgt_id")
        if sid not in nodes:
            nodes[sid] = NodeModel(id=sid, label=rec["src_label"] or "Unknown",
                                   properties=rec["src_props"] or {})
        if tid is not None and tid not in nodes:
            nodes[tid] = NodeModel(id=tid, label=rec["tgt_label"] or "Unknown",
                                   properties=rec["tgt_props"] or {})
        if rec.get("rel_id") and tid is not None:
            relationships.append(RelationshipModel(
                id=rec["rel_id"],
                source_id=rec["actual_src"],
                target_id=rec["actual_tgt"],
                type=rec["rel_type"],
                properties={},
            ))

    node_list = list(nodes.values())
    return GraphModel(nodes=node_list, relationships=relationships,
                      total_nodes=len(node_list),
                      total_relationships=len(relationships))


def search_nodes(query: str, limit: int = 20) -> List[SearchResultModel]:
    """
    Case-insensitive full-text search across name, country, industry properties.
    Works without APOC or full-text indexes using CONTAINS.
    """
    q = """
    MATCH (n)
    WHERE (n.name IS NOT NULL     AND toLower(n.name)     CONTAINS toLower($q))
       OR (n.country IS NOT NULL  AND toLower(n.country)  CONTAINS toLower($q))
       OR (n.industry IS NOT NULL AND toLower(n.industry) CONTAINS toLower($q))
       OR (n.node_id IS NOT NULL  AND toLower(n.node_id)  CONTAINS toLower($q))
    RETURN
        id(n)          AS nid,
        labels(n)[0]   AS lbl,
        coalesce(n.name, n.node_id, '') AS display_name,
        n.country      AS country,
        n.industry     AS industry,
        properties(n)  AS props
    LIMIT $limit
    """
    rows = neo4j_conn.query(q, {"q": query, "limit": limit})
    return [
        SearchResultModel(
            id=r["nid"],
            label=r["lbl"],
            name=r["display_name"],
            country=r.get("country"),
            industry=r.get("industry"),
            properties=r["props"],
        )
        for r in rows
    ]
