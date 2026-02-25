"""
LunarTech AI — Cache Service
LRU memory + disk cache for LLM responses.
"""

import hashlib
import json
import os
import time
from functools import lru_cache
from collections import OrderedDict

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# ── In-memory LRU cache ──
_memory_cache = OrderedDict()
MAX_MEMORY = 100  # son 100 sorgu hafızada
CACHE_TTL = 3600  # 1 saat


def _make_key(messages: list, model: str, max_tokens: int, temperature: float) -> str:
    """Cache key oluşturur (SHA256 hash)."""
    payload = json.dumps(
        {
            "messages": messages,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def get(
    messages: list, model: str, max_tokens: int = 4096, temperature: float = 0.7
) -> str | None:
    """Cache'den yanıt getir. Yoksa None döner."""
    key = _make_key(messages, model, max_tokens, temperature)

    # 1. Memory cache
    if key in _memory_cache:
        entry = _memory_cache[key]
        if time.time() - entry["ts"] < CACHE_TTL:
            _memory_cache.move_to_end(key)
            return entry["value"]
        else:
            del _memory_cache[key]

    # 2. Disk cache
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                entry = json.load(f)
            if time.time() - entry["ts"] < CACHE_TTL:
                _memory_cache[key] = entry
                _trim_memory()
                return entry["value"]
            else:
                os.remove(path)
        except Exception:
            pass

    return None


def put(messages: list, model: str, max_tokens: int, temperature: float, value: str):
    """Yanıtı cache'e yaz."""
    key = _make_key(messages, model, max_tokens, temperature)
    entry = {"value": value, "ts": time.time(), "model": model}

    # Memory
    _memory_cache[key] = entry
    _trim_memory()

    # Disk
    try:
        path = os.path.join(CACHE_DIR, f"{key}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
    except Exception:
        pass


def _trim_memory():
    """Memory cache'i MAX_MEMORY sınırına indir."""
    while len(_memory_cache) > MAX_MEMORY:
        _memory_cache.popitem(last=False)


def clear():
    """Tüm cache'i temizle."""
    global _memory_cache
    _memory_cache = OrderedDict()
    for f in os.listdir(CACHE_DIR):
        try:
            os.remove(os.path.join(CACHE_DIR, f))
        except Exception:
            pass


def stats() -> dict:
    """Cache istatistikleri."""
    disk_count = len([f for f in os.listdir(CACHE_DIR) if f.endswith(".json")])
    return {
        "memory_items": len(_memory_cache),
        "disk_items": disk_count,
        "max_memory": MAX_MEMORY,
        "ttl_seconds": CACHE_TTL,
    }
