# Internal Service API Reference

Currently, LunarTech Deep RAG operates primarily through the Streamlit web framework, bypassing traditional HTTP REST endpoints in favor of direct Python function calls for maximum speed and zero network latency.

If you are looking to decouple the frontend from the backend, you can hook into the following core functions found in `services/` and `core/`:

### 1. `document_processor.py`

`process_to_chunks(file_obj, filename)`

- Extracts text from PDF/DOCX/MD.
- Validates minimum token counts.
- Stores directly into the LightRAG Graph.

### 2. `llm_service.py`

`chat_completion(messages, model, temperature)`

- The core orchestrator.
- Input a list of messages (OpenAI format).
- Will automatically attempt to route through:
  1. OpenRouter (Grok 2)
  2. OpenRouter (Gemini Flash)
  3. Native Google Generative AI (Gemini 2.0 Flash)
  4. Local Ollama Fallback.

### 3. `supabase_service.py`

Data manipulation.

- `get_documents(user_id)`
- `save_document(filename, page_count, chunk_count, user_id)`
- `get_chat_history(user_id)`
- `save_chat_message(role, content, user_id)`
