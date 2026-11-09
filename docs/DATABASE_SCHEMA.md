# AtmoGraph – Neo4j Database Schema

## Node Labels

### `Company`
Represents a named supply chain participant (supplier or customer).
Source: `data/supply_network/supplychainKG_clean.csv`

| Property | Type | Description | Example |
|---|---|---|---|
| `name` | String (UNIQUE) | Company name | `"Eni SpA"` |
| `country` | String | Headquarters country | `"Italy"` |
| `industry` | String | Primary industry sector | `"Oil & Gas Producers"` |
| `type` | String | Role: `Supplier`, `Customer`, or `Both` | `"Both"` |
| `source_dataset` | String | Origin | `"supplychainKG"` |

**Indexes**: `name` (unique constraint), `country`, `industry`, `type`

---

### `Country`
Represents a country. Shared by Company nodes via LOCATED_IN and Port nodes via PORT_IN.
Source: derived from `supplychainKG_clean.csv` and `Port-disruption-database.xlsx`

| Property | Type | Description |
|---|---|---|
| `name` | String (UNIQUE) | Country name |

---

### `Industry`
Represents an industry sector.
Source: derived from `supplychainKG_clean.csv`

| Property | Type | Description | Example |
|---|---|---|---|
| `name` | String (UNIQUE) | Industry name | `"Steel"`, `"Automotive"` |

---

### `Port`
Represents a seaport that experienced a disruption event.
Source: `data/disruption_events/Port-disruption-database.xlsx`

| Property | Type | Description |
|---|---|---|
| `name` | String (UNIQUE) | Port name |
| `country` | String | Country where port is located |
| `source_dataset` | String | `"port_disruption"` |

---

### `DisruptionEvent`
A climate-related or operational event that affected a port.
Source: `data/disruption_events/Port-disruption-database.xlsx`

| Property | Type | Description |
|---|---|---|
| `event_id` | String (UNIQUE) | Internal event ID (`"event_0"` etc.) |
| `event_name` | String | Event name (e.g., Hurricane Harvey) |
| `year` | Integer | Year of event |
| `source_dataset` | String | `"port_disruption"` |

---

### `AnonNode`
Anonymised supply chain node. Used for topological analysis where company names are not needed.
Source: `data/supply_network/nodes_anon.csv`

| Property | Type | Description |
|---|---|---|
| `node_id` | String (UNIQUE) | Original ID (`"n0"`, `"n1"`, …) |
| `location` | String | Country (may be empty) |
| `products` | String | Product(s) associated with this node |
| `source_dataset` | String | `"anonnet"` |

---

## Relationship Types

### `SUPPLIES_TO`
`(Company)-[:SUPPLIES_TO]->(Company)`
Indicates a supplier–customer relationship.
Source: `supplychainKG_clean.csv`

| Property | Description |
|---|---|
| `source_dataset` | `"supplychainKG"` |

**Count**: ~16,640

---

### `LOCATED_IN`
`(Company)-[:LOCATED_IN]->(Country)`
Links a company to its headquarters country.

**Count**: ~6,222

---

### `BELONGS_TO`
`(Company)-[:BELONGS_TO]->(Industry)`
Links a company to its primary industry sector.

**Count**: ~6,222

---

### `CONNECTS_TO`
`(AnonNode)-[:CONNECTS_TO]->(AnonNode)`
Directed edge in the anonymised supply network.
Source: `edges_anon.csv`

| Property | Description |
|---|---|
| `source_dataset` | `"anonnet"` |

**Count**: ~43,926

---

### `PORT_IN`
`(Port)-[:PORT_IN]->(Country)`
Links a port to the country it is located in.

---

### `AFFECTED_BY`
`(Port)-[:AFFECTED_BY]->(DisruptionEvent)`
Links a port to a disruption it experienced.

| Property | Type | Description |
|---|---|---|
| `severity` | Integer | 0 (minimal) to 3 (severe) |
| `total_affected_days` | Float | Total days of impact |

---

## Constraints

```cypher
CREATE CONSTRAINT company_name_unique   IF NOT EXISTS FOR (c:Company)        REQUIRE c.name     IS UNIQUE;
CREATE CONSTRAINT country_name_unique   IF NOT EXISTS FOR (c:Country)        REQUIRE c.name     IS UNIQUE;
CREATE CONSTRAINT industry_name_unique  IF NOT EXISTS FOR (i:Industry)       REQUIRE i.name     IS UNIQUE;
CREATE CONSTRAINT port_name_unique      IF NOT EXISTS FOR (p:Port)           REQUIRE p.name     IS UNIQUE;
CREATE CONSTRAINT anonnode_id_unique    IF NOT EXISTS FOR (a:AnonNode)       REQUIRE a.node_id  IS UNIQUE;
CREATE CONSTRAINT event_id_unique       IF NOT EXISTS FOR (e:DisruptionEvent) REQUIRE e.event_id IS UNIQUE;
```

## Expected Node / Relationship Counts

| Type | Expected Count |
|---|---|
| Company | ~6,222 |
| Country | ~96 |
| Industry | ~24 |
| Port | ~20–30 |
| DisruptionEvent | ~23 |
| AnonNode | 7,245 |
| SUPPLIES_TO | 16,640 |
| LOCATED_IN | ~6,222 |
| BELONGS_TO | ~6,222 |
| CONNECTS_TO | 43,926 |
| PORT_IN | ~20–30 |
| AFFECTED_BY | ~23 |
