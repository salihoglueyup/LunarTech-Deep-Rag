# System Overview

**LunarTech Deep RAG** is a highly advanced, multi-agent AI operating system designed to process complex documents, generate immense structured handbooks, and run autonomous background tasks.

## High-Level Architecture

The system consists of several interconnected layers working in harmony:

1. **Frontend / UI Layer (Streamlit)**
   - Interactive React-like components using Streamlit.
   - Distinct views: Chat, Handbook Generator, Dashboard, Knowledge Graph, Shadow Agents, Swarm Studio, and Admin Panel.

2. **Core AI Engine (Core/)**
   - `AgentWrite`: Our proprietary implementation of the AgentWrite algorithm capable of generating 20,000+ word structured handbooks.
   - `Shadow Agents`: Background task processors that execute long-running jobs (web scraping, data mining) robustly.
   - `Data Agent`: Text-to-SQL logic for dynamically interacting with external databases via natural language.

3. **Data & Vector Layer (LightRAG)**
   - Powered by Microsoft's LightRAG architecture.
   - Hybrid routing: Combines standard vector embeddings with a comprehensive knowledge graph.
   - Real-time Entity Extraction parsing documents into nodes and edges for 3D visualization.

4. **Service Integration Layer (Services/)**
   - **LLM Service:** Multi-model routing. Gracefully falls back across OpenRouter (Grok, Gemini) and local Ollama integrations.
   - **Supabase Service:** Manages Row Level Security (RLS) authentication, workspace logic, and persistent chatting history.

## Multi-Agent Orchestration

LunarTech transcends simple chat interfaces by allowing users to construct their own pipelines using **Swarm Studio**. Users can chain primitive agents together to accomplish vast, multi-step cognitive objectives.
