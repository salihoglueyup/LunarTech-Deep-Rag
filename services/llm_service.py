"""
LunarTech AI — LLM Service v2
OpenRouter API with retry, cache, timeout, and token tracking.
"""

import os
import sys
import time
import numpy as np
from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from services import cache_service
from utils import logger

# ── Config ──
MAX_RETRIES = 3
RETRY_DELAYS = [1, 3, 8]  # exponential backoff (seconds)
DEFAULT_TIMEOUT = 60  # seconds


def get_client(model: str = None) -> OpenAI:
    """Returns OpenRouter or local Ollama client depending on the model."""
    if model and model.startswith("ollama/"):
        return OpenAI(
            base_url=config.OLLAMA_BASE_URL,
            api_key="ollama",  # Local doesn't need a real key but OpenAI client requires one
            timeout=600,
        )
    return OpenAI(
        base_url=config.OPENROUTER_BASE_URL,
        api_key=config.OPENROUTER_API_KEY,
        timeout=DEFAULT_TIMEOUT,
    )


# ── Token tracking ──
_token_usage = {"prompt": 0, "completion": 0, "total": 0, "calls": 0, "cached": 0}


def get_token_usage() -> dict:
    return dict(_token_usage)


def reset_token_usage():
    global _token_usage
    _token_usage = {"prompt": 0, "completion": 0, "total": 0, "calls": 0, "cached": 0}


# ── Retry wrapper ──
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)


def _is_retryable_error(e: Exception) -> bool:
    err_str = str(e).lower()
    if "401" in err_str or "403" in err_str or "invalid" in err_str:
        logger.error("LLM auth/validation error (no retry)", exc=e)
        return False
    return True


def _before_sleep(retry_state):
    logger.warning(
        f"LLM API retry {retry_state.attempt_number}/{MAX_RETRIES}",
        error=str(retry_state.outcome.exception()),
    )


@retry(
    wait=wait_exponential(multiplier=1, min=1, max=15),
    stop=stop_after_attempt(MAX_RETRIES),
    retry=retry_if_exception_type(Exception),
    before_sleep=_before_sleep,
    reraise=True,
)
def _retry_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        if not _is_retryable_error(e):
            raise
        raise


# ── Core Functions ──


def chat_completion(
    messages: list[dict],
    model: str = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    use_cache: bool = True,
    tools: list = None,
    tool_choice: str = "auto",
):
    """Gets response from LLM (cache + retry). If tools are provided as an array, it may return a raw message object."""
    model = model or config.DEFAULT_MODEL

    # Cache check -> Disable cache if tools are provided (tool calls need active loops)
    if use_cache and temperature <= 0.3 and not tools:
        cached = cache_service.get(messages, model, max_tokens, temperature)
        if cached is not None:
            _token_usage["cached"] += 1
            logger.llm_call(model, cached=True)
            return cached

    # API call with retry
    start = time.time()

    def _call():
        client = get_client(model)

        actual_model = model
        if actual_model.startswith("ollama/"):
            actual_model = actual_model.replace("ollama/", "")

        kwargs = {
            "model": actual_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        return client.chat.completions.create(**kwargs)

    response = _retry_call(_call)
    duration_ms = int((time.time() - start) * 1000)

    # If it's a tool call, return the message object directly
    msg = response.choices[0].message
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        return msg

    result = msg.content or ""

    # Track tokens
    if hasattr(response, "usage") and response.usage:
        _token_usage["prompt"] += response.usage.prompt_tokens or 0
        _token_usage["completion"] += response.usage.completion_tokens or 0
        _token_usage["total"] += response.usage.total_tokens or 0
    _token_usage["calls"] += 1

    logger.llm_call(model, tokens=_token_usage["total"], duration_ms=duration_ms)

    # Cache store (only low-temperature responses & no tools)
    if use_cache and temperature <= 0.3 and not tools:
        cache_service.put(messages, model, max_tokens, temperature, result)

    return result


def stream_completion(
    messages: list[dict],
    model: str = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
):
    """Gets streaming response from LLM (generator)."""
    model = model or config.DEFAULT_MODEL
    _token_usage["calls"] += 1

    def _call():
        client = get_client(model)

        actual_model = model
        if actual_model.startswith("ollama/"):
            actual_model = actual_model.replace("ollama/", "")

        return client.chat.completions.create(
            model=actual_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

    stream = _retry_call(_call)

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# ── Embedding Functions ──


def get_embedding(text: str) -> list[float]:
    """Generates an embedding vector for the text."""

    def _call():
        client = get_client()
        return client.embeddings.create(model=config.EMBEDDING_MODEL, input=text)

    response = _retry_call(_call)
    return response.data[0].embedding


# ── LightRAG Wrappers ──


async def lightrag_llm_func(
    prompt: str,
    system_prompt: str = None,
    history_messages: list = None,
    **kwargs,
) -> str:
    """Async LLM wrapper for LightRAG."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    model = kwargs.get("model", config.DEFAULT_MODEL)
    max_tokens = kwargs.get("max_tokens", 4096)

    return chat_completion(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=0.1,
        use_cache=True,
    )


async def lightrag_embedding_func(texts: list[str], **kwargs) -> np.ndarray:
    """Async embedding wrapper for LightRAG."""

    def _call():
        client = get_client()
        return client.embeddings.create(model=config.EMBEDDING_MODEL, input=batch)

    embeddings = []
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = _retry_call(_call)
        for item in response.data:
            embeddings.append(item.embedding)

    return np.array(embeddings)
