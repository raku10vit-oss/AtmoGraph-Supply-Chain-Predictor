# AtmoGraph Dataset Directory

This directory contains the curated datasets used by AtmoGraph for supply chain graph construction,
disruption event modelling, and system evaluation.

**All original source repositories remain untouched on the Desktop. Only data files were copied here.**

---

## Directory Structure

    data/
    ├── supply_network/           <- Graph topology (nodes + edges)
    │   ├── nodes_anon.csv        — AnonNet: 7,245 anonymised supply-network nodes
    │   ├── edges_anon.csv        — AnonNet: 43,926 directed supply-link edges
    │   └── supplychainKG_clean.csv — Named company KG: 16,640 supplier->customer links
    ├── disruption_events/
    │   └── Port-disruption-database.xlsx — 23 climate events x ports, severity, TAD
    ├── delay_prediction/         <- SynDelay (54 MB, NOT committed to Git)
    │   └── README.md             — Download instructions
    └── evaluation/
        ├── benchmark_v2/         <- 1,117 synthetic disruption articles + specs (JSON)
        └── scenarios/            <- 30 disruption scenarios (BMW, Mercedes, Tesla)

---

## Datasets

### 1. supply_network/nodes_anon.csv + edges_anon.csv (AnonNet)
Source: Xu, Long, Brintrup. AnonNet: An Anonymised Real-World Network for Supply Network Analysis, 2025. MIM 2025 Data Challenge.
Licence: No explicit licence — academic/research use, please cite.
Stats: 7,245 nodes, 43,926 edges. Anonymised real-world multi-tier manufacturer network.
Columns (nodes): id, location, products
Columns (edges): source, target
Usage: Primary graph topology for AtmoGraph disruption propagation modelling.

### 2. supply_network/supplychainKG_clean.csv
Source: AlMahri, Xu, Brintrup. Supply Chain Disruption Monitoring, 2025-2026. University of Cambridge.
Licence: CC BY-NC 4.0 (Attribution, NonCommercial). (c) 2025-2026 Sara AlMahri.
Stats: 16,640 supply links, 6,222 companies, 96 countries, 24 industries.
Columns: Supplier, Supplier Industry, Supplier Country, Customer, Customer Industry, Customer Country, Relationship1-3
Usage: Named-company knowledge graph for real-world supplier identification and risk scoring.

Citation:
  @misc{almahri2025scframework,
    author = {AlMahri, Sara},
    title  = {Supply Chain Disruption Monitoring: Framework, Evaluation Data, and Results},
    year   = {2025},
    url    = {https://github.com/sara-almahri/supply-chain-disruption-monitoring}
  }

### 3. disruption_events/Port-disruption-database.xlsx
Source: (authors). Port disruptions due to climate extremes. Transportation Research Part D.
Licence: No explicit licence — academic/research use, please cite.
Stats: 23 climate extreme events (2011-2019): 8 Hurricanes, 10 TCs, 3 Typhoons, 2 Floods.
Schema: event name, country, port, year, date, days (reduction/shutdown/recovery/TAD), severity (0-3).
Usage: Ground-truth disruption event table linking weather events to port operational impact.

### 4. delay_prediction/syndelay_v1.csv (NOT committed - 54 MB)
Source: Xu, Long, Brintrup. SynDelay: A Synthetic Dataset for Delivery Delay Prediction, 2025. MIM 2025.
Licence: No explicit licence — academic/research use, please cite.
Stats: 155,489 orders, 41 features, multiclass delay label.
To obtain: Download from MIM 2025 challenge repository and place at data/delay_prediction/syndelay_v1.csv

### 5. evaluation/benchmark_v2/ (AlMahri Chapter 4)
Source: CC BY-NC 4.0.
Contents: 1,117 synthetic disruption news articles (JSON) + specs.json + test_set.json

### 6. evaluation/scenarios/ (AlMahri Chapter 5)
Source: CC BY-NC 4.0.
Contents: 30 disruption scenarios for BMW, Mercedes-Benz, Tesla with ground-truth decisions.

---

## Licence Summary

| Dataset                  | Licence         | Commercial Use      |
|--------------------------|-----------------|---------------------|
| AnonNet                  | Academic/cite   | Not specified       |
| Port Disruption Database | Academic/cite   | Not specified       |
| Supply Chain KG          | CC BY-NC 4.0    | Non-commercial only |
| SynDelay                 | Academic/cite   | Not specified       |
| Benchmark + Scenarios    | CC BY-NC 4.0    | Non-commercial only |

NOTE: For any commercial application, obtain explicit permission from dataset authors
or replace with commercially licensed alternatives.
