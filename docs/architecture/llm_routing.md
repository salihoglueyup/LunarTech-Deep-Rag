# Intelligent LLM Routing

Given the unstable nature of external LLM APIs (especially during peak hours), LunarTech Deep RAG uses a robust routing and fallback mechanism defined in `services/llm_service.py`.

## The Routing Pipeline

When a component requests an LLM completion via `chat_completion()`, the request does not go straight to a single provider. It enters the router:

### 1. Primary Model (e.g., Grok 2)

The system attempts to contact OpenRouter for the primary requested model (usually `x-ai/grok-2-1212`).
If this succeeds, the response is returned immediately.

### 2. Tier 1 Fallback (e.g., Gemini Flash)

If the primary model returns a `529` (Overloaded), `429` (Rate Limited), or `TimeoutError`, the router automatically degrades the request gracefully to a faster, highly-available model like `google/gemini-2.5-flash` via OpenRouter.

### 3. Tier 2 Fallback (Native Gemini)

If OpenRouter as a whole is down or unreachable, the system completely bypasses OpenRouter and attempts to connect directly to Google's Native Generative AI API using `GEMINI_API_KEY`.

### 4. Ultimate Fallback (Local Ollama)

If all cloud providers fail, or the server loses internet connection entirely, the router dynamically points the request to `http://localhost:11434` (Ollama) and attempts to resolve the completion using a local model like `llama3.1` or `qwen2.5`.

## Why this matters?

This 4-tier system guarantees **five nines (99.999%) of uptime** for local users. The background workers (Shadow Agents) can run overnight without failing due to temporary API outages.
