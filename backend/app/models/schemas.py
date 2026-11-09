"""
AtmoGraph – Pydantic Response Schemas
All models used as FastAPI response bodies.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Node / Relationship ────────────────────────────────────────────────────────

class NodeModel(BaseModel):
    id: int = Field(..., description="Neo4j internal node id")
    label: str = Field(..., description="Primary node label (Company, Country, …)")
    properties: Dict[str, Any] = Field(default_factory=dict)


class RelationshipModel(BaseModel):
    id: int = Field(..., description="Neo4j internal relationship id")
    source_id: int
    target_id: int
    type: str = Field(..., description="Relationship type (SUPPLIES_TO, LOCATED_IN, …)")
    properties: Dict[str, Any] = Field(default_factory=dict)


# ── Graph payload ──────────────────────────────────────────────────────────────

class GraphModel(BaseModel):
    nodes: List[NodeModel]
    relationships: List[RelationshipModel]
    total_nodes: int
    total_relationships: int


# ── Statistics ─────────────────────────────────────────────────────────────────

class StatisticsModel(BaseModel):
    total_nodes: int
    total_relationships: int
    companies: int
    countries: int
    industries: int
    ports: int
    anon_nodes: int
    disruption_events: int
    label_counts: Dict[str, int] = Field(default_factory=dict)
    relationship_counts: Dict[str, int] = Field(default_factory=dict)


# ── Health check ───────────────────────────────────────────────────────────────

class HealthModel(BaseModel):
    status: str           # "ok" | "degraded" | "error"
    neo4j_connected: bool
    message: str
    version: str = "1.0.0"


# ── Search ─────────────────────────────────────────────────────────────────────

class SearchResultModel(BaseModel):
    id: int
    label: str
    name: str
    country: Optional[str] = None
    industry: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
