import os, sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import streamlit as st
import config
from app.lang import LANG


def t(key, default=None):
    return LANG.get("en", {}).get(key, default if default is not None else key)


from services import document_processor, lightrag_service, supabase_service
import config
import time
from utils.helpers import count_words


def _export_chat_md():
    if not st.session_state.get("messages"):
        return ""
    lines = [f"# {t('export_title', 'Chat Export')}\n"]
    for m in st.session_state.messages:
        role = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"**{role}**: {m['content']}\n")
    return "\n".join(lines)


def render_sidebar():
    with st.sidebar:
        # ── LOGO + LANG ──
        st.markdown(
            '<div class="logo-area"><div class="logo-moon">🌙</div><div class="logo-text">LunarTech AI</div><div class="logo-sub">v4 · rag engine</div></div>',
            unsafe_allow_html=True,
        )
        # Removed language switcher, enforcing English system-wide
        st.markdown(
            f'<div style="text-align:center;color:#475569;font-size:.7rem;margin-top:4px">AI Assistant</div>',
            unsafe_allow_html=True,
        )

        # Logout Button
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            from services.supabase_service import sign_out

            sign_out()
            st.session_state.user = None
            st.rerun()

        st.markdown('<hr class="glow-div">', unsafe_allow_html=True)

        # ── 1. NAVİGASYON ──
        st.markdown("### 🧭 NAVIGATION")
        pages = {
            "💬 Chat": "chat",
            "📚 Handbook": "handbook",
            "🧠 AI Tools": "ai_tools",
            "📊 Dashboard": "dashboard",
            "🔬 Knowledge Graph": "kg",
            "🕒 Shadow Agents": "shadow_agents",
            "🧩 Swarm Studio": "swarm_studio",
        }

        user_email = (
            st.session_state.user.email
            if hasattr(st.session_state.get("user"), "email")
            else ""
        )
        if user_email in config.ADMIN_EMAILS:
            pages["🛡️ Admin Panel"] = "admin"
        cols = st.columns(2)
        for i, (label, key) in enumerate(pages.items()):
            with cols[i % 2]:
                btn_type = (
                    "primary" if st.session_state.page_mode == key else "secondary"
                )
                if st.button(
                    label, use_container_width=True, type=btn_type, key=f"nav_{key}"
                ):
                    st.session_state.page_mode = key
                    st.rerun()

        st.markdown('<hr class="glow-div">', unsafe_allow_html=True)

        # ── 2. MODEL ──
        st.markdown(f"### {t('model_section')}")
        model_names = list(config.AVAILABLE_MODELS.keys())
        current_name = next(
            (
                n
                for n, m in config.AVAILABLE_MODELS.items()
                if m == st.session_state.selected_model
            ),
            model_names[0],
        )
        selected = st.selectbox(
            "Model",
            model_names,
            index=model_names.index(current_name),
            label_visibility="collapsed",
        )
        st.session_state.selected_model = config.AVAILABLE_MODELS[selected]
        mid = st.session_state.selected_model
        info = config.get_model_info(mid)
        fav_icon = "⭐" if st.session_state.favorite_model == mid else "☆"
        st.markdown(
            f"""<div class="model-card"><div class="model-id">📡 {mid} {fav_icon}</div><div class="model-meta">📏 {info["ctx"]} ctx · {info["speed"]} · {info["cost"]}</div></div>""",
            unsafe_allow_html=True,
        )
        if st.button(
            f"{t('favorite')} {'✓' if st.session_state.favorite_model == mid else ''}",
            key="fav_btn",
            use_container_width=True,
        ):
            st.session_state.favorite_model = (
                mid if st.session_state.favorite_model != mid else None
            )
            st.rerun()

        st.markdown('<hr class="glow-div">', unsafe_allow_html=True)

        # ── 3. PDF YÖNETİMİ ──
        st.markdown(f"### {t('upload_section')}")
        uploaded_files = st.file_uploader(
            "📄 PDF / DOCX / TXT / MD",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files:
            for f in uploaded_files:
                handle_file_upload(f)

        if st.session_state.documents:
            st.markdown(f"### {t('docs_section')}")
            total_p = sum(d.get("page_count", 0) for d in st.session_state.documents)
            total_w = sum(d.get("word_count", 0) for d in st.session_state.documents)
            st.markdown(
                f'<div style="color:#475569;font-size:.7rem;margin-bottom:6px;">{t("total_summary")}: {len(st.session_state.documents)} 📄 · {total_p} {t("page_short")} · {total_w:,} {t("word_short")}</div>',
                unsafe_allow_html=True,
            )
            docs_to_remove = None
            for idx, doc in enumerate(st.session_state.documents):
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(
                        f'<div class="doc"><div class="doc-info"><div class="doc-name">📄 {doc["filename"]}</div><div class="doc-meta">{doc.get("page_count","?")}p · {doc.get("word_count","?")}w</div></div></div>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("🗑️", key=f"del_doc_{idx}"):
                        docs_to_remove = idx
            if docs_to_remove is not None:
                doc_to_delete = st.session_state.documents.pop(docs_to_remove)

                uid = (
                    st.session_state.user.id
                    if hasattr(st.session_state.get("user"), "id")
                    else None
                )
                if "id" in doc_to_delete:
                    supabase_service.delete_document(doc_to_delete["id"], user_id=uid)

                import os

                doc_dir = os.path.join(config.LIGHTRAG_WORK_DIR, "documents")
                safe_name = (
                    f"{uid}_{doc_to_delete['filename']}"
                    if uid
                    else doc_to_delete["filename"]
                )
                file_path = os.path.join(doc_dir, safe_name)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass

                if not st.session_state.documents:
                    st.session_state.has_documents = False
                    st.session_state.current_doc_id = None

                st.rerun()

        st.markdown('<hr class="glow-div">', unsafe_allow_html=True)

        # ── 4. AYARLAR ──
        with st.expander(t("settings_section"), expanded=False):
            st.markdown("#### 🏢 Team & Workspace")
            workspace_id = st.text_input(
                "Team Code (Optional)",
                value=st.session_state.get("workspace_id", ""),
                help="You can share documents and chats with teammates who enter the same code.",
            )
            if workspace_id != st.session_state.get("workspace_id", ""):
                st.session_state.workspace_id = workspace_id
                # Re-fetch documents and chats for the new workspace
                import services.supabase_service as ss_module

                uid = (
                    workspace_id
                    if workspace_id
                    else (
                        st.session_state.user.id
                        if hasattr(st.session_state.get("user"), "id")
                        else None
                    )
                )
                st.session_state.documents = ss_module.get_documents(user_id=uid)
                st.session_state.messages = ss_module.get_chat_history(user_id=uid)
                st.session_state.has_documents = bool(st.session_state.documents)
                st.rerun()

            st.markdown("#### 🎛️ AI Parameters")
            st.session_state.temperature = st.slider(
                t("temperature"), 0.0, 1.0, st.session_state.temperature, 0.1
            )
            st.session_state.max_tokens = st.select_slider(
                t("max_tokens"),
                options=[1024, 2048, 4096, 8192, 16384],
                value=st.session_state.max_tokens,
            )
            st.session_state.auto_rag = st.toggle(
                t("auto_rag"), value=st.session_state.get("auto_rag", False)
            )
            st.session_state.rag_mode = st.selectbox(
                t("rag_mode"),
                ["hybrid", "local", "global", "naive"],
                index=["hybrid", "local", "global", "naive"].index(
                    st.session_state.rag_mode
                ),
            )
            st.session_state.streaming_enabled = st.toggle(
                t("streaming"), value=st.session_state.streaming_enabled
            )
            st.session_state.use_persona = st.toggle(
                "👔 Learn & Apply Company Tone/Language",
                value=st.session_state.get("use_persona", False),
                help="Analyzes your previous chats to write responses in your or your company's corporate tone.",
            )
            st.session_state.custom_prompt = st.text_area(
                t("system_prompt"),
                value=st.session_state.custom_prompt,
                placeholder=t("custom_prompt_ph"),
                height=80,
            )

        # ── 5. SOHBET YÖNETİMİ ──
        with st.expander(t("chat_mgmt"), expanded=False):
            if st.button(t("new_chat"), use_container_width=True, key="new_conv"):
                n = len(st.session_state.conversations) + 1
                name = f"{t('conv_label')} {n}"
                st.session_state.conversations[name] = []
                st.session_state.current_conv = name
                st.session_state.messages = []
                st.rerun()

            for cname, msgs in st.session_state.conversations.items():
                is_active = cname == st.session_state.current_conv
                cls = "conv-active" if is_active else ""
                cnt = len(msgs)
                if st.button(
                    f"{'▸ ' if is_active else '  '}{cname} ({cnt} {t('messages')})",
                    key=f"conv_{cname}",
                    use_container_width=True,
                ):
                    st.session_state.current_conv = cname
                    st.session_state.messages = st.session_state.conversations[cname]
                    st.rerun()

            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button(t("clear"), use_container_width=True, key="clr"):
                    st.session_state.conversations[st.session_state.current_conv] = []
                    st.session_state.messages = []
                    st.rerun()
            with cc2:
                if st.session_state.messages:
                    st.download_button(
                        t("export"),
                        data=_export_chat_md(),
                        file_name="chat.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

        # ── 6. HIZLI İSTATİSTİK ──
        with st.expander(t("stats_section"), expanded=False):
            stats = [
                (t("docs_label"), str(len(st.session_state.documents))),
                (t("words_label"), f"{st.session_state.total_words_processed:,}"),
                (t("queries_label"), str(st.session_state.total_queries)),
                (t("handbooks_label"), str(len(st.session_state.handbook_history))),
            ]
            for lb, vl in stats:
                st.markdown(
                    f'<div class="mini-stat"><span class="mini-stat-label">{lb}</span><span class="mini-stat-val">{vl}</span></div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<hr class="glow-div">', unsafe_allow_html=True)

        # ── 7. SİSTEM DURUMU ──
        st.markdown(f"### {t('system_section')}")
        errors = config.validate_config()
        if not errors:
            st.markdown(
                f'<span class="badge badge-on"><span class="pulse-dot pulse-on"></span> {t("connected")}</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<span class="badge badge-off"><span class="pulse-dot pulse-off"></span> {t("api_missing")}</span>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧹 Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.toast("System cache cleared successfully.", icon="✅")

        st.markdown(
            f'<div class="sb-footer"><div class="sb-footer-text">LunarTech AI v{config.APP_VERSION} · © 2026</div></div>',
            unsafe_allow_html=True,
        )


def handle_file_upload(uploaded_file):
    key = f"up_{uploaded_file.name}_{uploaded_file.size}"
    if key in st.session_state:
        return
    if not document_processor.is_supported(uploaded_file.name):
        st.sidebar.error(f"❌ Unsupported format: {uploaded_file.name}")
        return

    # Logical Versioning (v1, v2)
    base_name = uploaded_file.name
    existing_docs = [d["filename"] for d in st.session_state.documents]
    if base_name in existing_docs:
        import re

        version_count = sum(
            1 for d in existing_docs if d.startswith(base_name.rsplit(".", 1)[0])
        )
        name_parts = base_name.rsplit(".", 1)
        if len(name_parts) == 2:
            base_name = f"{name_parts[0]}_v{version_count + 1}.{name_parts[1]}"
        else:
            base_name = f"{base_name}_v{version_count + 1}"

    with st.sidebar:
        with st.spinner(f"📥 {base_name}..."):
            try:
                # Save physical file to disk for Viewer
                import os

                doc_dir = os.path.join(config.LIGHTRAG_WORK_DIR, "documents")
                os.makedirs(doc_dir, exist_ok=True)
                uid = (
                    st.session_state.user.id
                    if hasattr(st.session_state.get("user"), "id")
                    else "guest"
                )
                safe_name = f"{uid}_{base_name}"
                file_path = os.path.join(doc_dir, safe_name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                result = document_processor.process_to_chunks(
                    uploaded_file, uploaded_file.name
                )
                if not result["full_text"].strip():
                    st.error(f"❌ {t('no_text')}")
                    return
                # Quality check
                quality = document_processor.document_quality_score(result)
                # 3) Save to Supabase
                doc_record = {}
                try:
                    uid = (
                        st.session_state.user.id
                        if hasattr(st.session_state.get("user"), "id")
                        else None
                    )
                    doc_record = supabase_service.save_document(
                        filename=base_name,
                        page_count=result["page_count"],
                        chunk_count=result.get("chunk_count", 0),
                        user_id=uid,
                    )
                except Exception:  # Changed from except: to except Exception:
                    pass
                with st.spinner("🧠 Knowledge Graph..."):
                    lightrag_service.insert_document(result["full_text"])
                wc = count_words(result["full_text"])
                st.session_state.documents.append(
                    {
                        "filename": base_name,
                        "page_count": result["page_count"],
                        "chunk_count": result.get("chunk_count", 0),
                        "word_count": wc,
                        "full_text": result["full_text"],
                        "id": doc_record.get("id"),
                        "format": result.get("format", "unknown"),
                        "quality": quality,
                    }
                )
                st.session_state.has_documents = True
                st.session_state.current_doc_id = doc_record.get("id")
                st.session_state.total_words_processed += wc
                st.session_state[key] = True
                fmt = result.get("format", "").upper()
                grade = quality.get("grade", "?")
                st.success(f"✅ {uploaded_file.name} ({fmt} · Quality: {grade})")
            except Exception as e:
                st.error(f"❌ {str(e)}")


# ══════════════════════════════════════════════════════════
# PAGE: CHAT
# ══════════════════════════════════════════════════════════
