# Changelog

All notable changes to **LunarTech Deep RAG** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - AI Operating System Update

*(Internal Codename: Level 13)*

### Added

- **Shadow Agents**: Asynchronous background workers detached from the Streamlit UI event loop allowing long tasks to run continuously.
- **Swarm Studio**: A multi-agent chaining UI to string disparate prompt engines into sequential pipelines.
- **4-Tier LLM Routing**:
  - Primary: OpenRouter (Grok 2)
  - Secondary: OpenRouter (Gemini Flash)
  - Tertiary: Google Generative AI Native (Gemini 2.0 Flash)
  - Fallback: Local Offline Ollama Runtime
- **Interactive Canvas**: Parallel split-screen UI for generating outputs alongside chatting.
- **Enterprise Localization**: 100% of Turkish strings removed, converting the interface globally to English.

### Changed

- Refactored `st.session_state` management to prevent `StreamlitAPIException` during callback-heavy workflows in the Chat View.
- Abstracted `AgentWrite` handbook generator logic to prevent memory leaking on 20,000+ word tasks.

## [1.1.0] - Hybrid Database Switch

*(Internal Codename: Level 7)*

### Added

- **LightRAG Graph DB**: Integrated Microsoft's LightRAG framework substituting standard FAISS/ChromaDB similarity search.
- Integrated Echarts 3D Visualizer to view graph nodes and edges.
- Added Supabase RLS (Row Level Security) for `documents` and `chat_history`.

## [1.0.0] - Initial Release

### Added

- Core Streamlit chat interface.
- Basic PDF document parsing (PyPDF).
- Initial OpenAI format chat integrations.
