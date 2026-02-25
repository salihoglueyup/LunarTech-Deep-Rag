import os, sys
import streamlit as st
import pandas as pd
from datetime import datetime
import config
from app.lang import LANG
from core.background_worker import add_task, get_all_tasks, clear_completed_tasks


def t(key):
    lang = st.session_state.get("lang", "tr")
    return LANG.get(lang, LANG["tr"]).get(key, key)


def render_shadow_agents_page():
    st.markdown(
        f'<div class="pg-header"><div class="pg-title pg-title-dash">🕒 Shadow Agents (Background Tasks)</div><div class="pg-sub">Let the AI complete background tasks even when you are not here.</div></div>',
        unsafe_allow_html=True,
    )

    st.info(
        "💡 **Shadow Agents** work on the server even if you close the system, completing long-running tasks like web scraping, data mining, or periodic reporting."
    )

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown("### 📝 Create New Task")

        task_type = st.selectbox(
            "Task Type",
            ["General Research", "URL Crawling & Summarization", "Database Report"],
        )
        task_prompt = st.text_area(
            "What do you want to be done?",
            height=150,
            placeholder="E.g.: Scan AI news on HackerNews and generate a summary report for me.",
        )

        trigger_type_label = st.radio(
            "Schedule", ["Run Immediately", "Scheduled (Recurring)"], horizontal=True
        )
        schedule_time = None
        interval_minutes = None
        if trigger_type_label == "Scheduled (Recurring)":
            interval_minutes = st.number_input(
                "Run Every X Minutes", min_value=1, value=60
            )
            from datetime import timedelta

            schedule_time = datetime.now() + timedelta(minutes=interval_minutes)

        if st.button("🚀 Add Task to Queue", type="primary", use_container_width=True):
            if task_prompt.strip():
                uid = (
                    st.session_state.user.id
                    if hasattr(st.session_state.get("user"), "id")
                    else "guest"
                )
                tt = (
                    "immediate"
                    if trigger_type_label == "Run Immediately"
                    else "scheduled"
                )
                task_id = add_task(
                    task_type,
                    task_prompt,
                    user_id=uid,
                    trigger_type=tt,
                    schedule_time=schedule_time,
                    interval_minutes=interval_minutes,
                )
                st.success(f"Task added to queue! ID: {task_id[:8]}...")
                st.rerun()
            else:
                st.error("Please enter task instructions.")

    with col2:
        st.markdown("### 📋 Task Queue & Results")

        tasks = get_all_tasks()

        if not tasks:
            st.markdown(
                f'<div class="empty-state"><div class="empty-icon">🏖️</div><div class="empty-text">No pending or running tasks at the moment.</div></div>',
                unsafe_allow_html=True,
            )
        else:
            # Sort tasks: pending first, then running, then completed (newest first)
            tasks.sort(
                key=lambda x: (
                    0
                    if x["status"] == "running"
                    else (1 if x["status"] == "pending" else 2)
                )
            )

            for task in tasks:
                status_colors = {
                    "pending": "orange",
                    "running": "blue",
                    "completed": "green",
                    "failed": "red",
                }
                color = status_colors.get(task["status"], "gray")

                with st.expander(
                    f"[{task['status'].upper()}] {task['type']} - {task['created_at'].strftime('%H:%M:%S')}",
                    expanded=(task["status"] == "running"),
                ):
                    st.write(f"**Instruction:** {task['prompt']}")
                    st.write(f"**Status:** :{color}[{task['status']}]")

                    if task.get("trigger_type") == "scheduled":
                        st.write(
                            f"⏱️ **Period:** Every {task.get('interval_minutes', '-')} minute(s)."
                        )
                        if task["status"] == "pending" and task.get("schedule_time"):
                            st.write(
                                f"⏳ **Next Run:** {task['schedule_time'].strftime('%H:%M:%S')}"
                            )

                    if task.get("completed_at"):
                        st.write(
                            f"**Completed At:** {task['completed_at'].strftime('%H:%M:%S')}"
                        )

                    if task["status"] == "completed":
                        st.success("Task completed successfully.")
                        st.markdown(f"**Result:**\n\n```text\n{task['result']}\n```")
                    elif task["status"] == "failed":
                        st.error(f"Task failed: {task['error']}")

            if any(t["status"] in ["completed", "failed"] for t in tasks):
                if st.button("🗑️ Clear History"):
                    clear_completed_tasks()
                    st.rerun()
