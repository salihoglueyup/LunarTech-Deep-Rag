"""
LunarTech AI - Merkezi Konfigürasyon Modülü v2
Yeni modeller, daha fazla ayar seçeneği.
"""

import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path, override=True)

# ── Supabase ──────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")

# ── Admin Settings ────────────────────────────────────────
ADMIN_EMAILS = [
    e.strip() for e in os.getenv("ADMIN_EMAILS", "admin@lunartech.ai,eyupz").split(",")
]

# ── API Keys & Base URLs ──────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# ── LLM Modelleri ─────────────────────────────────────────
AVAILABLE_MODELS = {
    "Ollama Qwen 2.5 (3B)": "ollama/qwen2.5:3b",
    "Solar Pro 3 (Free)": "upstage/solar-pro-3:free",
    "Gemini 2.5 Flash": "google/gemini-2.5-flash",
    "Gemini 2.5 Pro": "google/gemini-2.5-pro",
    "DeepSeek Chat V3": "deepseek/deepseek-chat-v3-0324",
    "DeepSeek R1": "deepseek/deepseek-r1",
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    "Claude 4 Sonnet": "anthropic/claude-sonnet-4",
    "Llama 4 Scout": "meta-llama/llama-4-scout",
    "Qwen3 235B": "qwen/qwen3-235b-a22b",
}

DEFAULT_MODEL = os.getenv("LLM_MODEL", "ollama/qwen2.5:3b")

# Model bilgi kartları
MODEL_INFO = {
    "ollama/qwen2.5:3b": {"ctx": "32K", "speed": "💻 Yerel", "cost": "Bedava"},
    "upstage/solar-pro-3:free": {
        "ctx": "32K",
        "speed": "⚡ Fast",
        "cost": "Free",
    },
    "google/gemini-2.5-flash": {"ctx": "1M", "speed": "⚡ Hızlı", "cost": "💰"},
    "google/gemini-2.5-pro": {"ctx": "1M", "speed": "🐢 Yavaş", "cost": "💰💰💰"},
    "deepseek/deepseek-chat-v3-0324": {"ctx": "64K", "speed": "⚡ Hızlı", "cost": "💰"},
    "deepseek/deepseek-r1": {"ctx": "64K", "speed": "🐢 Yavaş", "cost": "💰💰"},
    "anthropic/claude-3.5-sonnet": {"ctx": "200K", "speed": "⚡ Orta", "cost": "💰💰"},
    "anthropic/claude-sonnet-4": {"ctx": "200K", "speed": "⚡ Orta", "cost": "💰💰"},
    "meta-llama/llama-4-scout": {"ctx": "512K", "speed": "⚡ Hızlı", "cost": "💰"},
    "qwen/qwen3-235b-a22b": {"ctx": "128K", "speed": "⚡ Orta", "cost": "💰"},
}

# ── Embedding ─────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = 384

# ── LightRAG ──────────────────────────────────────────────
LIGHTRAG_WORK_DIR = os.path.join(os.path.dirname(__file__), "data", "lightrag_store")

# ── Handbook / LongWriter ─────────────────────────────────
MAX_HANDBOOK_WORDS = int(os.getenv("MAX_HANDBOOK_WORDS", "20000"))
WORDS_PER_SECTION = 2000
MAX_SECTIONS = 15

# ── PDF İşleme ────────────────────────────────────────────
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ── Uygulama Ayarları ─────────────────────────────────────
APP_TITLE = "🌙 LunarTech AI"
APP_SUBTITLE = "RAG Chat & Handbook Generator"
APP_ICON = "🌙"
APP_VERSION = "2.0"


def validate_config() -> list[str]:
    errors = []
    if not OPENROUTER_API_KEY:
        errors.append("OPENROUTER_API_KEY .env dosyasında tanımlı değil!")
    if not SUPABASE_URL:
        errors.append("SUPABASE_URL .env dosyasında tanımlı değil!")
    if not SUPABASE_KEY:
        errors.append("SUPABASE_KEY .env dosyasında tanımlı değil!")
    return errors


def get_model_info(model_id: str) -> dict:
    """Model hakkında bilgi kartı döndürür."""
    return MODEL_INFO.get(model_id, {"ctx": "?", "speed": "?", "cost": "?"})
