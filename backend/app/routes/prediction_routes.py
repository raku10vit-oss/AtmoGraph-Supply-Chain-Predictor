"""
AtmoGraph – Week 2 Prediction API Routes
7 endpoints for the disruption prediction engine.
All prefixed with /api/predictions/.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    AffectedCompanyModel,
    CompanyRiskProfileModel,
    DisruptionEventModel,
    OverviewModel,
    PropagationModel,
    ScenarioModel,
)
from app.services import prediction_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


# ── 1. Overview ───────────────────────────────────────────────────

@router.get(
    "/overview",
    response_model=OverviewModel,
    summary="Overall supply chain risk overview — scores, counts, top risk countries and industries",
)
async def get_overview() -> OverviewModel:
    try:
        return prediction_service.get_overview()
    except Exception as exc:
        logger.error("get_overview error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ── 2. Disruption Events ──────────────────────────────────────────

@router.get(
    "/disruptions",
    response_model=List[DisruptionEventModel],
    summary="Ranked list of historical disruption events with risk scores",
)
async def get_disruptions(
    limit: int = Query(20, ge=1, le=50, description="Max events to return"),
) -> List[DisruptionEventModel]:
    try:
        return prediction_service.get_disruptions(limit=limit)
    except Exception as exc:
        logger.error("get_disruptions error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ── 3. Affected Companies ─────────────────────────────────────────

@router.get(
    "/affected-companies",
    response_model=List[AffectedCompanyModel],
    summary="Companies at risk, ranked by combined risk score",
)
async def get_affected_companies(
    limit: int = Query(50, ge=1, le=200, description="Max companies to return"),
) -> List[AffectedCompanyModel]:
    try:
        return prediction_service.get_affected_companies(limit=limit)
    except Exception as exc:
        logger.error("get_affected_companies error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ── 4. Company Risk Profile ───────────────────────────────────────

@router.get(
    "/company/{company_name}",
    response_model=CompanyRiskProfileModel,
    summary="Detailed risk signal breakdown for a named company",
)
async def get_company_profile(company_name: str) -> CompanyRiskProfileModel:
    try:
        profile = prediction_service.get_company_risk_profile(company_name)
        if profile is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_name}' not found in supply chain dataset.",
            )
        return profile
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_company_profile error for '%s': %s", company_name, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ── 5. Country Impact Analysis ────────────────────────────────────

@router.get(
    "/impact/{country}",
    response_model=dict,
    summary="Disruption impact analysis for a given country",
)
async def get_country_impact(country: str) -> dict:
    try:
        from app.services.prediction_service import _load_port_cache, _load_kg, _risk_level
        cache = _load_port_cache()
        kg = _load_kg()

        cr = cache.get("country_risk", {})
        entry = cr.get(country)
        if entry is None:
            # Try partial match
            for k, v in cr.items():
                if country.lower() in k.lower() or k.lower() in country.lower():
                    entry = v
                    country = k
                    break

        if entry is None:
            raise HTTPException(
                status_code=404,
                detail=f"No disruption history found for country '{country}'",
            )

        # Suppliers in this country
        COUNTRY_MAP = {"U.S.A.": "United States", "U.S.A": "United States"}
        mapped_country = COUNTRY_MAP.get(country, country)
        suppliers_here = kg[kg["Supplier Country"] == mapped_country]["Supplier"].unique().tolist()
        customers_served = kg[kg["Supplier Country"] == mapped_country]["Customer"].unique().tolist()

        # Find port entries for this country
        port_entries = {
            port: pdata
            for port, pdata in cache.get("port_risk", {}).items()
            if pdata.get("country") == country
        }

        risk_score = float(entry.get("risk_score", 0.0))
        return {
            "country": country,
            "risk_score": risk_score,
            "risk_level": _risk_level(risk_score),
            "event_count": entry.get("event_count", 0),
            "mean_severity": entry.get("mean_severity", 0.0),
            "mean_days_affected": entry.get("mean_days", 0.0),
            "total_days_affected": entry.get("total_days", 0.0),
            "severity_distribution": entry.get("severity_counts", {}),
            "disruption_events": entry.get("events", []),
            "ports_affected": list(port_entries.keys()),
            "port_count": len(port_entries),
            "suppliers_in_country": len(suppliers_here),
            "customers_at_risk": len(customers_served),
            "sample_suppliers": suppliers_here[:10],
            "sample_customers": customers_served[:10],
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("get_country_impact error for '%s': %s", country, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ── 6. Propagation ────────────────────────────────────────────────

@router.get(
    "/propagation/{node_id}",
    response_model=PropagationModel,
    summary="BFS disruption propagation from a Neo4j node (up to 3 hops via SUPPLIES_TO)",
)
async def get_propagation(
    node_id: int,
    max_hops: int = Query(3, ge=1, le=4, description="Maximum BFS hops"),
) -> PropagationModel:
    try:
        return prediction_service.get_propagation(node_id, max_hops=max_hops)
    except Exception as exc:
        logger.error("get_propagation error for node %d: %s", node_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ── 7. Scenarios ──────────────────────────────────────────────────

@router.get(
    "/scenarios",
    response_model=List[ScenarioModel],
    summary="Structured disruption scenarios with risk scores (from evaluation dataset)",
)
async def get_scenarios(
    limit: int = Query(30, ge=1, le=30, description="Max scenarios"),
) -> List[ScenarioModel]:
    try:
        return prediction_service.get_scenarios(limit=limit)
    except Exception as exc:
        logger.error("get_scenarios error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
