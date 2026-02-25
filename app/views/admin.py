import os, sys
import streamlit as st
import pandas as pd
import config
from app.lang import LANG
from services import supabase_service


def t(key):
    lang = st.session_state.get("lang", "tr")
    return LANG.get(lang, LANG["tr"]).get(key, key)


def render_admin_page():
    user = st.session_state.get("user")
    user_email = user.email if hasattr(user, "email") else ""

    if user_email not in config.ADMIN_EMAILS:
        st.error(t("admin_unauthorized"))
        return

    st.markdown(
        f'<div class="pg-header"><div class="pg-title pg-title-dash">🛡️ {t("admin_title")}</div><div class="pg-sub">{t("admin_desc")}</div></div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Loading data..."):
        usage_data = supabase_service.get_all_token_usage()

    if not usage_data:
        st.info("No token usage data found yet.")
        return

    df = pd.DataFrame(usage_data)

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.date
    if "tokens" not in df.columns:
        df["tokens"] = 0
    if "user_id" not in df.columns:
        df["user_id"] = "Unknown"

    total_tokens = df["tokens"].sum()
    total_users = df["user_id"].nunique()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="m-card"><div class="m-val">{total_tokens:,}</div><div class="m-lbl">🪙 Total Tokens</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="m-card"><div class="m-val">{total_users}</div><div class="m-lbl">👥 Active Users/Teams</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="m-card"><div class="m-val">{len(df)}</div><div class="m-lbl">🤖 Total Queries</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(
        [
            "📊 System Analysis",
            "🏢 Workspace Manager",
            "🔗 Corporate Integrations",
        ]
    )

    with tab1:
        left, right = st.columns(2)

        with left:
            st.markdown("#### User/Team Quotas (Tokens)")
            user_grouped = (
                df.groupby("user_id")["tokens"]
                .sum()
                .reset_index()
                .sort_values("tokens", ascending=False)
            )
            st.dataframe(user_grouped, use_container_width=True, hide_index=True)

        with right:
            st.markdown("#### Model Distribution")
            model_grouped = (
                df.groupby("model")["tokens"]
                .sum()
                .reset_index()
                .sort_values("tokens", ascending=False)
            )
            st.bar_chart(model_grouped.set_index("model"), color="#818cf8")

    with tab2:
        st.markdown("#### 🌍 All Documents in the System")
        st.info(
            "With your admin privileges, you can view documents belonging to all teams/users."
        )

        all_docs = supabase_service.get_documents()
        if all_docs:
            docs_df = pd.DataFrame(all_docs)
            if "created_at" in docs_df.columns:
                docs_df["created_at"] = pd.to_datetime(
                    docs_df["created_at"]
                ).dt.strftime("%Y-%m-%d %H:%M")

            st.dataframe(
                docs_df[
                    [
                        "id",
                        "filename",
                        "user_id",
                        "page_count",
                        "chunk_count",
                        "created_at",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("There are no documents uploaded to the system yet.")

    with tab3:
        st.markdown("#### Corporate Service Connectors")
        st.info(
            "Through this section, you can allow LunarTech agents direct access to your company's external data sources."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_g, col_j, col_s = st.columns(3)

        with col_g:
            st.markdown("##### ☁️ Google Drive")
            st.caption("Let agents automatically sync your folders.")
            if st.button("Connect to Drive", key="btn_drive"):
                st.toast("Google OAuth flow is starting...", icon="☁️")

        with col_j:
            st.markdown("##### 🎫 Jira / Trello")
            st.caption("Let agents read sprint tasks and manage assignments.")
            if st.button("Connect to Jira", key="btn_jira", disabled=True):
                pass

        with col_s:
            st.markdown("##### 💬 Slack / Teams")
            st.caption("Let agents infiltrate corporate channels as shadow agents.")
            if st.button("Add to Slack", key="btn_slack", disabled=True):
                pass
