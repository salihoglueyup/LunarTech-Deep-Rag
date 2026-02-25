# 🗺️ LunarTech Roadmap

LunarTech Deep RAG has evolved rapidly from a basic chat interface to a full-fledged agentic AI operating system (Level 13). However, the journey does not stop here.

This document outlines the planned trajectory for future development.

## 🟢 Phase 1: Near-Term Expansions (Current Focus)

- **Tool Integration for Swarm Studio:** Allow users to define API webhooks directly in the UI for Custom Agents to trigger external enterprise systems (Slack, Jira, Salesforce).
- **Docker Compose Profiles:** Release official `docker-compose.yml` templates for 1-click enterprise deployment linking Supabase local and Ollama instances.
- **Audio Out/Voice Modalities:** Integrate real-time text-to-speech API bindings in the Chat Interface, allowing the AI to "read aloud" complex graph summaries.

## 🟡 Phase 2: Medium-Term Ecosystem

- **Visual Analytics Dashboard:** Expand the Admin Panel to include Token Usage per user per month limits, connecting to a Stripe billing logic layer for SaaS setups.
- **Deep Web Crawling Shadow Agent:** Upgrade the Shadow Agents to utilize headless Playwright, allowing them to login to websites securely and scrape gated data.
- **Hybrid Local Embeddings:** Transition completely off cloud embeddings (OpenAI `text-embedding-3-small`) to purely local ONNX models (`nomic-embed-text`) to guarantee 100% offline data sovereignty.

## 🔴 Phase 3: Long-Term Horizons ("Level 15+")

- **Self-Healing Python Agents:** Agents that can write Python scripts, execute them locally in a secure sandbox, read the standard error (`stderr`), and re-write the code until the script succeeds.
- **Multi-Player Canvas:** Real-time collaboration (like Google Docs) where multiple human users and multiple AI Swarms edit the same `AgentWrite` handbook concurrently.
- **Native Desktop App:** Wrap the Streamlit/FastAPI architecture in an Electron or Tauri shell to distribute LunarTech as an executable `.exe` / `.dmg` native application.

---

*Note: The roadmap is subject to change based on community feedback and advancements in local LLM inference speeds.*
