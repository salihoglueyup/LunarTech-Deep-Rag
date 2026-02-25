# Multi-Tier Caching Strategy

Performance and cost optimization are critical when dealing with large LLM orchestration. LunarTech Deep RAG implements a multi-tier caching system located in `services/cache_service.py` to drastically reduce API costs and latency.

## How the Cache Works

Whenever a semantic query or smart feature is executed, a unique hash is generated based on:

1. The exact user prompt/input.
2. The specific document context selected.
3. The model parameters being used.

Before making an outbound HTTP request to an LLM provider, the system checks this hash against the cache layers.

### Tier 1: Memory Cache (RAM)

- **Speed**: Instantaneous (< 1ms).
- **Scope**: The current user session.
- **Eviction**: Uses an LRU (Least Recently Used) policy to prevent Streamlit from encountering Out-Of-Memory (OOM) errors.

### Tier 2: Persistent Disk Cache (JSON)

- **Speed**: Extremely fast (< 5ms).
- **Scope**: Global (across server restarts).
- **Format**: Stored safely in `data/cache/llm_cache.json`.

## Performance Impact

Because Handbook Generation (`AgentWrite`) often requires the LLM to reflect on similar pieces of data continuously, caching identical sub-queries reduces the overall API token consumption by up to 40% per handbook.

## Cache Management

Users can manually clear their cache to force fresh LLM generations by clicking the **"Clear Cache"** button located at the bottom of the navigation sidebar.
