# AtmoGraph – Week 2 Architecture
## Disruption Prediction Engine

### Overview

Week 2 adds a data-driven supply chain disruption prediction engine on top of the Week 1 graph foundation. All risk scores are computed from real datasets using five interpretable signals — no black-box ML models.

---

## System Architecture (Week 2)

```
┌─────────────────────────────────────────────────────────┐
│  React Frontend (Vite + React Flow)                     │
│  ┌──────────┐ ┌──────────────────────────────────────┐  │
│  │ Dashboard│ │ PredictionDashboard                  │  │
│  │ (Week 1) │ │  Tabs: Overview | Disruptions |      │  │
│  │          │ │        Companies | Scenarios         │  │
│  └──────────┘ │  Components: RiskScoreGauge          │  │
│               │             DisruptionList           │  │
│               │             AffectedCompanies        │  │
│               │             RiskChart                │  │
│               └──────────────────────────────────────┘  │
│                        Navbar (tab navigation)          │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP / axios
┌───────────────────────▼─────────────────────────────────┐
│  FastAPI Backend                                        │
│  ┌────────────────┐  ┌──────────────────────────────┐  │
│  │ graph_routes   │  │ prediction_routes             │  │
│  │ (Week 1 — 6   │  │ /api/predictions/             │  │
│  │  endpoints)    │  │  overview, disruptions,       │  │
│  └────────────────┘  │  affected-companies,          │  │
│                      │  company/{name},              │  │
│                      │  impact/{country},            │  │
│                      │  propagation/{node_id},       │  │
│                      │  scenarios                    │  │
│                      └──────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────┐    │
│  │ prediction_service                              │    │
│  │  Signal 1: Port Exposure (port_risk_cache.json) │    │
│  │  Signal 2: Supplier Concentration (HHI on KG)   │    │
│  │  Signal 3: Graph Centrality (networkx PageRank)  │    │
│  │  Signal 4: Industry Vulnerability (KG + port DB) │    │
│  │  Signal 5: Propagation (Neo4j BFS Cypher)        │    │
│  └─────────────────────────────────────────────────┘    │
└──────────┬──────────────────────────┬───────────────────┘
           │ Cypher (bolt)            │ File I/O
┌──────────▼──────────┐  ┌───────────▼──────────────────┐
│  Neo4j Graph DB     │  │  Dataset Files               │
│  Company, Country,  │  │  supplychainKG_clean.csv     │
│  Industry, Port,    │  │  Port-disruption-database.xlsx│
│  DisruptionEvent,   │  │  nodes_anon.csv / edges_anon  │
│  AnonNode           │  │  multi_company_scenarios.json │
└─────────────────────┘  └──────────────────────────────┘
```

---

## Risk Scoring Methodology

### Five Signals (weights sum to 1.0)

| Signal | Weight | Source | Method |
|--------|--------|--------|--------|
| Port Exposure | 30% | Port-disruption-database.xlsx (217 events) | Historical mean severity (0–3) per country, min-max normalised |
| Supplier Concentration | 25% | supplychainKG_clean.csv (16,640 links) | Herfindahl–Hirschman Index on supplier country distribution |
| Graph Centrality | 20% | edges_anon.csv (43,926 edges) | NetworkX PageRank (α=0.85), normalised to [0,1] |
| Industry Vulnerability | 15% | KG + port DB | Fraction of industry suppliers in historically disrupted countries |
| Network Propagation | 10% | Neo4j BFS | Downstream company count from disrupted country (normalised) |

### Risk Level Thresholds
```
Score 0.00–0.35 → Low     (green)
Score 0.35–0.65 → Medium  (amber)  
Score 0.65–1.00 → High    (red)
```

### Why Not a Trained ML Model?

The Port Disruption Database contains 217 labelled events across 92 ports. While sufficient for statistical scoring, this is insufficient for training a generalisable classifier (minimum ~1,000+ labelled samples per class recommended). The interpretable signal approach is:
- **Transparent**: every score has a plain-language explanation
- **Reproducible**: same input → same output, no randomness
- **Honest**: no false claims of predictive accuracy

---

## New Files (Week 2)

### Backend
| File | Purpose |
|------|---------|
| `app/services/prediction_service.py` | Core risk computation logic |
| `app/routes/prediction_routes.py` | 7 FastAPI endpoints |
| `app/data/port_risk_cache.json` | Preprocessed XLSX risk statistics |
| `scripts/preprocess_port_disruptions.py` | Cache builder (run once) |
| `scripts/test_week2.py` | 17-test integration test suite |

### Frontend
| File | Purpose |
|------|---------|
| `src/pages/PredictionDashboard.jsx` | 4-tab prediction page |
| `src/components/RiskScoreGauge.jsx` | Animated SVG arc gauge |
| `src/components/DisruptionList.jsx` | Event cards with score bars |
| `src/components/AffectedCompanies.jsx` | Sortable risk company table |
| `src/components/RiskChart.jsx` | Horizontal signal breakdown bars |

### Modified Files
| File | Change |
|------|--------|
| `app/models/schemas.py` | +7 Pydantic models (Week 1 unchanged) |
| `app/main.py` | +prediction_routes registered, v2.0.0, preload_all() on startup |
| `app/routes/graph_routes.py` | Unchanged |
| `app/services/graph_service.py` | Unchanged |
| `requirements.txt` | +scikit-learn ≥1.3.0, +networkx ≥3.0 |
| `src/services/api.js` | +7 prediction API functions (Week 1 unchanged) |
| `src/App.jsx` | State-based routing: graph ↔ predictions |
| `src/components/Navbar.jsx` | +Graph Explorer / Risk Predictions tabs |
| `src/components/Sidebar.jsx` | Version footer updated to v2.0 |
| `src/pages/Dashboard.jsx` | +onNavigate prop for tab switching |

---

## Startup Sequence (Week 2)

```bash
# 1. Build the port risk cache (run once, or after updating XLSX)
cd backend
python scripts/preprocess_port_disruptions.py

# 2. Start the backend (auto-preloads all data caches at startup)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Start the frontend
cd frontend && npm run dev
```

---

## API Endpoints (complete list)

### Week 1 (unchanged)
| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Neo4j connectivity check |
| `GET /api/graph` | Subgraph (top-N companies by degree) |
| `GET /api/graph/statistics` | Node/relationship counts |
| `GET /api/graph/search` | Full-text search |
| `GET /api/graph/node/{id}` | Node details |
| `GET /api/graph/node/{id}/connections` | 1-hop neighbourhood |

### Week 2 (new)
| Endpoint | Description |
|----------|-------------|
| `GET /api/predictions/overview` | Overall risk score + country/industry breakdown |
| `GET /api/predictions/disruptions` | Historical events ranked by risk |
| `GET /api/predictions/affected-companies` | At-risk company list |
| `GET /api/predictions/company/{name}` | Full signal profile for one company |
| `GET /api/predictions/impact/{country}` | Country disruption impact analysis |
| `GET /api/predictions/propagation/{node_id}` | BFS ripple from a Neo4j node |
| `GET /api/predictions/scenarios` | 30 structured evaluation scenarios |
