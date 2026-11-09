// ═══════════════════════════════════════════════════════════════════════════
//  AtmoGraph – Relationship Import Cypher Templates
//  Reference templates; actual import uses Python scripts with UNWIND.
// ═══════════════════════════════════════════════════════════════════════════

// ── SUPPLIES_TO ───────────────────────────────────────────────────────────────
// (Supplier Company) -[:SUPPLIES_TO]-> (Customer Company)
MATCH (s:Company {name: "Eni SpA"})
MATCH (c:Company {name: "Sonatrach Group"})
MERGE (s)-[r:SUPPLIES_TO]->(c)
ON CREATE SET r.source_dataset = "supplychainKG"
RETURN s.name, type(r), c.name;

// ── LOCATED_IN ────────────────────────────────────────────────────────────────
// (Company) -[:LOCATED_IN]-> (Country)
MATCH (c:Company {name: "Eni SpA"})
MATCH (co:Country {name: "Italy"})
MERGE (c)-[:LOCATED_IN]->(co)
RETURN c.name, co.name;

// ── BELONGS_TO ────────────────────────────────────────────────────────────────
// (Company) -[:BELONGS_TO]-> (Industry)
MATCH (c:Company {name: "Eni SpA"})
MATCH (i:Industry {name: "Oil & Gas Producers"})
MERGE (c)-[:BELONGS_TO]->(i)
RETURN c.name, i.name;

// ── CONNECTS_TO (AnonNet) ─────────────────────────────────────────────────────
// (AnonNode) -[:CONNECTS_TO]-> (AnonNode)
MATCH (s:AnonNode {node_id: "n0"})
MATCH (t:AnonNode {node_id: "n5491"})
MERGE (s)-[r:CONNECTS_TO]->(t)
ON CREATE SET r.source_dataset = "anonnet"
RETURN s.node_id, t.node_id;

// ── PORT_IN ───────────────────────────────────────────────────────────────────
// (Port) -[:PORT_IN]-> (Country)
MATCH (p:Port {name: "Port of Houston"})
MATCH (c:Country {name: "United States"})
MERGE (p)-[:PORT_IN]->(c)
RETURN p.name, c.name;

// ── AFFECTED_BY ───────────────────────────────────────────────────────────────
// (Port) -[:AFFECTED_BY {severity, total_affected_days}]-> (DisruptionEvent)
MATCH (p:Port {name: "Port of Houston"})
MATCH (e:DisruptionEvent {event_id: "event_0"})
MERGE (p)-[r:AFFECTED_BY]->(e)
ON CREATE SET r.severity = 3, r.total_affected_days = 14
RETURN p.name, type(r), e.event_name;

// ── Verify relationship counts ────────────────────────────────────────────────
MATCH ()-[r]->()
WITH type(r) AS type, count(r) AS count
RETURN type, count
ORDER BY count DESC;
