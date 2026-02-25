import os, sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import config
from app.lang import LANG
from services import supabase_service


def t(key):
    lang = st.session_state.get("lang", "tr")
    return LANG.get(lang, LANG["tr"]).get(key, key)


def render_auth_page():
    st.markdown(
        f'<div class="pg-header"><div class="pg-title pg-title-dash">{t("login_title")}</div><div class="pg-sub">{t("login_desc")}</div></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs([t("login_tab"), t("register_tab")])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input(t("email_label"))
                password = st.text_input(t("password_label"), type="password")
                submit = st.form_submit_button(t("login_btn"), use_container_width=True)

                if submit:
                    if not email or not password:
                        st.error(t("auth_empty_fields"))
                    else:
                        with st.spinner("⏳ Loading..."):
                            try:
                                res = supabase_service.sign_in(email, password)
                                if res and res.user:
                                    st.session_state.user = res.user

                                    # Load user data into session
                                    st.session_state.documents = (
                                        supabase_service.get_documents(
                                            user_id=res.user.id
                                        )
                                    )
                                    st.session_state.messages = (
                                        supabase_service.get_chat_history(
                                            user_id=res.user.id
                                        )
                                    )
                                    st.session_state.handbook_history = (
                                        supabase_service.get_handbooks(
                                            user_id=res.user.id
                                        )
                                    )
                                    if st.session_state.documents:
                                        st.session_state.has_documents = True

                                    st.session_state.toast_msg = t("login_success")
                                    st.rerun()
                                else:
                                    st.error(t("auth_failed"))
                            except Exception as e:
                                st.error(f"{t('auth_failed')}: {str(e)}")

        with tab_register:
            with st.form("register_form"):
                reg_email = st.text_input(t("email_label"), key="reg_email")
                reg_password = st.text_input(
                    t("password_label"), type="password", key="reg_pass"
                )
                reg_password_conf = st.text_input(
                    t("password_conf_label"), type="password", key="reg_pass_conf"
                )
                submit_reg = st.form_submit_button(
                    t("register_btn"), use_container_width=True
                )

                if submit_reg:
                    if not reg_email or not reg_password:
                        st.error(t("auth_empty_fields"))
                    elif reg_password != reg_password_conf:
                        st.error(t("auth_password_mismatch"))
                    else:
                        with st.spinner("⏳ Loading..."):
                            try:
                                res = supabase_service.sign_up(reg_email, reg_password)
                                if res and res.user:
                                    st.success(t("register_success"))
                                else:
                                    st.error(t("auth_failed"))
                            except Exception as e:
                                st.error(f"{t('auth_failed')}: {str(e)}")
