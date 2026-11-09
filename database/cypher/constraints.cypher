// ═══════════════════════════════════════════════════════════════════════════
//  AtmoGraph – Neo4j Constraints & Indexes
//  Run these once against your database before importing any data.
//
//  In Neo4j Browser: paste and run each block separately.
//  In cypher-shell:  cypher-shell -f database/cypher/constraints.cypher
// ═══════════════════════════════════════════════════════════════════════════

// ── Unique constraints ───────────────────────────────────────────────────────
// These also create an implicit index on the constrained property.

CREATE CONSTRAINT company_name_unique IF NOT EXISTS
  FOR (c:Company) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT country_name_unique IF NOT EXISTS
  FOR (c:Country) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT industry_name_unique IF NOT EXISTS
  FOR (i:Industry) REQUIRE i.name IS UNIQUE;

CREATE CONSTRAINT port_name_unique IF NOT EXISTS
  FOR (p:Port) REQUIRE p.name IS UNIQUE;

CREATE CONSTRAINT anonnode_id_unique IF NOT EXISTS
  FOR (a:AnonNode) REQUIRE a.node_id IS UNIQUE;

CREATE CONSTRAINT event_id_unique IF NOT EXISTS
  FOR (e:DisruptionEvent) REQUIRE e.event_id IS UNIQUE;

// ── Additional indexes for common lookups ────────────────────────────────────

CREATE INDEX company_country_idx IF NOT EXISTS
  FOR (c:Company) ON (c.country);

CREATE INDEX company_industry_idx IF NOT EXISTS
  FOR (c:Company) ON (c.industry);

CREATE INDEX company_type_idx IF NOT EXISTS
  FOR (c:Company) ON (c.type);

CREATE INDEX anonnode_location_idx IF NOT EXISTS
  FOR (a:AnonNode) ON (a.location);

CREATE INDEX disruption_year_idx IF NOT EXISTS
  FOR (e:DisruptionEvent) ON (e.year);

// Verify: SHOW CONSTRAINTS;
//         SHOW INDEXES;
