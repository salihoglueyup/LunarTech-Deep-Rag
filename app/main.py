"""
LunarTech AI v4 — Mega Sidebar + i18n Edition
🌙 RAG Chat & Handbook Generator
"""

import os, sys, time, json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import importlib
import config

importlib.reload(config)

# Kalıcı fallback — eğer cache sorunu varsa fonksiyonu doğrudan tanımla
if not hasattr(config, "get_model_info"):

    def _get_model_info(model_id):
        return {
            "id": model_id,
            "name": model_id.split("/")[-1].replace("-", " ").title(),
            "context": 128000,
            "developer": "Unknown",
            "pricing": {"prompt": "0.00", "completion": "0.00"},
            "type": "General",
            "recommended": False,
            "is_free": False,
        }

    config.get_model_info = _get_model_info

from app.components.theme import inject_css
from app.lang import LANG

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def t(key):
    lang = st.session_state.get("lang", "tr")
    return LANG.get(lang, LANG["tr"]).get(key, key)


inject_css()


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
def init_session_state():
    defaults = {
        "messages": [],
        "documents": [],
        "current_doc_id": None,
        "has_documents": False,
        "selected_model": config.DEFAULT_MODEL,
        "handbook_result": None,
        "handbook_history": [],
        "lang": "tr",
        "toast_msg": None,
        "page_mode": "chat",
        "favorite_model": None,
        "temperature": 0.7,
        "max_tokens": 4096,
        "streaming_enabled": True,
        "rag_mode": "hybrid",
        "total_words_processed": 0,
        "total_queries": 0,
        "custom_prompt": "",
        "conversations": {"LunarTech AI v4": []},
        "current_conv": "LunarTech AI v4",
        "user": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Make config validation quiet at startup unless in an active session
    errors = config.validate_config()
    if errors and st.session_state.get("toast_msg") != "loaded":
        for e in errors:
            print(f"Config Warning: {e}")


init_session_state()

# ══════════════════════════════════════════════════════════
# ROUTING & PAGE IMPORTS
# ══════════════════════════════════════════════════════════
from app.components.sidebar import render_sidebar, handle_file_upload
from app.views.chat import render_chat_page, _render_welcome
from app.views.handbook import render_handbook_page
from app.views.dashboard import render_dashboard_page
from app.views.kg import render_kg_page
from app.views.ai_tools import render_ai_tools_page
from app.views.auth import render_auth_page
from app.views.admin import render_admin_page


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
def main():
    if st.session_state.get("toast_msg"):
        st.toast(st.session_state.toast_msg)
        st.session_state.toast_msg = None

    # Yetkilendirme Kontrolü
    if not st.session_state.get("user"):
        render_auth_page()
        return

    render_sidebar()
    page = st.session_state.get("page_mode", "chat")
    print(f"[DEBUG] Routing to page: '{page}'")

    if page == "chat":
        if not st.session_state.messages and not st.session_state.has_documents:
            _render_welcome()
        else:
            render_chat_page()
    elif page == "handbook":
        render_handbook_page()
    elif page == "dashboard":
        render_dashboard_page()
    elif page == "kg":
        render_kg_page()
    elif page == "ai_tools":
        render_ai_tools_page()
    elif page == "admin":
        render_admin_page()
    elif page == "shadow_agents":
        from app.views.shadow_agents import render_shadow_agents_page

        render_shadow_agents_page()
    elif page == "swarm_studio":
        from app.views.swarm_studio import render_swarm_studio_page

        render_swarm_studio_page()


if __name__ == "__main__":
    main()
