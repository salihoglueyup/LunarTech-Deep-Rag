"""
LunarTech AI — Logger
Structured logging with file output and Streamlit integration.
"""

import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ── Log file ──
_log_file = os.path.join(LOG_DIR, f"lunartech_{datetime.now().strftime('%Y%m%d')}.log")

# ── Logger setup ──
logger = logging.getLogger("lunartech")
logger.setLevel(logging.DEBUG)

# File handler
if not logger.handlers:
    fh = logging.FileHandler(_log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", datefmt="%H:%M:%S"
        )
    )
    logger.addHandler(fh)

    # Console handler (WARNING+)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("⚠️ %(levelname)s: %(message)s"))
    logger.addHandler(ch)


def info(msg: str, **kwargs):
    """Bilgi logu."""
    extra = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"{msg} {extra}" if extra else msg)


def warning(msg: str, **kwargs):
    """Uyarı logu."""
    extra = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.warning(f"{msg} {extra}" if extra else msg)


def error(msg: str, exc: Exception = None, **kwargs):
    """Hata logu."""
    extra = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    full_msg = f"{msg} {extra}" if extra else msg
    if exc:
        logger.error(f"{full_msg} | error={type(exc).__name__}: {str(exc)}")
    else:
        logger.error(full_msg)


def llm_call(model: str, tokens: int = 0, cached: bool = False, duration_ms: int = 0):
    """LLM çağrı logu."""
    status = "CACHED" if cached else "API"
    logger.info(
        f"LLM {status} | model={model} | tokens={tokens} | time={duration_ms}ms"
    )


def get_recent_logs(n: int = 50) -> list[str]:
    """Son N log satırını döndürür."""
    try:
        with open(_log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-n:]
    except FileNotFoundError:
        return []
