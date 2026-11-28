# AtmoGraph – Database Schema

## 1. Introduction

AtmoGraph uses Neo4j, a graph database, to store and manage supply chain information. It represents companies, suppliers, countries, industries and ports as connected entities.

## 2. Graph Database Components

A graph database consists of three main components:

- **Nodes:** Represent entities such as companies, countries and ports.
- **Relationships:** Represent connections between different entities.
- **Properties:** Store additional information about nodes and relationships.

## 3. Node Types

The AtmoGraph database includes the following node types:

| Node | Description |
|---|---|
| Company | Represents a company in the supply chain. |
| Country | Represents the country associated with an entity. |
| Industry | Represents the industry of a company. |
| Port | Represents a shipping port. |
| DisruptionEvent | Represents a supply chain disruption event. |
| AnonNode | Represents an anonymised supply-chain network entity. |

## 4. Relationship Types

| Relationship | Description |
|---|---|
| SUPPLIES_TO | Connects a supplier company to another company. |
| LOCATED_IN | Connects a company to a country. |
| BELONGS_TO | Connects a company to an industry. |
| CONNECTS_TO | Connects anonymised network entities. |
| PORT_IN | Connects a port to a country. |
| AFFECTED_BY | Connects a port to a disruption event. |

## 5. Importance of Graph Database

Neo4j helps represent complex supply chain connections. It allows the system to explore supplier relationships, identify connected companies and analyse how disruptions may affect different parts of the supply chain.

## 6. Conclusion

The Neo4j database provides the foundation for the AtmoGraph platform. Its graph-based structure makes it easier to understand supply chain dependencies and supports further graph analysis and disruption risk assessment.
