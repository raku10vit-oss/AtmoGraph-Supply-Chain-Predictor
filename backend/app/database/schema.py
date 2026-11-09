"""
AtmoGraph – Database Schema Constants
Centralises node label names and relationship type names
so they can be imported rather than hard-coded as strings.
"""

# ── Node Labels ────────────────────────────────────────────────────────────────
LABEL_COMPANY = "Company"
LABEL_COUNTRY = "Country"
LABEL_INDUSTRY = "Industry"
LABEL_PORT = "Port"
LABEL_DISRUPTION_EVENT = "DisruptionEvent"
LABEL_ANON_NODE = "AnonNode"

ALL_LABELS = [
    LABEL_COMPANY,
    LABEL_COUNTRY,
    LABEL_INDUSTRY,
    LABEL_PORT,
    LABEL_DISRUPTION_EVENT,
    LABEL_ANON_NODE,
]

# ── Relationship Types ─────────────────────────────────────────────────────────
REL_SUPPLIES_TO = "SUPPLIES_TO"
REL_LOCATED_IN = "LOCATED_IN"
REL_BELONGS_TO = "BELONGS_TO"
REL_CONNECTS_TO = "CONNECTS_TO"
REL_AFFECTED_BY = "AFFECTED_BY"
REL_PORT_IN = "PORT_IN"

ALL_RELATIONSHIPS = [
    REL_SUPPLIES_TO,
    REL_LOCATED_IN,
    REL_BELONGS_TO,
    REL_CONNECTS_TO,
    REL_AFFECTED_BY,
    REL_PORT_IN,
]

# ── Property names ─────────────────────────────────────────────────────────────
PROP_NAME = "name"
PROP_COUNTRY = "country"
PROP_INDUSTRY = "industry"
PROP_TYPE = "type"            # Supplier | Customer | Both
PROP_NODE_ID = "node_id"     # AnonNet original id (n0, n1, …)
PROP_LOCATION = "location"
PROP_PRODUCTS = "products"
PROP_SOURCE = "source_dataset"
