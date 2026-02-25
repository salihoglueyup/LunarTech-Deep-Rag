"""
LunarTech AI — Analytics Service
Session-based stats tracking for tools, models, and usage.
"""

import time
from collections import defaultdict


class Analytics:
    """Oturum bazlı analitik takibi."""

    def __init__(self):
        self.tool_usage = defaultdict(int)  # tool_name → count
        self.model_usage = defaultdict(int)  # model_name → count
        self.events = []  # [{type, name, ts, detail}]
        self.start_time = time.time()

    def track_tool(self, tool_name: str, model: str = "", duration_ms: int = 0):
        """AI tool kullanımını kaydet."""
        self.tool_usage[tool_name] += 1
        if model:
            self.model_usage[model] += 1
        self.events.append(
            {
                "type": "tool",
                "name": tool_name,
                "model": model,
                "ts": time.time(),
                "duration_ms": duration_ms,
            }
        )

    def track_chat(self, model: str = ""):
        """Chat mesajı kaydet."""
        self.events.append(
            {"type": "chat", "name": "chat", "model": model, "ts": time.time()}
        )
        if model:
            self.model_usage[model] += 1

    def track_upload(self, filename: str, fmt: str, quality: str):
        """Dosya yükleme kaydet."""
        self.events.append(
            {
                "type": "upload",
                "name": filename,
                "model": "",
                "ts": time.time(),
                "format": fmt,
                "quality": quality,
            }
        )

    def get_top_tools(self, n: int = 5) -> list:
        """En çok kullanılan araçlar."""
        sorted_tools = sorted(self.tool_usage.items(), key=lambda x: x[1], reverse=True)
        return sorted_tools[:n]

    def get_top_models(self, n: int = 3) -> list:
        """En çok kullanılan modeller."""
        sorted_models = sorted(
            self.model_usage.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_models[:n]

    def get_session_duration(self) -> str:
        """Oturum süresi."""
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}s {minutes}dk"
        return f"{minutes}dk {seconds}sn"

    def get_event_count(self) -> dict:
        """Olay sayıları."""
        counts = defaultdict(int)
        for e in self.events:
            counts[e["type"]] += 1
        return dict(counts)

    def get_recent_events(self, n: int = 10) -> list:
        """Son N olay."""
        return list(reversed(self.events[-n:]))

    def get_summary(self) -> dict:
        """Özet istatistikler."""
        return {
            "total_tools": sum(self.tool_usage.values()),
            "unique_tools": len(self.tool_usage),
            "total_chats": sum(1 for e in self.events if e["type"] == "chat"),
            "total_uploads": sum(1 for e in self.events if e["type"] == "upload"),
            "session_duration": self.get_session_duration(),
            "top_tools": self.get_top_tools(),
            "top_models": self.get_top_models(),
        }


# Singleton instance
_analytics = None


def get():
    """Analytics singleton'ını döndürür."""
    global _analytics
    if _analytics is None:
        _analytics = Analytics()
    return _analytics
