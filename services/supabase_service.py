"""
LunarTech AI - Supabase Servisi
Doküman metadata, chat geçmişi ve handbook kayıtları için CRUD işlemleri.
"""

import os
import sys
from datetime import datetime

# Proje kökünü path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

try:
    from supabase import create_client, Client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_client() -> "Client":
    """Supabase client'ı döndürür."""
    if not SUPABASE_AVAILABLE:
        raise ImportError("supabase library is not installed. pip install supabase")

    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be defined in the .env file!"
        )

    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


# ── Auth İşlemleri ────────────────────────────────────────


def sign_up(email: str, password: str):
    """Yeni kullanıcı kaydı oluşturur."""
    client = get_client()
    return client.auth.sign_up({"email": email, "password": password})


def sign_in(email: str, password: str):
    """Kullanıcı girişi yapar."""
    client = get_client()
    return client.auth.sign_in_with_password({"email": email, "password": password})


def sign_out():
    """Oturumu kapatır."""
    client = get_client()
    return client.auth.sign_out()


def get_user():
    """Geçerli oturumdaki kullanıcıyı getirir."""
    client = get_client()
    return client.auth.get_user()


# ── Doküman İşlemleri ─────────────────────────────────────


def save_document(
    filename: str, page_count: int, chunk_count: int, user_id: str = None
) -> dict:
    """Yeni doküman kaydı oluşturur."""
    client = get_client()
    data = {
        "filename": filename,
        "page_count": page_count,
        "chunk_count": chunk_count,
        "status": "processed",
    }
    if user_id:
        data["user_id"] = user_id

    result = client.table("documents").insert(data).execute()
    return result.data[0] if result.data else {}


def get_documents(user_id: str = None) -> list[dict]:
    """Tüm dokümanları listeler."""
    client = get_client()
    query = client.table("documents").select("*")
    if user_id:
        query = query.eq("user_id", user_id)

    result = query.order("created_at", desc=True).execute()
    return result.data or []


def delete_document(doc_id: str, user_id: str = None) -> bool:
    """Dokümanı ve ilişkili kayıtları siler."""
    client = get_client()
    query = client.table("documents").delete().eq("id", doc_id)
    if user_id:
        query = query.eq("user_id", user_id)

    query.execute()
    return True


# ── Chat Geçmişi İşlemleri ────────────────────────────────


def save_chat_message(
    role: str, content: str, document_id: str = None, user_id: str = None
) -> dict:
    """Chat mesajını kaydeder."""
    client = get_client()
    data = {"role": role, "content": content}
    if document_id:
        data["document_id"] = document_id
    if user_id:
        data["user_id"] = user_id

    result = client.table("chat_history").insert(data).execute()
    return result.data[0] if result.data else {}


def get_chat_history(
    document_id: str = None, limit: int = 50, user_id: str = None
) -> list[dict]:
    """Chat geçmişini getirir."""
    client = get_client()
    query = client.table("chat_history").select("*")

    if document_id:
        query = query.eq("document_id", document_id)
    if user_id:
        query = query.eq("user_id", user_id)

    result = query.order("created_at", desc=False).limit(limit).execute()
    return result.data or []


def clear_chat_history(document_id: str = None, user_id: str = None) -> bool:
    """Chat geçmişini temizler."""
    client = get_client()
    query = client.table("chat_history").delete()

    if document_id:
        query = query.eq("document_id", document_id)
    else:
        query = query.gte("created_at", "2000-01-01")

    if user_id:
        query = query.eq("user_id", user_id)

    query.execute()
    return True


# ── Handbook İşlemleri ─────────────────────────────────────


def save_handbook(
    title: str,
    content: str,
    word_count: int,
    document_id: str = None,
    user_id: str = None,
) -> dict:
    """Handbook kaydı oluşturur."""
    client = get_client()
    data = {
        "title": title,
        "content": content,
        "word_count": word_count,
    }
    if document_id:
        data["document_id"] = document_id
    if user_id:
        data["user_id"] = user_id

    result = client.table("handbooks").insert(data).execute()
    return result.data[0] if result.data else {}


def get_handbooks(document_id: str = None, user_id: str = None) -> list[dict]:
    """Handbook listesini getirir."""
    client = get_client()
    query = client.table("handbooks").select("*")

    if document_id:
        query = query.eq("document_id", document_id)
    if user_id:
        query = query.eq("user_id", user_id)

    result = query.order("created_at", desc=True).execute()
    return result.data or []


# ── Finansal Analiz (Admin) ────────────────────────────────


def save_token_usage(user_id: str, model: str, tokens: int) -> bool:
    """Kullanıcının token harcamasını kaydeder."""
    try:
        client = get_client()
        client.table("token_usage").insert(
            {"user_id": user_id, "model": model, "tokens": tokens}
        ).execute()
        return True
    except Exception:
        return False


def get_all_token_usage() -> list[dict]:
    """Admin paneli için tüm token kullanımlarını getirir."""
    try:
        client = get_client()
        res = (
            client.table("token_usage")
            .select("*")
            .order("created_at", desc=True)
            .limit(1000)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


# ── Bağlantı Testi ─────────────────────────────────────────


def test_connection() -> bool:
    """Supabase bağlantısını test eder."""
    try:
        client = get_client()
        client.table("documents").select("id").limit(1).execute()
        return True
    except Exception:
        return False
