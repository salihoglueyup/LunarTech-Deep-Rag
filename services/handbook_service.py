"""
LunarTech AI - Handbook Service v2
Handbook generation management with LongWriter orchestrator.
Per-section RAG query support added.
"""

import os
import sys
from typing import Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services import lightrag_service, supabase_service
from core.longwriter import generate_handbook


def start_generation(
    topic: str,
    model: str = None,
    document_id: str = None,
    progress_callback: Optional[Callable] = None,
    user_id: str = None,
) -> dict:
    """Starts the handbook generation process."""
    _safe_callback(progress_callback, 0, 1, "🔍 Gathering context from documents...", 0)

    context = _gather_context(topic)

    # RAG query function — can make separate queries for each section
    def rag_query_func(query: str) -> str:
        try:
            return lightrag_service.query(query, mode="hybrid")
        except Exception:
            return ""

    result = generate_handbook(
        topic=topic,
        context=context,
        model=model,
        progress_callback=progress_callback,
        rag_query_func=rag_query_func,
    )

    try:
        supabase_service.save_handbook(
            title=result["title"],
            content=result["content"],
            word_count=result["word_count"],
            document_id=document_id,
            user_id=user_id,
        )
    except Exception:
        pass

    return result


# ── INTERACTIVE HANDBOOK ──


def start_interactive_generation(topic: str, model: str = None) -> dict:
    context = _gather_context(topic)
    from core.longwriter import init_interactive_handbook

    return init_interactive_handbook(topic, context, model=model)


def rag_query_func_wrapper(query: str) -> str:
    try:
        return lightrag_service.query(query, mode="hybrid")
    except Exception:
        return ""


def save_interactive_handbook(
    result: dict, document_id: str = None, user_id: str = None
):
    try:
        supabase_service.save_handbook(
            title=result["title"],
            content=result["content"],
            word_count=result["word_count"],
            document_id=document_id,
            user_id=user_id,
        )
    except Exception:
        pass


def _gather_context(topic: str) -> str:
    """Gathers comprehensive context from LightRAG about the topic."""
    context_parts = []

    queries = [
        f"General information about {topic}",
        f"Core concepts and terms of {topic}",
        f"Application areas and examples of {topic}",
        f"Best practices for {topic}",
        f"Recent developments and trends in {topic}",
    ]

    for q in queries:
        try:
            result = lightrag_service.query(q, mode="hybrid")
            if result and len(result) > 50:
                context_parts.append(result)
        except Exception:
            continue

    if not context_parts:
        return "Failed to retrieve context from documents. The handbook will be generated based on general knowledge."

    return "\n\n---\n\n".join(context_parts)


def _safe_callback(callback, *args):
    if callback:
        try:
            callback(*args)
        except Exception:
            pass
