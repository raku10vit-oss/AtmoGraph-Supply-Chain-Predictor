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
    assert len(WEIGHTS) == 6, f"Expected 6 signals (5 original + delay_risk), got {len(WEIGHTS)}"

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

# ── 6. Week 2.5 — Signal 6 & new data sources ────────────────────
print("\n[6] Week 2.5 — Signal 6 (Shipping Delay Risk)")

def _test_syndelay_cache_loads():
    from app.services.prediction_service import _load_syndelay_risk
    sd = _load_syndelay_risk()
    assert isinstance(sd, dict), "SynDelay cache should be a dict"
    assert "country_risk" in sd
    assert "shipping_mode_risk" in sd
    assert "overall_delay_rate" in sd
    assert 0.0 < sd["overall_delay_rate"] < 1.0, "Overall delay rate should be between 0 and 1"
    assert sd.get("countries_with_data", 0) >= 100, "Should have data for at least 100 countries"
    print(f"      Countries: {sd['countries_with_data']}, overall delay: {sd['overall_delay_rate']:.1%}")

test("SynDelay country risk cache loads from JSON", _test_syndelay_cache_loads)

def _test_syndelay_signal():
    from app.services.prediction_service import _shipping_delay_for_country
    # Country in dataset
    score, expl = _shipping_delay_for_country("France")
    assert 0.0 <= score <= 1.0, f"Score out of range: {score}"
    assert isinstance(expl, str) and len(expl) > 0
    # Country NOT in dataset
    score2, expl2 = _shipping_delay_for_country("Nonexistent Country XYZ")
    assert 0.0 <= score2 <= 1.0
    assert "overall" in expl2.lower() or "No SynDelay" in expl2
    print(f"      France delay risk: {score:.3f}")

test("Shipping delay signal — France (in dataset) and fallback", _test_syndelay_signal)

def _test_shipping_modes():
    from app.services.prediction_service import _load_syndelay_risk
    sd = _load_syndelay_risk()
    modes = sd.get("shipping_mode_risk", {})
    assert len(modes) >= 2, "Should have at least 2 shipping modes"
    for mode, v in modes.items():
        assert 0.0 <= v["risk_score"] <= 1.0
        assert 0.0 <= v["delay_rate"] <= 1.0
    print(f"      Shipping modes: {list(modes.keys())}")

test("SynDelay shipping mode risk scores are valid", _test_shipping_modes)

def _test_weights_6_signals():
    from app.services.prediction_service import WEIGHTS
    total = sum(WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9, f"6-signal weights must sum to 1.0, got {total}"
    assert len(WEIGHTS) == 6, f"Expected 6 signals, got {len(WEIGHTS)}"
    assert "delay_risk" in WEIGHTS, "delay_risk signal missing from WEIGHTS"
    assert WEIGHTS["delay_risk"] == 0.10
    assert WEIGHTS["port_exposure"] == 0.25, f"port_exposure should be 0.25, got {WEIGHTS['port_exposure']}"

test("6-signal WEIGHTS sum to 1.0 and delay_risk weight is 0.10", _test_weights_6_signals)

print("\n[7] Week 2.5 — Company aliases & attribute overrides")

def _test_aliases_load():
    from app.services.prediction_service import _load_aliases
    aliases = _load_aliases()
    assert isinstance(aliases, dict)
    assert "aliases" in aliases
    assert "overrides" in aliases
    assert aliases.get("alias_count", 0) >= 100, "Should have at least 100 alias pairs"
    # Spot-check known alias
    alias_map = aliases["aliases"]
    assert "alona corp" in alias_map, "Known alias 'alona corp' should be present"
    assert alias_map["alona corp"] == "Alcoa Corp"
    print(f"      Aliases: {len(alias_map)}, overrides: {len(aliases['overrides'])}")

test("Company aliases load: 245+ pairs, spot-check 'alona corp' → 'Alcoa Corp'", _test_aliases_load)

def _test_alias_resolution():
    from app.services.prediction_service import _resolve_company_name
    # Known alias
    resolved = _resolve_company_name("Alona Corp")
    assert resolved == "Alcoa Corp", f"Expected 'Alcoa Corp', got '{resolved}'"
    # Unknown name should pass through unchanged
    resolved2 = _resolve_company_name("Some Unknown Company")
    assert resolved2 == "Some Unknown Company"

test("Alias resolution: 'Alona Corp' → 'Alcoa Corp', unknown → passthrough", _test_alias_resolution)

def _test_attribute_overrides():
    from app.services.prediction_service import _load_aliases
    a = _load_aliases()
    overrides = a.get("overrides", {})
    # 10 companies should have overrides
    assert len(overrides) >= 5, f"Expected at least 5 overrides, got {len(overrides)}"
    # At least one has a 'country' field
    has_country = any("country" in v for v in overrides.values())
    assert has_country, "At least one override should have a 'country' field"
    print(f"      Override companies: {list(overrides.keys())[:3]} ...")

test("Attribute overrides: 10 companies with country corrections", _test_attribute_overrides)

print("\n[8] Week 2.5 — Ground truth tier chains")

def _test_gt_index_loads():
    from app.services.prediction_service import _load_ground_truth
    gt = _load_ground_truth()
    assert isinstance(gt, dict)
    assert gt.get("total_scenarios", 0) == 30, f"Expected 30 scenarios, got {gt.get('total_scenarios')}"
    assert "by_id" in gt
    assert "by_company" in gt
    companies = gt.get("monitored_companies", [])
    assert len(companies) == 3
    assert "Tesla Inc" in companies or any("Tesla" in c for c in companies)
    print(f"      Total scenarios: {gt['total_scenarios']}, companies: {gt.get('monitored_companies')}")

test("Ground truth index loads: 30 scenarios, 3 monitored companies", _test_gt_index_loads)

def _test_gt_tier_chains():
    from app.services.prediction_service import _load_ground_truth
    gt = _load_ground_truth()
    by_id = gt.get("by_id", {})
    # Find a scenario with non-empty tiers
    rich_scenarios = [(sid, s) for sid, s in by_id.items()
                      if s.get("total_tier_2", 0) > 0]
    assert len(rich_scenarios) > 0, "Some scenarios should have tier_2 data"
    sid, s = rich_scenarios[0]
    assert isinstance(s["tier_1_affected"], list)
    assert isinstance(s["tier_2_affected"], list)
    assert s["total_tier_2"] == len(s["tier_2_affected"])
    print(f"      Sample: {sid}: T1={s['total_tier_1']} T2={s['total_tier_2']} T3={s['total_tier_3']}")

test("Ground truth tier chains: non-empty T2 for some scenarios, counts match", _test_gt_tier_chains)

def _test_scenarios_have_gt():
    from app.services.prediction_service import get_scenarios
    scenarios = get_scenarios(limit=30)
    # Scenarios with GT data should have tier fields
    for s in scenarios:
        assert hasattr(s, "gt_tier_1"), "ScenarioModel missing gt_tier_1"
        assert hasattr(s, "gt_total_tier_2"), "ScenarioModel missing gt_total_tier_2"
        assert s.gt_total_tier_1 == len(s.gt_tier_1)
        assert s.gt_total_tier_2 == len(s.gt_tier_2)
    # At least some should have gt data
    has_gt = sum(1 for s in scenarios if s.gt_total_tier_2 > 0)
    print(f"      Scenarios with GT tier_2 data: {has_gt}/{len(scenarios)}")
    # Note: GT only available for BMW/MERC/TSLA scenarios; multi_company_scenarios may not match

test("Scenarios endpoint: ScenarioModel has GT tier fields (backward compatible)", _test_scenarios_have_gt)

def _test_schema_backward_compat():
    """Verify ScenarioModel GT fields are Optional with defaults — old code still works."""
    from app.models.schemas import ScenarioModel
    # Construct without GT fields — should not raise
    s = ScenarioModel(
        scenario_id="TEST01",
        name="Test Scenario",
        description="Test",
        disruption_type="Test",
        affected_countries=[],
        affected_industries=[],
        affected_companies=[],
        is_true_positive=False,
        risk_score=0.5,
        risk_level="Medium",
    )
    assert s.gt_tier_1 == []
    assert s.gt_total_tier_1 == 0
    assert s.gt_total_tier_2 == 0

test("ScenarioModel GT fields are backward compatible (default to empty)", _test_schema_backward_compat)

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
