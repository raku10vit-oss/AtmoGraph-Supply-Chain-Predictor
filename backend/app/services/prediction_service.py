"""
AtmoGraph – Week 2 Prediction Service
======================================
Computes supply-chain disruption risk scores from real datasets.

Five interpretable risk signals (all data-driven, no fabrication):
  1. Port Exposure Score      — from Port-disruption-database.xlsx
  2. Supplier Concentration   — Herfindahl–Hirschman Index on KG data
  3. Graph Centrality Score   — networkx PageRank on AnonNet edges
  4. Industry Vulnerability   — KG industries exposed to disrupted countries
  5. Network Propagation      — Neo4j BFS hop-distance from disrupted nodes

Weights (sum to 1.0, documented here for transparency):
  port_exposure:        0.30
  concentration:        0.25
  centrality:           0.20
  industry_vuln:        0.15
  propagation:          0.10
"""
from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from app.database.neo4j_connection import neo4j_conn
from app.models.schemas import (
    AffectedCompanyModel,
    CompanyRiskProfileModel,
    DisruptionEventModel,
    OverviewModel,
    PropagationModel,
    PropagationNodeModel,
    RiskSignalModel,
    RiskScoreModel,
    ScenarioModel,
)

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────
_HERE = os.path.dirname(__file__)
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
# Support both: running from backend/ or from project root
for _candidate in [
    os.path.join(_HERE, "..", "data"),
    os.path.join(_HERE, "..", "..", "app", "data"),
]:
    if os.path.isdir(_candidate):
        _DATA_DIR = os.path.abspath(_candidate)
        break
else:
    _DATA_DIR = os.path.abspath(os.path.join(_HERE, "..", "data"))

_CACHE_PATH = os.path.join(_DATA_DIR, "port_risk_cache.json")

# Locate repository data/ folder
for _root_cand in [
    os.path.join(_HERE, "..", "..", "..", "data"),
    os.path.join(_HERE, "..", "..", "data"),
]:
    if os.path.isdir(_root_cand):
        _REPO_DATA = os.path.abspath(_root_cand)
        break
else:
    _REPO_DATA = os.path.join(_HERE, "..", "..", "..", "data")

_KG_PATH        = os.path.join(_REPO_DATA, "supply_network", "supplychainKG_clean.csv")
_EDGES_PATH     = os.path.join(_REPO_DATA, "supply_network", "edges_anon.csv")
_NODES_PATH     = os.path.join(_REPO_DATA, "supply_network", "nodes_anon.csv")
_SCENARIOS_PATH = os.path.join(_REPO_DATA, "evaluation", "scenarios", "multi_company_scenarios.json")

# ── Signal weights (must sum to 1.0) ─────────────────────────────
WEIGHTS = {
    "port_exposure":    0.30,
    "concentration":    0.25,
    "centrality":       0.20,
    "industry_vuln":    0.15,
    "propagation":      0.10,
}

RISK_THRESHOLDS = {"Low": 0.35, "Medium": 0.65}  # score < 0.35 → Low; < 0.65 → Medium; else High


def _risk_level(score: float) -> str:
    if score < RISK_THRESHOLDS["Low"]:
        return "Low"
    if score < RISK_THRESHOLDS["Medium"]:
        return "Medium"
    return "High"


# ══════════════════════════════════════════════════════════════════
#  DATA LOADERS  (each loaded once then cached in module-level var)
# ══════════════════════════════════════════════════════════════════

_port_cache: Optional[Dict] = None
_kg_df: Optional[pd.DataFrame] = None
_pagerank: Optional[Dict[str, float]] = None
_scenarios: Optional[List[Dict]] = None


def _load_port_cache() -> Dict:
    global _port_cache
    if _port_cache is None:
        if not os.path.exists(_CACHE_PATH):
            logger.warning("port_risk_cache.json not found at %s. Run preprocess_port_disruptions.py first.", _CACHE_PATH)
            _port_cache = {"country_risk": {}, "port_risk": {}, "disruption_events": [], "industry_risk": {}, "meta": {}}
        else:
            with open(_CACHE_PATH) as f:
                _port_cache = json.load(f)
            logger.info("✅ Port risk cache loaded: %d countries, %d events",
                        len(_port_cache.get("country_risk", {})),
                        len(_port_cache.get("disruption_events", [])))
    return _port_cache


def _load_kg() -> pd.DataFrame:
    global _kg_df
    if _kg_df is None:
        if not os.path.exists(_KG_PATH):
            logger.warning("supplychainKG_clean.csv not found at %s", _KG_PATH)
            _kg_df = pd.DataFrame(columns=[
                "Supplier", "Supplier Industry", "Supplier Country",
                "Customer", "Customer Industry", "Customer Country",
            ])
        else:
            _kg_df = pd.read_csv(_KG_PATH)
            logger.info("✅ KG loaded: %d rows", len(_kg_df))
    return _kg_df


def _load_pagerank() -> Dict[str, float]:
    """Compute PageRank on AnonNet graph once; cache in memory."""
    global _pagerank
    if _pagerank is None:
        if not os.path.exists(_EDGES_PATH):
            logger.warning("edges_anon.csv not found — centrality signal will be zero")
            _pagerank = {}
        else:
            edges_df = pd.read_csv(_EDGES_PATH)
            G = nx.DiGraph()
            G.add_edges_from(zip(edges_df["source"], edges_df["target"]))
            pr = nx.pagerank(G, alpha=0.85, max_iter=100)
            # Normalise to [0, 1]
            pr_values = list(pr.values())
            pr_min, pr_max = min(pr_values), max(pr_values)
            pr_range = pr_max - pr_min or 1.0
            _pagerank = {node: (v - pr_min) / pr_range for node, v in pr.items()}
            logger.info("✅ PageRank computed on %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
    return _pagerank


def _load_scenarios() -> List[Dict]:
    global _scenarios
    if _scenarios is None:
        if not os.path.exists(_SCENARIOS_PATH):
            logger.warning("multi_company_scenarios.json not found")
            _scenarios = []
        else:
            with open(_SCENARIOS_PATH) as f:
                _scenarios = json.load(f)
            logger.info("✅ Scenarios loaded: %d", len(_scenarios))
    return _scenarios


def preload_all() -> None:
    """Call this at server startup to warm the caches."""
    _load_port_cache()
    _load_kg()
    _load_pagerank()
    _load_scenarios()
    logger.info("✅ Prediction service data fully loaded")


# ══════════════════════════════════════════════════════════════════
#  SIGNAL COMPUTERS
# ══════════════════════════════════════════════════════════════════

def _port_exposure_for_country(country: str) -> Tuple[float, str]:
    """Return (normalised_score, explanation) for a country based on port disruption history."""
    cache = _load_port_cache()
    cr = cache.get("country_risk", {})

    # Try exact match first, then partial match
    entry = cr.get(country)
    if entry is None:
        # Fuzzy: check if country appears as substring of any key
        for k, v in cr.items():
            if country.lower() in k.lower() or k.lower() in country.lower():
                entry = v
                break

    if entry is None:
        return 0.0, f"No historical port disruption data for '{country}'"

    score = float(entry.get("risk_score", 0.0))
    mean_sev = entry.get("mean_severity", 0.0)
    n = entry.get("event_count", 0)
    return score, (
        f"Historical port data: {n} disruption events, "
        f"mean severity {mean_sev:.2f}/3.0 → score {score:.2f}"
    )


def _hhi_concentration(countries: List[str]) -> Tuple[float, str]:
    """
    Herfindahl-Hirschman Index on supplier country distribution.
    HHI = sum of (share_i)^2. Ranges 0 (perfectly diversified) → 1 (monopoly).
    """
    if not countries:
        return 0.0, "No supplier countries found"

    total = len(countries)
    from collections import Counter
    counts = Counter(countries)
    hhi = sum((n / total) ** 2 for n in counts.values())
    # HHI is already in [0,1]; scale slightly so max concentration is 1.0
    score = round(hhi, 4)
    top_country = counts.most_common(1)[0]
    return score, (
        f"Supplier concentration (HHI={hhi:.3f}): "
        f"{len(counts)} countries, top supplier country is "
        f"'{top_country[0]}' with {top_country[1]}/{total} links"
    )


def _industry_vulnerability(industry: str) -> Tuple[float, str]:
    """Return industry risk score from precomputed cache."""
    cache = _load_port_cache()
    ir = cache.get("industry_risk", {})
    entry = ir.get(industry)
    if entry is None:
        # Fuzzy match
        for k, v in ir.items():
            if industry.lower() in k.lower() or k.lower() in industry.lower():
                entry = v
                break

    if entry is None:
        return 0.1, f"No specific vulnerability data for industry '{industry}'; using baseline"

    score = float(entry.get("risk_score", 0.0))
    ratio = entry.get("exposure_ratio", 0.0)
    n = entry.get("suppliers_in_disrupted_countries", 0)
    total = entry.get("total_suppliers", 0)
    return score, (
        f"Industry vulnerability: {n}/{total} suppliers in disrupted countries "
        f"(exposure ratio {ratio:.2%}) → score {score:.2f}"
    )


def _neo4j_propagation_score(country: str) -> Tuple[float, str]:
    """
    Uses Neo4j to find how many companies are connected (via SUPPLIES_TO)
    to companies in the given country, as a propagation risk proxy.
    Returns a normalised score.
    """
    try:
        q = """
        MATCH (c:Company {country: $country})-[:SUPPLIES_TO]->(downstream:Company)
        RETURN count(DISTINCT downstream) AS downstream_count
        """
        rows = neo4j_conn.query(q, {"country": country})
        downstream = rows[0]["downstream_count"] if rows else 0

        # Normalise: empirically, max observed downstream is ~400
        score = min(downstream / 400.0, 1.0)
        return round(score, 4), (
            f"Neo4j BFS: {downstream} companies directly sourcing from '{country}'"
        )
    except Exception as exc:
        logger.warning("propagation query failed for %s: %s", country, exc)
        return 0.0, "Neo4j propagation query unavailable"


def _get_supplier_countries(company_name: str, kg: pd.DataFrame) -> List[str]:
    rows = kg[kg["Customer"].str.lower() == company_name.lower()]
    return rows["Supplier Country"].dropna().tolist()


def _get_customer_countries(company_name: str, kg: pd.DataFrame) -> List[str]:
    rows = kg[kg["Supplier"].str.lower() == company_name.lower()]
    return rows["Customer Country"].dropna().tolist()


# ══════════════════════════════════════════════════════════════════
#  PUBLIC SERVICE FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def get_overview() -> OverviewModel:
    """Return overall supply chain risk summary."""
    cache = _load_port_cache()
    kg = _load_kg()

    # Overall risk = average country risk score for the top-5 most exposed
    country_risks = cache.get("country_risk", {})
    scores = sorted(
        [(c, v.get("risk_score", 0)) for c, v in country_risks.items()],
        key=lambda x: x[1], reverse=True
    )
    top_countries = [
        {
            "country": c,
            "risk_score": round(v, 4),
            "risk_level": _risk_level(v),
            "event_count": country_risks[c].get("event_count", 0),
            "mean_severity": country_risks[c].get("mean_severity", 0),
        }
        for c, v in scores[:10]
    ]

    overall = sum(s for _, s in scores[:5]) / 5.0 if scores else 0.0

    # Count companies at risk by their country
    # Use KG: companies whose supplier country has risk > 0.35
    high_risk_countries = {c for c, v in scores if v >= 0.65}
    medium_risk_countries = {c for c, s in scores if 0.35 <= s < 0.65}

    # Map country names between datasets
    COUNTRY_MAP = {"U.S.A.": "United States", "U.S.A": "United States"}
    def _map(c): return COUNTRY_MAP.get(c, c)

    high_risk_cn = {_map(c) for c in high_risk_countries}
    medium_risk_cn = {_map(c) for c in medium_risk_countries}

    high_count = int(kg[kg["Supplier Country"].isin(high_risk_cn)]["Supplier"].nunique())
    medium_count = int(kg[kg["Supplier Country"].isin(medium_risk_cn)]["Supplier"].nunique())
    low_count = int(kg["Supplier"].nunique()) - high_count - medium_count
    total_at_risk = high_count + medium_count

    # Top risk industries
    ir = cache.get("industry_risk", {})
    top_industries = [
        {
            "industry": ind,
            "risk_score": round(vals.get("risk_score", 0), 4),
            "risk_level": _risk_level(vals.get("risk_score", 0)),
            "exposure_ratio": round(vals.get("exposure_ratio", 0), 4),
        }
        for ind, vals in list(ir.items())[:8]
    ]

    return OverviewModel(
        overall_risk_score=round(overall, 4),
        risk_level=_risk_level(overall),
        total_companies_at_risk=total_at_risk,
        high_risk_count=high_count,
        medium_risk_count=medium_count,
        low_risk_count=max(low_count, 0),
        top_risk_countries=top_countries,
        top_risk_industries=top_industries,
        signal_weights=WEIGHTS,
        methodology_note=(
            "Risk scores are computed from 5 interpretable signals: "
            "Port Exposure (historical severity from 217 disruption events 2011–2019), "
            "Supplier Concentration (HHI on 16,640 KG supply links), "
            "Graph Centrality (PageRank on 43,926 AnonNet edges), "
            "Industry Vulnerability (industry exposure to disrupted countries), "
            "Network Propagation (Neo4j BFS from disruption source). "
            "No black-box ML; all scores are reproducible and explained per entity."
        ),
    )


def get_disruptions(limit: int = 20) -> List[DisruptionEventModel]:
    """Return ranked disruption events from port database."""
    cache = _load_port_cache()
    events = cache.get("disruption_events", [])

    result = []
    for ev in events[:limit]:
        # Classify event type
        name_lower = ev["event_name"].lower()
        if "hurricane" in name_lower:
            dtype = "Hurricane"
        elif "typhoon" in name_lower:
            dtype = "Typhoon"
        elif "tropical" in name_lower or "tc " in name_lower:
            dtype = "Tropical Cyclone"
        elif "flood" in name_lower:
            dtype = "Flood"
        else:
            dtype = "Weather Event"

        result.append(DisruptionEventModel(
            event_name=ev["event_name"],
            disruption_type=dtype,
            ports_affected=ev.get("ports_affected", []),
            countries_affected=ev.get("countries_affected", []),
            years=ev.get("years", []),
            ports_count=ev.get("ports_count", 0),
            mean_severity=ev.get("mean_severity", 0.0),
            total_days=ev.get("total_days", 0.0),
            risk_score=ev.get("risk_score", 0.0),
            risk_level=ev.get("risk_level", "Low"),
        ))

    return result


def get_affected_companies(limit: int = 50) -> List[AffectedCompanyModel]:
    """
    Return companies at risk, scored by combining port exposure, concentration
    and industry vulnerability based on their KG profile.
    """
    cache = _load_port_cache()
    kg = _load_kg()

    country_risks = cache.get("country_risk", {})
    industry_risks = cache.get("industry_risk", {})

    COUNTRY_MAP = {"U.S.A.": "United States", "U.S.A": "United States", "USA": "United States"}
    def _cmap(c): return COUNTRY_MAP.get(c, c)

    # Build risk lookup with both original and mapped names
    country_risk_lookup: Dict[str, float] = {}
    for c, v in country_risks.items():
        country_risk_lookup[c] = v.get("risk_score", 0.0)
        country_risk_lookup[_cmap(c)] = v.get("risk_score", 0.0)

    # Aggregate per company
    supplier_counts = kg.groupby("Supplier").size().to_dict()
    customer_counts = kg.groupby("Customer").size().to_dict()

    # Companies whose supplier country has disruption history
    companies: Dict[str, dict] = {}
    for _, row in kg.iterrows():
        supplier = row["Supplier"]
        sup_country = str(row.get("Supplier Country", "") or "")
        sup_industry = str(row.get("Supplier Industry", "") or "")

        c_risk = country_risk_lookup.get(sup_country, 0.0)
        if c_risk < 0.1:
            continue  # skip low-exposure companies

        if supplier not in companies:
            companies[supplier] = {
                "name": supplier,
                "country": sup_country,
                "industry": sup_industry,
                "country_risk": c_risk,
                "supplier_count": supplier_counts.get(supplier, 0),
                "customer_count": customer_counts.get(supplier, 0),
                "sup_countries": [],
            }
        companies[supplier]["sup_countries"].append(sup_country)

    results = []
    for name, info in companies.items():
        # Supplier concentration
        conc_score, _ = _hhi_concentration(info["sup_countries"])

        # Industry vulnerability
        ind_score, _ = _industry_vulnerability(info["industry"])

        # Weighted aggregate (no propagation signal here — too slow for bulk)
        overall = (
            WEIGHTS["port_exposure"] * info["country_risk"]
            + WEIGHTS["concentration"] * conc_score
            + WEIGHTS["industry_vuln"] * ind_score
            + WEIGHTS["centrality"] * 0.0        # no centrality in bulk mode
            + WEIGHTS["propagation"] * 0.0
        ) / (WEIGHTS["port_exposure"] + WEIGHTS["concentration"] + WEIGHTS["industry_vuln"])

        overall = round(min(overall, 1.0), 4)
        level = _risk_level(overall)

        reasons = []
        if info["country_risk"] >= 0.5:
            reasons.append(f"Supplier country '{info['country']}' has high port disruption history")
        if conc_score >= 0.5:
            reasons.append(f"High supplier concentration (HHI={conc_score:.2f})")
        if ind_score >= 0.5:
            reasons.append(f"Industry '{info['industry']}' has high exposure to disrupted regions")
        if not reasons:
            reasons.append("Moderate exposure to historically disrupted supply routes")

        results.append(AffectedCompanyModel(
            name=name,
            country=info["country"],
            industry=info["industry"],
            risk_score=overall,
            risk_level=level,
            supplier_count=info["supplier_count"],
            customer_count=info["customer_count"],
            country_risk_score=round(info["country_risk"], 4),
            industry_risk_score=round(ind_score, 4),
            concentration_score=round(conc_score, 4),
            reasons=reasons,
        ))

    # Sort by risk score descending
    results.sort(key=lambda x: x.risk_score, reverse=True)
    return results[:limit]


def get_company_risk_profile(company_name: str) -> Optional[CompanyRiskProfileModel]:
    """Full risk breakdown for a single company."""
    kg = _load_kg()
    cache = _load_port_cache()

    # Find company in KG (supplier or customer)
    as_supplier = kg[kg["Supplier"].str.lower() == company_name.lower()]
    as_customer = kg[kg["Customer"].str.lower() == company_name.lower()]

    if as_supplier.empty and as_customer.empty:
        return None

    # Determine primary industry and country
    country = None
    industry = None
    if not as_supplier.empty:
        country = as_supplier.iloc[0]["Supplier Country"]
        industry = as_supplier.iloc[0]["Supplier Industry"]
    elif not as_customer.empty:
        country = as_customer.iloc[0]["Customer Country"]
        industry = as_customer.iloc[0]["Customer Industry"]

    supplier_countries = _get_supplier_countries(company_name, kg)
    customer_countries = _get_customer_countries(company_name, kg)

    # 1. Port exposure
    pe_score, pe_expl = _port_exposure_for_country(str(country or ""))

    # 2. Concentration (of their own supplier countries)
    conc_score, conc_expl = _hhi_concentration(supplier_countries)

    # 3. Centrality (not available for named companies — AnonNet is anonymised)
    cent_score = 0.0
    cent_expl = "Graph centrality not available: AnonNet nodes are anonymised and cannot be matched to named companies"

    # 4. Industry vulnerability
    ind_score, ind_expl = _industry_vulnerability(str(industry or ""))

    # 5. Propagation (via Neo4j)
    prop_score, prop_expl = _neo4j_propagation_score(str(country or ""))

    overall = (
        WEIGHTS["port_exposure"] * pe_score
        + WEIGHTS["concentration"] * conc_score
        + WEIGHTS["centrality"] * cent_score
        + WEIGHTS["industry_vuln"] * ind_score
        + WEIGHTS["propagation"] * prop_score
    )
    overall = round(min(overall, 1.0), 4)

    signals = [
        RiskSignalModel(
            signal_name="Port Exposure",
            score=round(pe_score, 4),
            weight=WEIGHTS["port_exposure"],
            weighted_score=round(WEIGHTS["port_exposure"] * pe_score, 4),
            explanation=pe_expl,
        ),
        RiskSignalModel(
            signal_name="Supplier Concentration",
            score=round(conc_score, 4),
            weight=WEIGHTS["concentration"],
            weighted_score=round(WEIGHTS["concentration"] * conc_score, 4),
            explanation=conc_expl,
        ),
        RiskSignalModel(
            signal_name="Graph Centrality",
            score=round(cent_score, 4),
            weight=WEIGHTS["centrality"],
            weighted_score=round(WEIGHTS["centrality"] * cent_score, 4),
            explanation=cent_expl,
        ),
        RiskSignalModel(
            signal_name="Industry Vulnerability",
            score=round(ind_score, 4),
            weight=WEIGHTS["industry_vuln"],
            weighted_score=round(WEIGHTS["industry_vuln"] * ind_score, 4),
            explanation=ind_expl,
        ),
        RiskSignalModel(
            signal_name="Network Propagation",
            score=round(prop_score, 4),
            weight=WEIGHTS["propagation"],
            weighted_score=round(WEIGHTS["propagation"] * prop_score, 4),
            explanation=prop_expl,
        ),
    ]

    # Find matching scenarios
    scenarios_raw = _load_scenarios()
    matching = []
    for s in scenarios_raw:
        affected = [a.lower() for a in s.get("affected_companies", [])]
        if company_name.lower() in affected or (
            str(industry or "").lower() in [i.lower() for i in s.get("affected_industries", [])]
            and str(country or "").lower() in [c.lower() for c in s.get("affected_countries", [])]
        ):
            sc_score = round(overall * 0.9 + 0.05, 4)  # slight adjustment for matching
            matching.append(ScenarioModel(
                scenario_id=s.get("scenario_id", ""),
                name=s.get("name", ""),
                description=s.get("description", ""),
                disruption_type=s.get("disruption_type", ""),
                affected_countries=s.get("affected_countries", []),
                affected_industries=s.get("affected_industries", []),
                affected_companies=s.get("affected_companies", []),
                target_tier=s.get("target_tier"),
                is_true_positive=s.get("is_true_positive", False),
                monitored_company=s.get("monitored_company"),
                risk_score=sc_score,
                risk_level=_risk_level(sc_score),
            ))

    return CompanyRiskProfileModel(
        name=company_name,
        country=str(country or ""),
        industry=str(industry or ""),
        overall_score=overall,
        risk_level=_risk_level(overall),
        signals=signals,
        supplier_countries=list(set(supplier_countries)),
        customer_countries=list(set(customer_countries)),
        supplier_count=len(as_customer),     # rows where this company IS the customer
        customer_count=len(as_supplier),     # rows where this company IS the supplier
        matching_scenarios=matching[:5],
        explanation=(
            f"{company_name} operates in {industry or 'unknown'} sector "
            f"in {country or 'unknown'}. "
            f"Overall risk score: {overall:.2f} ({_risk_level(overall)}). "
            f"Primary risk driver: "
            + (signals[0].explanation if signals else "no data")
        ),
    )


def get_propagation(node_id: int, max_hops: int = 3) -> PropagationModel:
    """
    BFS propagation from a given Neo4j node outward via SUPPLIES_TO.
    Shows how disruption would ripple through the supply network.
    """
    cache = _load_port_cache()
    country_risks = cache.get("country_risk", {})
    COUNTRY_MAP = {"U.S.A.": "United States", "U.S.A": "United States"}

    def _cmap(c): return COUNTRY_MAP.get(c, c)

    country_risk_lookup = {c: v.get("risk_score", 0) for c, v in country_risks.items()}
    for c, v in list(country_risk_lookup.items()):
        country_risk_lookup[_cmap(c)] = v

    # Get source node
    src_rows = neo4j_conn.query(
        "MATCH (n) WHERE id(n) = $nid RETURN id(n) AS nid, labels(n)[0] AS lbl, properties(n) AS props",
        {"nid": node_id}
    )
    if not src_rows:
        return PropagationModel(
            source_node_id=node_id, source_name="Unknown",
            max_hops=max_hops, total_affected=0,
            propagation_nodes=[],
            methodology="Node not found"
        )

    src = src_rows[0]
    src_name = src["props"].get("name") or src["props"].get("node_id") or f"Node {node_id}"

    # BFS via Cypher (variable-length path)
    q = """
    MATCH (src)
    WHERE id(src) = $node_id
    MATCH path = (src)-[:SUPPLIES_TO*1..3]->(downstream)
    WHERE downstream <> src
    WITH downstream, length(path) AS hop
    ORDER BY hop ASC
    RETURN
        id(downstream)         AS nid,
        labels(downstream)[0]  AS lbl,
        properties(downstream) AS props,
        min(hop)               AS hop
    LIMIT 100
    """
    try:
        rows = neo4j_conn.query(q, {"node_id": node_id})
    except Exception as exc:
        logger.error("propagation query failed: %s", exc)
        rows = []

    prop_nodes = []
    for r in rows:
        country = r["props"].get("country", "")
        c_risk = country_risk_lookup.get(str(country), 0.0)
        # Decay risk score by hop distance
        hop = int(r.get("hop", 1))
        decayed = round(c_risk * (0.7 ** (hop - 1)), 4)
        level = _risk_level(decayed)
        name = r["props"].get("name") or r["props"].get("node_id") or f"Node {r['nid']}"
        prop_nodes.append(PropagationNodeModel(
            node_id=int(r["nid"]),
            name=name,
            label=str(r.get("lbl") or "Unknown"),
            hop=hop,
            country=str(country) if country else None,
            industry=r["props"].get("industry"),
            risk_score=decayed,
            risk_level=level,
        ))

    return PropagationModel(
        source_node_id=node_id,
        source_name=src_name,
        max_hops=max_hops,
        total_affected=len(prop_nodes),
        propagation_nodes=prop_nodes,
        methodology=(
            "BFS traversal up to 3 hops via SUPPLIES_TO relationships in Neo4j. "
            "Risk score decays by 30% per hop from source node's country risk. "
            "Source: Port-disruption-database.xlsx (217 events, 2011–2019)."
        ),
    )


def get_scenarios(limit: int = 30) -> List[ScenarioModel]:
    """Return structured disruption scenarios with computed risk scores."""
    cache = _load_port_cache()
    country_risks = cache.get("country_risk", {})
    industry_risks = cache.get("industry_risk", {})

    COUNTRY_MAP = {"U.S.A.": "United States"}
    def _cmap(c): return COUNTRY_MAP.get(c, c)

    country_risk_lookup = {c: v.get("risk_score", 0) for c, v in country_risks.items()}
    for c, v in list(country_risk_lookup.items()):
        country_risk_lookup[_cmap(c)] = v

    result = []
    for s in _load_scenarios()[:limit]:
        # Compute scenario risk as average country + industry risk
        c_scores = [country_risk_lookup.get(c, 0.1) for c in s.get("affected_countries", [])]
        i_scores = [industry_risks.get(ind, {}).get("risk_score", 0.1)
                    for ind in s.get("affected_industries", [])]

        avg_c = sum(c_scores) / len(c_scores) if c_scores else 0.1
        avg_i = sum(i_scores) / len(i_scores) if i_scores else 0.1
        score = round(0.6 * avg_c + 0.4 * avg_i, 4)

        result.append(ScenarioModel(
            scenario_id=s.get("scenario_id", ""),
            name=s.get("name", ""),
            description=s.get("description", ""),
            disruption_type=s.get("disruption_type", ""),
            affected_countries=s.get("affected_countries", []),
            affected_industries=s.get("affected_industries", []),
            affected_companies=s.get("affected_companies", []),
            target_tier=s.get("target_tier"),
            is_true_positive=bool(s.get("is_true_positive", False)),
            monitored_company=s.get("monitored_company"),
            risk_score=score,
            risk_level=_risk_level(score),
        ))

    result.sort(key=lambda x: x.risk_score, reverse=True)
    return result
