"""
LunarTech AI - LightRAG Service
Knowledge Graph based RAG engine management.
"""

import os
import sys
import asyncio
import threading
from typing import Optional, Dict

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

try:
    from lightrag import LightRAG, QueryParam
    from lightrag.utils import EmbeddingFunc
    from lightrag.llm.openai import openai_complete_if_cache
    from openai import AsyncOpenAI
    import numpy as np

    LIGHTRAG_AVAILABLE = True
except ImportError:
    LIGHTRAG_AVAILABLE = False


# ── Singleton RAG Instance ────────────────────────────────

_rag_instance: "LightRAG" = None
_llm_lock = None


async def _custom_llm_func(
    prompt: str,
    system_prompt: str = None,
    history_messages: list = None,
    keyword_extraction: bool = False,
    **kwargs,
) -> str:
    """Asynchronous LLM Engine featuring Google Gemini 5RPM Rate Limiter for LightRAG."""
    global _llm_lock
    import asyncio

    if _llm_lock is None:
        _llm_lock = asyncio.Lock()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    try:
        # If Gemini Model is used (Connect directly to Google API / Completely Free)
        if "gemini" in config.DEFAULT_MODEL.lower() and getattr(
            config, "GEMINI_API_KEY", ""
        ):
            client = AsyncOpenAI(
                api_key=config.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            # Remove 'google/' prefix in OpenRouter format (for native OpenAI compatibility)
            actual_model = config.DEFAULT_MODEL.replace("google/", "")
        elif "ollama" in config.DEFAULT_MODEL.lower():
            # Connect to Fully Local Ollama Engine (Zero Network Traffic, Unlimited Limit)
            client = AsyncOpenAI(
                api_key="ollama",  # Ollama doesn't require an API key, sent as a dummy
                base_url=getattr(
                    config, "OLLAMA_BASE_URL", "http://localhost:11434/v1"
                ),
            )
            actual_model = config.DEFAULT_MODEL.replace("ollama/", "")
        else:
            # Standard OpenRouter connection for other models (Grok, Claude, etc.)
            client = AsyncOpenAI(
                api_key=config.OPENROUTER_API_KEY, base_url=config.OPENROUTER_BASE_URL
            )
            actual_model = config.DEFAULT_MODEL

        # ── GEMINI 5RPM Free Tier Throttling (Global Lock) ──
        if "gemini" in config.DEFAULT_MODEL.lower() and getattr(
            config, "GEMINI_API_KEY", ""
        ):
            async with _llm_lock:
                print(
                    "⏳ Gemini Rate Limiter (Lock Acquired): Waiting 13 seconds to bypass 5RPM quota..."
                )
                await asyncio.sleep(13)
                response = await client.chat.completions.create(
                    model=actual_model,
                    messages=messages,
                    temperature=kwargs.get("temperature", 0.0),
                    top_p=kwargs.get("top_p", 1.0),
                    max_tokens=kwargs.get("max_tokens", 4096),
                )
        elif "ollama" in config.DEFAULT_MODEL.lower():
            # Ollama (Local GPU/CPU):
            # To prevent the model from processing 4-5 giant texts at once and crashing the computer or getting a Timeout,
            # we queue the processes with a Lock. It never has a quota, but it has a hardware limit.
            async with _llm_lock:
                print(f"🧠 Local Ollama Task: Generating with {actual_model}...")
                response = await client.chat.completions.create(
                    model=actual_model,
                    messages=messages,
                    temperature=kwargs.get("temperature", 0.0),
                    top_p=kwargs.get("top_p", 1.0),
                    max_tokens=kwargs.get("max_tokens", 4096),
                )
        else:
            response = await client.chat.completions.create(
                model=actual_model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.0),
                top_p=kwargs.get("top_p", 1.0),
                max_tokens=kwargs.get("max_tokens", 4096),
            )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM API Error (Gemini/OpenRouter Bypass): {str(e)}")
        raise e


# To load the Local Embedding model only when necessary
_embedding_model = None
_embedding_executor = None


async def _custom_embedding_func(texts: list[str], **kwargs):
    """Local CPU-based embedding function for LightRAG."""
    global _embedding_model, _embedding_executor
    import asyncio
    import concurrent.futures

    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer

        print(f"Loading local embedding model: {config.EMBEDDING_MODEL} (384d)...")
        _embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)

    if _embedding_executor is None:
        _embedding_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    try:
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            _embedding_executor,
            lambda: _embedding_model.encode(texts, show_progress_bar=False),
        )
        return np.array(embeddings)
    except Exception as e:
        print(f"Local Embedding Error: {str(e)}")
        raise e


_rag_instance = None


def get_rag() -> "LightRAG":
    """
    Returns the LightRAG instance.
    Thanks to the background thread, we can use a single singleton LightRAG object.
    """
    global _rag_instance
    if _rag_instance is not None:
        return _rag_instance

    if not LIGHTRAG_AVAILABLE:
        raise ImportError(
            "lightrag-hku library is not installed. pip install lightrag-hku"
        )

    os.makedirs(config.LIGHTRAG_WORK_DIR, exist_ok=True)

    kwargs = {}
    if hasattr(config, "SUPABASE_DB_URL") and config.SUPABASE_DB_URL:
        import urllib.parse

        parsed_url = urllib.parse.urlparse(config.SUPABASE_DB_URL)

        os.environ["POSTGRES_USER"] = parsed_url.username or "postgres"
        os.environ["POSTGRES_PASSWORD"] = parsed_url.password or ""
        os.environ["POSTGRES_HOST"] = parsed_url.hostname or ""
        os.environ["POSTGRES_PORT"] = str(parsed_url.port or 5432)
        os.environ["POSTGRES_DATABASE"] = parsed_url.path.lstrip("/") or "postgres"

        kwargs["kv_storage"] = "PGKVStorage"
        kwargs["vector_storage"] = "PGVectorStorage"
        kwargs["doc_status_storage"] = "PGDocStatusStorage"

    emb_func = EmbeddingFunc(
        func=_custom_embedding_func,
        embedding_dim=config.EMBEDDING_DIM,
        max_token_size=8192,
    )
    setattr(emb_func, "model_name", "lunar_vectordb")

    _rag_instance = LightRAG(
        working_dir=config.LIGHTRAG_WORK_DIR,
        llm_model_func=_custom_llm_func,
        embedding_func=emb_func,
        chunk_token_size=9000,
        **kwargs,
    )
    return _rag_instance


# Background loop for all DB/async operations to prevent Streamlit threading conflicts
_loop = None
_thread = None


def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def _get_background_loop():
    global _loop, _thread
    if _loop is None:
        _loop = asyncio.new_event_loop()
        _thread = threading.Thread(
            target=_start_background_loop, args=(_loop,), daemon=True
        )
        _thread.start()
    return _loop


def _run_async(coro):
    """Safely runs any asynchronous function in the background thread."""
    loop = _get_background_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


# Storage initialization flag
_rag_initialized = False


def reset_rag():
    """Resets the RAG state."""
    global _rag_initialized
    _rag_initialized = False


# ── Document Operations ───────────────────────────────────


async def _ensure_initialized_async(rag):
    global _rag_initialized
    if not _rag_initialized:
        try:
            if hasattr(rag, "initialize_storages"):
                await rag.initialize_storages()
        except Exception as e:
            print(f"Bypass Storage Init Error (non-critical): {e}")
        _rag_initialized = True


def _ensure_initialized(rag):
    _run_async(_ensure_initialized_async(rag))


async def _insert_async(text: str):
    """Inserts the document text into LightRAG asynchronously."""
    rag = get_rag()
    await _ensure_initialized_async(rag)
    await rag.ainsert(text)


def insert_document(text: str):
    """
    Inserts the document text into LightRAG.
    Entities and relations are automatically extracted.

    Args:
        text: The full text of the document
    """
    _run_async(_insert_async(text))


async def _query_async(question: str, mode: str = "hybrid") -> str:
    """Async query."""
    rag = get_rag()
    await _ensure_initialized_async(rag)
    return await rag.aquery(
        question,
        param=QueryParam(mode=mode),
    )


def query(question: str, mode: str = "hybrid") -> str:
    """
    Performs a query over the LightRAG Knowledge Graph.

    Args:
        question: User query
        mode: Query mode - "local", "global", "hybrid", "naive"
            - local: Detailed, specific answers
            - global: Overview, broad topics
            - hybrid: Combination of both (recommended)
            - naive: Simple vector search (fallback)

    Returns:
        The response generated by the LLM
    """
    return _run_async(_query_async(question, mode))


def get_context(question: str) -> str:
    """
    Retrieves the context for a question (for the chat service).
    Gathers both local and global information using hybrid mode.
    """
    try:
        return query(question, mode="hybrid")
    except Exception as e:
        return f"Failed to retrieve context: {str(e)}"


def is_initialized() -> bool:
    """Checks if LightRAG contains any data."""
    work_dir = config.LIGHTRAG_WORK_DIR
    if not os.path.exists(work_dir):
        return False

    # Check the files created by LightRAG
    expected_files = ["graph_chunk_entity_relation.graphml"]
    for f in expected_files:
        if os.path.exists(os.path.join(work_dir, f)):
            return True

    return False
