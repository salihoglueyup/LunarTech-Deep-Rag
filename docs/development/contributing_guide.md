# Contributing to LunarTech Deep RAG

We welcome contributions! As LunarTech is built to be a robust, modular AI operating system, there are plenty of avenues for enhancement: from writing new Agent tools to creating entirely new smart features.

## Getting Started

1. Fork the repository.
2. Clone your forked repository locally.
3. Follow the `setup/installation.md` guide to spin up the Streamlit interface.

## Project Structure

- `app/`: Frontend Streamlit logic (components, views).
- `core/`: The "Brain". Heavy LLM orchestration logic like AgentWrite, Swarm Studio, and Smart Features.
- `services/`: IO bounds. LLM routing, Database interaction, caching, and text extraction.
- `data/`: Local storage for the LightRAG engine and SQLite databases.

## Pull Request Guidelines

- Ensure your code follows PEP-8 standards.
- If you are adding a new model integration, make sure properly handle `TimeoutError` and rate-limit fallbacks inside `services/llm_service.py`.
- Do not commit `.env` or any `lightrag_workspace` graph files.

## Adding a "Smart Feature"

If you want to add a feature (e.g., "Code Reviewer" or "Poem Writer"):

1. Write the prompt orchestrator in `core/smart_features.py`.
2. Map the new orchestrator to a UI button in `app/views/ai_tools.py`.
3. Add English translations to `app/lang.py`.
