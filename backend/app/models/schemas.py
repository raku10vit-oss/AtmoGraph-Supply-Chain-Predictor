"""
AtmoGraph – Week 2 Pydantic Schemas (Prediction Engine)
All new models are appended here; existing models are UNCHANGED.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════════
#  EXISTING MODELS  (Week 1 — do not remove)
# ══════════════════════════════════════════════════════════════════

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


class GraphModel(BaseModel):
    nodes: List[NodeModel]
    relationships: List[RelationshipModel]
    total_nodes: int
    total_relationships: int


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


class HealthModel(BaseModel):
    status: str           # "ok" | "degraded" | "error"
    neo4j_connected: bool
    message: str
    version: str = "2.0.0"


class SearchResultModel(BaseModel):
    id: int
    label: str
    name: str
    country: Optional[str] = None
    industry: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════
#  NEW MODELS — Week 2 Prediction Engine
# ══════════════════════════════════════════════════════════════════

class RiskSignalModel(BaseModel):
    """One of the five interpretable risk signals."""
    signal_name: str = Field(..., description="Human-readable signal name")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalised score 0–1")
    weight: float = Field(..., description="Weight used in aggregation")
    weighted_score: float = Field(..., description="score × weight")
    explanation: str = Field(..., description="Plain-language reason for this score")


class RiskScoreModel(BaseModel):
    """Aggregated risk score with breakdown of all five signals."""
    entity_name: str
    entity_type: str              # "company" | "country" | "port" | "industry"
    overall_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str               # "Low" | "Medium" | "High"
    signals: List[RiskSignalModel]
    explanation: str


class OverviewModel(BaseModel):
    """Top-level supply chain risk overview."""
    overall_risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    total_companies_at_risk: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    top_risk_countries: List[Dict[str, Any]]
    top_risk_industries: List[Dict[str, Any]]
    signal_weights: Dict[str, float]
    methodology_note: str


class DisruptionEventModel(BaseModel):
    """A historical or scenario disruption event with risk metadata."""
    event_name: str
    disruption_type: str          # "Hurricane" | "Typhoon" | "Flood" etc.
    ports_affected: List[str]
    countries_affected: List[str]
    years: List[int]
    ports_count: int
    mean_severity: float          # 0–3 from source data
    total_days: float
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str


class AffectedCompanyModel(BaseModel):
    """A company identified as at risk from disruption propagation."""
    name: str
    country: Optional[str] = None
    industry: Optional[str] = None
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    supplier_count: int
    customer_count: int
    country_risk_score: float
    industry_risk_score: float
    concentration_score: float
    reasons: List[str]


class PropagationNodeModel(BaseModel):
    """One node in a BFS propagation path."""
    node_id: int
    name: str
    label: str
    hop: int                       # distance from disruption source
    country: Optional[str] = None
    industry: Optional[str] = None
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str


class PropagationModel(BaseModel):
    """Full BFS propagation result from a disrupted node."""
    source_node_id: int
    source_name: str
    max_hops: int
    total_affected: int
    propagation_nodes: List[PropagationNodeModel]
    methodology: str


class ScenarioModel(BaseModel):
    """One of the 30 structured disruption scenarios."""
    scenario_id: str
    name: str
    description: str
    disruption_type: str
    affected_countries: List[str]
    affected_industries: List[str]
    affected_companies: List[str]
    target_tier: Optional[int] = None
    is_true_positive: bool
    monitored_company: Optional[str] = None
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str


class CompanyRiskProfileModel(BaseModel):
    """Detailed risk analysis for a single company."""
    name: str
    country: Optional[str] = None
    industry: Optional[str] = None
    overall_score: float
    risk_level: str
    signals: List[RiskSignalModel]
    supplier_countries: List[str]
    customer_countries: List[str]
    supplier_count: int
    customer_count: int
    matching_scenarios: List[ScenarioModel]
    explanation: str
