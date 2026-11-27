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

## 8. Testing and Validation

Testing and validation are important parts of the AtmoGraph project to ensure that the system components work as expected.

The project includes a Week 2 integration test script named `test_week2.py`, containing 17 test cases according to the system architecture documentation.

### 8.1 Testing Areas

The following areas are important for validating the system:

1. **Database Connectivity:** Verify the connection between the application and Neo4j.
2. **Graph Data Validation:** Check whether company nodes and supplier relationships are available.
3. **API Testing:** Verify that backend API endpoints return the expected responses.
4. **Risk Score Validation:** Check whether the weighted risk-scoring methodology produces scores within the expected range of 0 to 1.
5. **Disruption Analysis:** Verify the identification of affected companies and connected supply-chain entities.
6. **Frontend Validation:** Check whether the dashboard displays graph information and prediction results correctly.

### 8.2 Expected Outcomes

- Successful communication between the backend and Neo4j database.
- Correct retrieval of graph information.
- Valid API responses.
- Risk scores within the defined range.
- Proper display of disruption information on the dashboard.

### 8.3 Validation Status

Actual test execution results, including passed tests, failed tests and observations, should be recorded after running the test suite.

No test results are assumed in this section.

## 9. Conclusion

AtmoGraph – Supply Chain Ripple Effect Predictor aims to provide an intelligent approach to identifying and analysing supply chain disruptions. By combining graph database technology, Python-based data processing, graph analysis and interactive visualisation, the system helps understand how a disruption in one part of the supply chain can affect other connected businesses.

The project uses Neo4j to represent relationships between companies and suppliers, while graph analytics and weighted risk-scoring techniques help identify potentially vulnerable entities. The backend and frontend components provide a way to process, access and visualise supply chain information.

Through this project, we gained an understanding of graph databases, supply chain networks, risk analysis, API integration and system architecture.

Overall, AtmoGraph demonstrates how data-driven technologies can support better supply chain risk assessment and decision-making. Future improvements can include advanced machine learning models, real-time news analysis and more accurate disruption predictions.
