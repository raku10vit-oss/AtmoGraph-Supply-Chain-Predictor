// ═══════════════════════════════════════════════════════════════════════════
//  AtmoGraph – Schema Documentation Queries
//  Run these in Neo4j Browser to explore the schema at any time.
// ═══════════════════════════════════════════════════════════════════════════

// ── 1. Full schema overview ──────────────────────────────────────────────────
CALL db.schema.visualization();

// ── 2. All node labels and counts ───────────────────────────────────────────
MATCH (n)
WITH labels(n)[0] AS label, count(n) AS count
RETURN label, count
ORDER BY count DESC;

// ── 3. All relationship types and counts ─────────────────────────────────────
MATCH ()-[r]->()
WITH type(r) AS type, count(r) AS count
RETURN type, count
ORDER BY count DESC;

// ── 4. Node label property examples ─────────────────────────────────────────
MATCH (c:Company) RETURN c LIMIT 3;
MATCH (c:Country) RETURN c LIMIT 3;
MATCH (i:Industry) RETURN i LIMIT 3;
MATCH (p:Port) RETURN p LIMIT 3;
MATCH (e:DisruptionEvent) RETURN e LIMIT 3;
MATCH (a:AnonNode) RETURN a LIMIT 3;

// ── 5. Supply chain sample paths ─────────────────────────────────────────────
// 2-hop supply chain: who supplies whom who supplies whom
MATCH path = (:Company)-[:SUPPLIES_TO]->(:Company)-[:SUPPLIES_TO]->(:Company)
RETURN path LIMIT 5;

// ── 6. Top 10 suppliers by out-degree ────────────────────────────────────────
MATCH (c:Company)-[:SUPPLIES_TO]->()
WITH c.name AS supplier, c.country AS country, count(*) AS customers
ORDER BY customers DESC
LIMIT 10
RETURN supplier, country, customers;

// ── 7. Industry supply links summary ─────────────────────────────────────────
MATCH (s:Company)-[:SUPPLIES_TO]->(c:Company)
WHERE s.industry IS NOT NULL AND c.industry IS NOT NULL
WITH s.industry AS from_industry, c.industry AS to_industry, count(*) AS links
ORDER BY links DESC
LIMIT 15
RETURN from_industry, to_industry, links;

// ── 8. Port disruption by severity ───────────────────────────────────────────
MATCH (p:Port)-[r:AFFECTED_BY]->(e:DisruptionEvent)
RETURN p.name AS port, e.event_name AS event, r.severity AS severity,
       r.total_affected_days AS days_affected
ORDER BY r.total_affected_days DESC;
