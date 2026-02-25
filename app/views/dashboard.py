import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import streamlit as st
import config
from app.lang import LANG

def t(key):
    lang = st.session_state.get('lang', 'tr')
    return LANG.get(lang, LANG['tr']).get(key, key)

from services import lightrag_service, llm_service, cache_service
import config

def render_dashboard_page():
    st.markdown(
        f'<div class="pg-header"><div class="pg-title pg-title-dash">{t("dash_title")}</div><div class="pg-sub">{t("dash_desc")}</div></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    md = [
        ("📄", t("docs_label"), str(len(st.session_state.documents))),
        ("📝", t("words_label"), f"{st.session_state.total_words_processed:,}"),
        ("💬", t("queries_label"), str(st.session_state.total_queries)),
        ("📚", t("handbooks_label"), str(len(st.session_state.handbook_history))),
    ]
    for col, (ic, lb, vl) in zip(cols, md):
        with col:
            st.markdown(
                f'<div class="m-card"><div class="m-val">{vl}</div><div class="m-lbl">{ic} {lb}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Analytics Section ──
    st.markdown(f"#### ⚡ {t('token_usage')} & {t('cache_stats')}")
    acols = st.columns(4)
    token_data = llm_service.get_token_usage()
    cache_data = cache_service.stats()
    analytics_items = [
        ("🔤", "Tokens", f"{token_data['total']:,}"),
        ("📡", "API Calls", str(token_data["calls"])),
        ("💾", "Cache Hit", str(token_data["cached"])),
        (
            "📂",
            "Cache Items",
            str(cache_data["memory_items"] + cache_data["disk_items"]),
        ),
    ]
    for col, (ic, lb, vl) in zip(acols, analytics_items):
        with col:
            st.markdown(
                f'<div class="m-card"><div class="m-val">{vl}</div><div class="m-lbl">{ic} {lb}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown(f"#### {t('doc_list')}")
        if st.session_state.documents:
            for d in st.session_state.documents:
                fmt = d.get("format", "pdf").upper()
                q = d.get("quality", {})
                grade = q.get("grade", "?") if isinstance(q, dict) else "?"
                st.markdown(
                    f'<div class="glass" style="margin-bottom:8px;padding:.8rem 1rem"><div style="color:#cbd5e1;font-weight:600">📄 {d["filename"]} <span class="badge badge-on" style="font-size:.6rem">{fmt}</span> <span class="badge badge-on" style="font-size:.6rem">{grade}</span></div><div style="color:#475569;font-size:.75rem">{d.get("page_count","?")}p · {d.get("word_count","?")}w</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f'<div class="empty-state"><div class="empty-icon">📭</div><div class="empty-text">{t("no_doc_yet")}</div></div>',
                unsafe_allow_html=True,
            )
    with right:
        st.markdown(f"#### {t('handbook_history')}")
        if st.session_state.handbook_history:
            for h in reversed(st.session_state.handbook_history):
                st.markdown(
                    f'<div class="glass" style="margin-bottom:8px;padding:.8rem 1rem"><div style="color:#cbd5e1;font-weight:600">📘 {h["title"]}</div><div style="color:#475569;font-size:.75rem">{h["word_count"]:,} {t("words_label")} · {h["time"]}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f'<div class="empty-state"><div class="empty-icon">📝</div><div class="empty-text">{t("no_handbook_yet")}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### {t('system_section')}")
    scols = st.columns(3)
    errors = config.validate_config()
    api_ok = len(errors) == 0
    rag_ok = lightrag_service.is_initialized()
    for col, (name, ok) in zip(
        scols, [("OpenRouter API", api_ok), ("LightRAG", rag_ok), ("Supabase", api_ok)]
    ):
        with col:
            dot = "pulse-on" if ok else "pulse-off"
            label = t("active") if ok else t("waiting")
            st.markdown(
                f'<div class="glass" style="text-align:center"><div style="color:#cbd5e1;font-weight:500;margin-bottom:6px">{name}</div><span class="pulse-dot {dot}"></span><span style="color:#64748b;font-size:.75rem;margin-left:6px">{label}</span></div>',
                unsafe_allow_html=True,
            )
    if st.session_state.messages:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### {t('last_messages')}")
        for msg in st.session_state.messages[-8:]:
            dot_cls = "tl-dot-user" if msg["role"] == "user" else "tl-dot-ai"
            icon = "🧑‍💻" if msg["role"] == "user" else "🌙"
            preview = (
                msg["content"][:100] + "..."
                if len(msg["content"]) > 100
                else msg["content"]
            )
            st.markdown(
                f'<div class="tl-item"><div class="tl-dot {dot_cls}"></div><div class="tl-content">{icon} {preview}</div></div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════
# PAGE: KNOWLEDGE GRAPH
# ══════════════════════════════════════════════════════════
