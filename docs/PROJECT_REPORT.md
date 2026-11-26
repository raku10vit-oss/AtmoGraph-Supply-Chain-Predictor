# AtmoGraph – Supply Chain Ripple Effect Predictor

## 1. Introduction

AtmoGraph is an AI-powered supply chain risk prediction system designed to identify how disruptions in one part of a supply chain can affect other connected companies and industries.

The project uses graph database technology to represent relationships between companies, suppliers, industries, countries and ports. It analyses these connections to understand how disruptions can spread through the supply chain network.

## 2. Problem Statement

Traditional supply chain systems often analyse companies and suppliers independently. They may fail to identify how a disruption affecting one supplier, port or country can impact other connected businesses.

AtmoGraph aims to address this problem by representing the supply chain as an interconnected graph and analysing the possible ripple effects of disruptions.

## 3. Project Objectives

- Develop a graph-based supply chain representation.
- Store and manage company and supplier relationships.
- Identify important companies and connections in the supply chain.
- Analyse potential supply chain disruptions.
- Calculate risk scores for connected companies.
- Visualise supply chain networks and disruption risks through an interactive dashboard.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and backend logic |
| Neo4j | Graph database |
| Cypher | Graph database queries |
| FastAPI | Backend API development |
| React | Frontend development |
| Vite | Frontend development environment |
| React Flow | Graph visualisation |
| NetworkX | Graph analysis |

## 5. System Architecture

The system consists of the following major components:

1. Data Sources: Supply chain datasets containing company and relationship information.
2. Data Processing: Python scripts process and prepare the data.
3. Graph Database: Neo4j stores companies, countries, industries, ports and their relationships.
4. Backend: FastAPI provides endpoints to access graph information and prediction results.
5. Frontend: React provides an interactive dashboard for exploring supply chain networks and risks.

## 6. Database Design

AtmoGraph uses Neo4j, a graph database, to represent supply chain relationships.

The database contains node types such as:

- Company
- Country
- Industry
- Port
- DisruptionEvent
- AnonNode

Relationships represent connections such as SUPPLIES_TO, LOCATED_IN, BELONGS_TO, PORT_IN and AFFECTED_BY.

This structure helps analyse connections between different entities in a supply chain.

## 7. Disruption Prediction Methodology

The Week 2 architecture describes a weighted risk-scoring approach using five factors:

- Port Exposure – 30%
- Supplier Concentration – 25%
- Graph Centrality – 20%
- Industry Vulnerability – 15%
- Network Propagation – 10%

These factors are combined to calculate an overall supply chain risk score.

The approach helps identify companies that may be vulnerable to disruptions in connected parts of the supply chain.

## 8. Conclusion

AtmoGraph aims to improve supply chain risk analysis by combining graph database technology, backend APIs, graph analysis and interactive visualisation.

The project provides a structured way to understand supply chain connections and investigate how disruptions may affect connected businesses.

*Note: This is an initial project report draft and will be expanded after reviewing the complete implementation and testing results.*
