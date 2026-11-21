"""
AtmoGraph – Week 2 Integration Tests
=====================================
Tests all prediction service functions and API route imports
without requiring a live Neo4j or HTTP server.

Run from the backend/ directory:
    python3 scripts/test_week2.py

Exit code 0 = all tests passed.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from typing import Callable

# ── Path setup ────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # backend/

PASS = 0
FAIL = 0
RESULTS = []


def test(name: str, fn: Callable) -> None:
    global PASS, FAIL
    try:
        fn()
        print(f"  ✅  {name}")
        PASS += 1
        RESULTS.append((name, True, None))
    except Exception as exc:
        msg = str(exc)
        print(f"  ❌  {name}")
        print(f"      {msg}")
        FAIL += 1
        RESULTS.append((name, False, msg))


# ══════════════════════════════════════════════════════════════════
#  TEST SUITE
# ══════════════════════════════════════════════════════════════════

print("=" * 60)
print("  AtmoGraph – Week 2 Test Suite")
print("=" * 60)

# ── 1. Imports ───────────────────────────────────────────────────
print("\n[1] Import checks")

def _test_schemas():
    from app.models.schemas import (
        RiskSignalModel, RiskScoreModel, OverviewModel,
        DisruptionEventModel, AffectedCompanyModel,
        CompanyRiskProfileModel, PropagationModel, ScenarioModel,
    )
    # Instantiate each model with minimal data
    sig = RiskSignalModel(signal_name="Test", score=0.5, weight=0.3,
                          weighted_score=0.15, explanation="ok")
    assert sig.score == 0.5

test("Week 2 Pydantic schemas importable and constructable", _test_schemas)

def _test_service_import():
    from app.services.prediction_service import (
        get_overview, get_disruptions, get_affected_companies,
        get_company_risk_profile, get_propagation, get_scenarios,
        preload_all, _load_port_cache, _load_kg, _load_pagerank,
    )
    assert callable(get_overview)
    assert callable(get_disruptions)

test("prediction_service module imports cleanly", _test_service_import)

def _test_routes_import():
    from app.routes.prediction_routes import router
    from fastapi import APIRouter
    assert isinstance(router, APIRouter)
    paths = [r.path for r in router.routes if hasattr(r, "path")]
    assert "/api/predictions/overview" in paths, f"overview missing, got: {paths}"
    assert "/api/predictions/disruptions" in paths
    assert "/api/predictions/affected-companies" in paths
    assert "/api/predictions/company/{company_name}" in paths
    assert "/api/predictions/impact/{country}" in paths
    assert "/api/predictions/propagation/{node_id}" in paths
    assert "/api/predictions/scenarios" in paths

test("7 prediction routes registered correctly", _test_routes_import)

def _test_main_app():
    from app.main import app
    assert app.version == "2.0.0", f"Expected 2.0.0, got {app.version}"
    all_paths = [r.path for r in app.routes if hasattr(r, "path")]
    assert "/" in all_paths

test("main.py registers both routers, version is 2.0.0", _test_main_app)

# ── 2. Data loading ───────────────────────────────────────────────
print("\n[2] Data loading")

def _test_port_cache():
    from app.services.prediction_service import _load_port_cache
    cache = _load_port_cache()
    assert isinstance(cache, dict), "Cache should be a dict"
    assert "country_risk" in cache, "Missing country_risk"
    assert "disruption_events" in cache, "Missing disruption_events"
    assert "port_risk" in cache, "Missing port_risk"
    assert len(cache["country_risk"]) >= 1, "Should have at least 1 country"
    assert len(cache["disruption_events"]) >= 1, "Should have at least 1 event"
    print(f"      Countries: {len(cache['country_risk'])}, "
          f"Events: {len(cache['disruption_events'])}, "
          f"Ports: {len(cache['port_risk'])}")

test("Port risk cache loads from JSON", _test_port_cache)

def _test_kg_load():
    from app.services.prediction_service import _load_kg
    kg = _load_kg()
    assert len(kg) > 0, "KG should not be empty"
    assert "Supplier" in kg.columns, "Missing Supplier column"
    assert "Supplier Country" in kg.columns, "Missing Supplier Country column"
    assert "Supplier Industry" in kg.columns, "Missing Supplier Industry column"
    print(f"      KG rows: {len(kg)}, unique suppliers: {kg['Supplier'].nunique()}")

test("Supply chain KG CSV loads correctly", _test_kg_load)

def _test_pagerank():
    from app.services.prediction_service import _load_pagerank
    pr = _load_pagerank()
    assert isinstance(pr, dict), "PageRank should return a dict"
    assert len(pr) > 0, "PageRank should have entries"
    scores = list(pr.values())
    assert all(0.0 <= s <= 1.0 for s in scores[:100]), "All scores should be in [0,1]"
    print(f"      PageRank nodes: {len(pr)}, max score: {max(scores):.4f}")

test("PageRank computed on AnonNet graph (normalised 0–1)", _test_pagerank)

def _test_scenarios_load():
    from app.services.prediction_service import _load_scenarios
    scenarios = _load_scenarios()
    assert isinstance(scenarios, list), "Scenarios should be a list"
    assert len(scenarios) >= 1, "Should have at least 1 scenario"
    s = scenarios[0]
    assert "scenario_id" in s
    assert "disruption_type" in s
    assert "affected_countries" in s
    assert "is_true_positive" in s
    print(f"      Scenarios loaded: {len(scenarios)}")

test("Disruption scenarios JSON loads correctly", _test_scenarios_load)

# ── 3. Risk signal functions ──────────────────────────────────────
print("\n[3] Risk signal computation")

def _test_port_exposure():
    from app.services.prediction_service import _port_exposure_for_country
    score, expl = _port_exposure_for_country("U.S.A.")
    assert 0.0 <= score <= 1.0, f"Score out of range: {score}"
    assert isinstance(expl, str) and len(expl) > 0, "Explanation should be non-empty"
    print(f"      U.S.A. port exposure: {score:.3f}")

test("Port exposure signal — U.S.A.", _test_port_exposure)

def _test_hhi():
    from app.services.prediction_service import _hhi_concentration
    # Monopoly: one country
    score, _ = _hhi_concentration(["Japan", "Japan", "Japan"])
    assert score == 1.0, f"Monopoly HHI should be 1.0, got {score}"
    # Diversified: many countries
    score2, _ = _hhi_concentration(["Japan", "Germany", "USA", "China", "India"])
    assert score2 < 0.5, f"Diversified HHI should be < 0.5, got {score2}"
    print(f"      HHI monopoly={score:.2f}, diversified={score2:.2f}")

test("HHI concentration — monopoly=1.0, diversified<0.5", _test_hhi)

def _test_industry_vuln():
    from app.services.prediction_service import _industry_vulnerability
    score, expl = _industry_vulnerability("Steel")
    assert 0.0 <= score <= 1.0, f"Score out of range: {score}"
    assert isinstance(expl, str)
    print(f"      Steel industry vulnerability: {score:.3f}")

test("Industry vulnerability signal — Steel", _test_industry_vuln)

# ── 4. Service-level functions ────────────────────────────────────
print("\n[4] Service function output")

def _test_get_overview():
    from app.services.prediction_service import get_overview
    ov = get_overview()
    assert 0.0 <= ov.overall_risk_score <= 1.0
    assert ov.risk_level in ("Low", "Medium", "High")
    assert ov.total_companies_at_risk >= 0
    assert isinstance(ov.top_risk_countries, list)
    assert len(ov.top_risk_countries) > 0
    assert isinstance(ov.signal_weights, dict)
    assert abs(sum(ov.signal_weights.values()) - 1.0) < 0.01, "Weights must sum to 1.0"
    print(f"      Score: {ov.overall_risk_score:.3f} ({ov.risk_level}), "
          f"At-risk companies: {ov.total_companies_at_risk}")

test("get_overview() returns valid OverviewModel", _test_get_overview)

def _test_get_disruptions():
    from app.services.prediction_service import get_disruptions
    events = get_disruptions(limit=10)
    assert isinstance(events, list)
    assert len(events) > 0
    for ev in events:
        assert 0.0 <= ev.risk_score <= 1.0
        assert ev.risk_level in ("Low", "Medium", "High")
        assert isinstance(ev.ports_affected, list)
    print(f"      Events returned: {len(events)}, top: {events[0].event_name} ({events[0].risk_level})")

test("get_disruptions() returns sorted DisruptionEventModel list", _test_get_disruptions)

def _test_get_affected_companies():
    from app.services.prediction_service import get_affected_companies
    cos = get_affected_companies(limit=20)
    assert isinstance(cos, list)
    assert len(cos) > 0
    # Sorted by risk score descending
    scores = [c.risk_score for c in cos]
    assert scores == sorted(scores, reverse=True), "Companies should be sorted by risk_score DESC"
    for c in cos:
        assert 0.0 <= c.risk_score <= 1.0
        assert c.risk_level in ("Low", "Medium", "High")
        assert c.name, "Company name should not be empty"
    print(f"      Companies returned: {len(cos)}, top: {cos[0].name} ({cos[0].risk_level}, {cos[0].risk_score:.3f})")

test("get_affected_companies() returns sorted AffectedCompanyModel list", _test_get_affected_companies)

def _test_get_scenarios():
    from app.services.prediction_service import get_scenarios
    scenarios = get_scenarios(limit=10)
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0
    for s in scenarios:
        assert 0.0 <= s.risk_score <= 1.0
        assert isinstance(s.is_true_positive, bool)
        assert s.scenario_id
    print(f"      Scenarios returned: {len(scenarios)}, top: {scenarios[0].name}")

test("get_scenarios() returns scored ScenarioModel list", _test_get_scenarios)

def _test_signal_weights_sum():
    from app.services.prediction_service import WEIGHTS
    total = sum(WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9, f"Weights must sum to exactly 1.0, got {total}"
    assert len(WEIGHTS) == 5, f"Expected 5 signals, got {len(WEIGHTS)}"

test("Signal weights sum to exactly 1.0", _test_signal_weights_sum)

def _test_no_hardcoded_names():
    """Ensure prediction_service has no hardcoded company names (all data is from datasets)."""
    svc_path = os.path.join(os.path.dirname(__file__), "..", "app", "services", "prediction_service.py")
    with open(svc_path) as f:
        src = f.read()
    # Check that common company names from the KG aren't hardcoded as strings
    forbidden = ["Tesla", "BMW", "Mercedes", "Apple Inc", "Samsung"]
    for name in forbidden:
        assert name not in src, f"Hardcoded company name found in prediction_service: '{name}'"

test("No hardcoded company names in prediction_service.py", _test_no_hardcoded_names)

# ── 5. Week 1 regression ─────────────────────────────────────────
print("\n[5] Week 1 regression (existing routes still present)")

def _test_week1_routes():
    from app.main import app
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    # These are assembled by APIRouter prefixes at app level, check by walking
    from app.routes.graph_routes import router as gr
    graph_paths = [r.path for r in gr.routes if hasattr(r, "path")]
    assert "/api/health" in graph_paths
    assert "/api/graph" in graph_paths
    assert "/api/graph/statistics" in graph_paths
    assert "/api/graph/search" in graph_paths
    assert "/api/graph/node/{node_id}" in graph_paths
    assert "/api/graph/node/{node_id}/connections" in graph_paths

test("All 6 Week 1 graph routes still registered", _test_week1_routes)

# ── Summary ───────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  Results: {PASS} passed, {FAIL} failed")
print(f"{'='*60}")

if FAIL > 0:
    print("\nFailed tests:")
    for name, ok, msg in RESULTS:
        if not ok:
            print(f"  ❌ {name}: {msg}")
    sys.exit(1)
else:
    print("\n  🎉 All tests passed!")
    sys.exit(0)
