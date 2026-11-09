"""
AtmoGraph – API Routes
All graph-related REST endpoints are registered here.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.database.neo4j_connection import neo4j_conn
from app.models.schemas import (
    GraphModel,
    HealthModel,
    NodeModel,
    SearchResultModel,
    StatisticsModel,
)
from app.services import graph_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["AtmoGraph"])


# ── Health ─────────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthModel,
    summary="Health check — backend + Neo4j connectivity",
)
async def health_check() -> HealthModel:
    try:
        neo4j_conn.query("RETURN 1 AS ping")
        return HealthModel(
            status="ok",
            neo4j_connected=True,
            message="AtmoGraph backend is running and Neo4j is connected.",
        )
    except Exception as exc:
        logger.warning("Health check: Neo4j unreachable — %s", exc)
        return HealthModel(
            status="degraded",
            neo4j_connected=False,
            message=f"Neo4j unreachable: {exc}",
        )


# ── Statistics ─────────────────────────────────────────────────────────────────

@router.get(
    "/graph/statistics",
    response_model=StatisticsModel,
    summary="Return node and relationship counts per label/type",
)
async def get_statistics() -> StatisticsModel:
    try:
        return graph_service.get_statistics()
    except Exception as exc:
        logger.error("get_statistics error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Search (must come before /graph/node/{id} to avoid conflict) ───────────────

@router.get(
    "/graph/search",
    response_model=List[SearchResultModel],
    summary="Full-text search across name, country, industry",
)
async def search(
    q: str = Query(..., min_length=1, description="Search term"),
    limit: int = Query(20, ge=1, le=100),
) -> List[SearchResultModel]:
    try:
        return graph_service.search_nodes(q, limit=limit)
    except Exception as exc:
        logger.error("search error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Graph ──────────────────────────────────────────────────────────────────────

@router.get(
    "/graph",
    response_model=GraphModel,
    summary="Return a subgraph (default: top-150 companies by out-degree)",
)
async def get_graph(
    limit: int = Query(150, ge=1, le=500, description="Max nodes to return"),
    label: Optional[str] = Query(None, description="Filter by node label"),
) -> GraphModel:
    try:
        return graph_service.get_graph(limit=limit, label=label)
    except Exception as exc:
        logger.error("get_graph error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Node detail ────────────────────────────────────────────────────────────────

@router.get(
    "/graph/node/{node_id}",
    response_model=NodeModel,
    summary="Return all properties of a single node",
)
async def get_node(node_id: int) -> NodeModel:
    node = graph_service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node with id {node_id} not found.")
    return node


@router.get(
    "/graph/node/{node_id}/connections",
    response_model=GraphModel,
    summary="Return the 1-hop neighbourhood of a node",
)
async def get_node_connections(node_id: int) -> GraphModel:
    try:
        return graph_service.get_node_connections(node_id)
    except Exception as exc:
        logger.error("get_node_connections error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
