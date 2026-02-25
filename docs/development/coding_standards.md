# LunarTech Coding Standards

This repository adheres to strict Python paradigms emphasizing AI operability.

## 1. Directory Structure Standards

- `app/views/`: Strict UI only. No LLM processing should occur here. All functions should trigger `st.rerun()` purely for visual updates.
- `app/components/`: Reusable Streamlit widgets (e.g., sidebars, floating terminals).
- `services/`: Core logic and external API communication.
- `core/`: Prompts and AI algorithm definitions (e.g., AgentWrite logic). No Streamlit logic should exist in `core/`.

## 2. Python Code Style

- Use `Black` for formatting.
- `ruff` is used for linting.
- **Type Annotations**: High-level internal schemas should be defined using Pydantic (e.g., parsing structured AI JSON outputs).
- Avoid `UnboundLocalError`: Explicitly check variables that use conditional `if/else` imports (especially prevalent in Streamlit event loops).

## 3. Localization

The system uses an internal `t()` function located in `app/lang.py`.

- **DO NOT** hardcode English or Turkish strings into Streamlit `st.markdown()` blocks.
- **DO** use: `st.write(t("hello_key"))`.

## 4. Error State Management

Because LLMs are non-deterministic, operations must use graceful fallback loops.
Example (from `llm_service.py`):

```python
try:
    return call_openrouter_grok(messages)
except TimeoutError:
    return call_ollama_local(messages)
```
