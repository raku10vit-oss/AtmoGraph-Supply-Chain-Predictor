// ═══════════════════════════════════════════════════════════════════════════
//  AtmoGraph – Node Import Cypher Templates
//
//  These are reference templates for the node import steps.
//  The Python import scripts (backend/scripts/) use the same logic
//  but with UNWIND batching for performance.
//
//  To use in Neo4j Browser (replace <values> with actual data):
// ═══════════════════════════════════════════════════════════════════════════

// ── Country node ─────────────────────────────────────────────────────────────
MERGE (c:Country {name: "Japan"})
RETURN c;

// ── Industry node ─────────────────────────────────────────────────────────────
MERGE (i:Industry {name: "Automotive"})
RETURN i;

// ── Company node (Supplier role) ─────────────────────────────────────────────
MERGE (c:Company {name: "Toyota Motor Corporation"})
ON CREATE SET
  c.country        = "Japan",
  c.industry       = "Automotive",
  c.type           = "Supplier",
  c.source_dataset = "supplychainKG"
RETURN c;

// ── Company node (Customer role) ─────────────────────────────────────────────
MERGE (c:Company {name: "Example Customer Co"})
ON CREATE SET
  c.country        = "United States",
  c.industry       = "Electronics",
  c.type           = "Customer",
  c.source_dataset = "supplychainKG"
RETURN c;

// ── AnonNode ─────────────────────────────────────────────────────────────────
MERGE (a:AnonNode {node_id: "n0"})
ON CREATE SET
  a.location       = "Japan",
  a.products       = "Fertilizer",
  a.source_dataset = "anonnet"
RETURN a;

// ── Port node ─────────────────────────────────────────────────────────────────
MERGE (p:Port {name: "Port of Houston"})
ON CREATE SET
  p.country        = "United States",
  p.source_dataset = "port_disruption"
RETURN p;

// ── DisruptionEvent node ─────────────────────────────────────────────────────
MERGE (e:DisruptionEvent {event_id: "event_0"})
ON CREATE SET
  e.event_name     = "Hurricane Harvey",
  e.year           = 2017,
  e.source_dataset = "port_disruption"
RETURN e;

// ── Batch import template (for large datasets) ───────────────────────────────
// UNWIND $rows AS row
// MERGE (c:Company {name: row.name})
// ON CREATE SET c.country = row.country, c.industry = row.industry, c.type = row.role
