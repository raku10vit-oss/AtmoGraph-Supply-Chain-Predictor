# AtmoGraph – Supply Chain Ripple Effect Predictor

> **AI-powered supply chain disruption prediction using Graph Databases, FastAPI, and React Flow**

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-green)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-6.x-orange)](https://neo4j.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)
[![React Flow](https://img.shields.io/badge/React_Flow-11-purple)](https://reactflow.dev)

---

## 📋 Project Overview

AtmoGraph models global supply chains as interconnected graphs and predicts how disruptions propagate across suppliers, manufacturers, ports, shipping routes, and industries.

## 🏗️ Week 1 Status — Graph Foundation ✅

| Component | Status |
|---|---|
| Neo4j schema (6 node labels, 6 rel types) | ✅ Ready |
| Data import scripts (3 datasets) | ✅ Ready |
| FastAPI backend (6 endpoints) | ✅ Ready |
| React + Vite + React Flow frontend | ✅ Ready |
| Interactive graph dashboard | ✅ Ready |

---

## 🗂️ Project Structure

```
AtmoGraph-Supply-Chain-Predictor/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── config.py           # Environment variable loading
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── database/
│   │   │   ├── neo4j_connection.py
│   │   │   └── schema.py
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic response models
│   │   ├── services/
│   │   │   └── graph_service.py # Cypher query logic
│   │   └── routes/
│   │       └── graph_routes.py  # API route handlers
│   ├── scripts/
│   │   ├── test_neo4j.py
│   │   ├── import_supply_chain.py
│   │   ├── import_anonnet.py
│   │   ├── import_port_disruptions.py
│   │   └── verify_graph.py
│   ├── requirements.txt
│   └── .env.example
├── database/
│   └── cypher/
│       ├── constraints.cypher   # Run before importing data
│       ├── schema.cypher        # Schema exploration queries
│       ├── import_nodes.cypher  # Reference templates
│       └── import_relationships.cypher
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── services/api.js      # Axios API client
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── StatisticsCards.jsx
│   │   │   ├── GraphVisualization.jsx
│   │   │   └── NodeDetails.jsx
│   │   └── pages/Dashboard.jsx
│   └── .env.example
├── data/                       # Curated datasets (see data/README.md)
│   ├── supply_network/
│   ├── disruption_events/
│   └── evaluation/
└── docs/
    ├── WEEK1_ARCHITECTURE.md
    ├── DATABASE_SCHEMA.md
    └── DATA_DICTIONARY.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- **Neo4j** (Desktop or Aura Free)

### Step 1 — Start Neo4j

**Option A — Neo4j Desktop** (local):
1. Download from https://neo4j.com/download/
2. Create a project → Start a database
3. Note your bolt URI, username, password

**Option B — Neo4j Aura** (free cloud):
1. Sign up at https://neo4j.com/cloud/platform/aura-graph-database/
2. Create a free instance → Download credentials

### Step 2 — Backend setup

```bash
cd backend

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Neo4j credentials

# Test Neo4j connectivity
python scripts/test_neo4j.py
```

### Step 3 — Import datasets

```bash
cd backend

# Apply constraints (run once in Neo4j Browser)
# Paste contents of: database/cypher/constraints.cypher

# Import datasets (order matters)
python scripts/import_supply_chain.py   # ~2 min
python scripts/import_anonnet.py        # ~3 min
python scripts/import_port_disruptions.py

# Verify everything imported correctly
python scripts/verify_graph.py
```

### Step 4 — Start the backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### Step 5 — Start the frontend

```bash
cd frontend
npm install   # first time only
npm run dev
```

Open http://localhost:5173 in your browser.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Backend + Neo4j health check |
| GET | `/api/graph/statistics` | Node and relationship counts |
| GET | `/api/graph?limit=150&label=Company` | Paginated subgraph |
| GET | `/api/graph/node/{id}` | Single node properties |
| GET | `/api/graph/node/{id}/connections` | 1-hop neighbourhood |
| GET | `/api/graph/search?q=Steel` | Full-text node search |

---

## 📊 Datasets

| Dataset | Nodes | Edges | Licence |
|---|---|---|---|
| Supply Chain KG (supplychainKG_clean.csv) | 6,222 companies | 16,640 SUPPLIES_TO | CC BY-NC 4.0 |
| AnonNet (nodes_anon + edges_anon) | 7,245 anon nodes | 43,926 CONNECTS_TO | Academic use |
| Port Disruption Database (XLSX) | ~25 ports | ~23 events | Academic use |

See [`data/README.md`](data/README.md) for full details.

---

## 🗺️ Development Roadmap

| Week | Focus | Status |
|---|---|---|
| **Week 1** | Graph foundation, Neo4j, FastAPI, React dashboard | ✅ **Complete** |
| Week 2 | NLP pipeline, Named Entity Recognition, news ingestion | 🔜 |
| Week 3 | Graph Neural Network, risk estimation | 🔜 |
| Week 4 | Real-time integration, WebSockets, 30/60/90-day forecasts | 🔜 |

---

## 📄 Documentation

- [`docs/WEEK1_ARCHITECTURE.md`](docs/WEEK1_ARCHITECTURE.md) — System architecture
- [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) — Full Neo4j schema reference
- [`data/README.md`](data/README.md) — Dataset documentation

---

**Domain:** AI / Machine Learning / Supply Chain Analytics  
**Stack:** Python · FastAPI · Neo4j · React · React Flow · Cypher
