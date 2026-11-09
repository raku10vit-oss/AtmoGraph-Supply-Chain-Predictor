# AtmoGraph-Supply-Chain-Predictor
AI-powered supply chain disruption prediction using Graph Neural Networks, NLP, and Neo4j
# AtmoGraph – Supply Chain Ripple Effect Predictor

## 1. Project Overview

AtmoGraph is an AI-powered supply chain risk prediction system designed to identify and predict how disruptions in one part of the global supply chain can affect other connected industries, businesses, and regions.

Traditional supply chain monitoring systems often analyse individual events separately. AtmoGraph aims to understand the complex relationships between suppliers, manufacturers, ports, shipping routes, and industries using Graph Neural Networks (GNNs).

By combining Natural Language Processing (NLP), Graph Databases, and Machine Learning, the system will analyse disruption-related information and estimate its potential impact across the supply chain.

## 2. Problem Statement

Global supply chains are highly interconnected. A disruption such as a port strike, natural disaster, political conflict, or shortage of raw materials can create delays across multiple industries and geographical regions.

Traditional predictive models often struggle to capture these complex relationships and multi-level dependencies.

AtmoGraph addresses this challenge by modelling global supply chains as interconnected graphs and predicting the possible ripple effects of disruptions.

## 3. Project Objectives

- Build an interconnected supply chain graph.
- Identify supply chain disruptions from news and text data.
- Extract relevant entities using NLP techniques.
- Map identified disruptions to the graph database.
- Develop a Graph Neural Network to estimate downstream supply chain risks and delays.
- Visualise affected companies, suppliers, routes, and industries.
- Provide future risk forecasts for 30, 60, and 90 days.

## 4. Key Features

1. **Supply Chain Graph:** Represents suppliers, manufacturers, products, ports, and transportation routes.
2. **News Intelligence:** Processes disruption-related news using NLP.
3. **Entity Recognition:** Identifies important companies, locations, industries, and events.
4. **Risk Detection:** Updates risk information for affected graph nodes.
5. **Ripple Effect Prediction:** Uses Graph Neural Networks to estimate the impact of disruptions across multiple connected nodes.
6. **Interactive Dashboard:** Displays the supply chain network and affected entities.
7. **Future Risk Forecasting:** Provides 30/60/90-day predicted risk and delay estimates.

## 5. Technology Stack

### Backend
- Python
- FastAPI
- Neo4j
- Cypher Query Language

### Natural Language Processing
- spaCy
- HuggingFace Transformers

### Machine Learning
- PyTorch
- PyTorch Geometric
- Graph Neural Networks

### Frontend
- React.js
- D3.js / React Flow
- JavaScript

### Communication
- REST APIs
- WebSockets

## 6. System Architecture

The proposed system follows this workflow:

1. News and disruption-related data are collected.
2. The NLP engine processes the text and extracts relevant entities.
3. Extracted entities are matched with existing supply chain nodes.
4. Neo4j stores the interconnected supply chain network and disruption information.
5. The Graph Neural Network analyses graph relationships and estimates downstream risks.
6. FastAPI communicates predictions to the frontend.
7. The React dashboard displays the affected network, risk levels, and forecast information.

## 7. Development Roadmap

### Week 1 – Graph Foundations
- Set up Neo4j.
- Design the supply chain graph schema.
- Create sample suppliers, manufacturers, ports, and shipping routes.
- Develop the initial React dashboard.
- Visualise the basic supply chain network.

### Week 2 – NLP Pipeline
- Develop the news ingestion pipeline.
- Implement Named Entity Recognition (NER).
- Extract disruption-related information.
- Update corresponding graph nodes in Neo4j.
- Integrate graph data with the frontend.

### Week 3 – GNN Engineering
- Prepare graph-based training data.
- Develop the Graph Neural Network.
- Train the model to estimate downstream delays and risks.
- Visualise predicted risk levels in the dashboard.

### Week 4 – Real-Time Integration
- Integrate the backend and frontend.
- Implement WebSocket communication.
- Display updated risk predictions.
- Add 30/60/90-day forecast visualisation.
- Test and refine the complete system.

## 8. Expected Outcome

The expected outcome is an interactive AI-powered supply chain risk management platform that can analyse disruption-related information, identify connected entities, and estimate how disruptions may propagate through a global supply chain.

The system aims to help logistics managers identify potential risks earlier and make better-informed decisions about supply chain operations and alternative transportation routes.

## 9. Project Status

**Current Phase:** Initial Development

The project is currently in the graph foundation and system setup stage.

Further development, model training, integration, and evaluation will be carried out according to the development roadmap.

---

**Project Name:** AtmoGraph – Supply Chain Ripple Effect Predictor

**Domain:** Artificial Intelligence / Machine Learning / Supply Chain Analytics

**Repository:** AtmoGraph-Supply-Chain-Predictor
