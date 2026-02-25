import os, sys
import streamlit as st
from app.lang import LANG
import config
from services.llm_service import chat_completion


def t(key):
    lang = st.session_state.get("lang", "tr")
    return LANG.get(lang, LANG["tr"]).get(key, key)


def render_swarm_studio_page():
    st.markdown(
        f'<div class="pg-header"><div class="pg-title pg-title-kg">🧩 Swarm Studio (Multi-Agent Flow Management)</div><div class="pg-sub">Define your own AI agents without writing code and chain them together to create pipeline workflows.</div></div>',
        unsafe_allow_html=True,
    )

    if "custom_agents" not in st.session_state:
        st.session_state.custom_agents = [
            {
                "id": "agent_analyst",
                "name": "Analyst Agent",
                "prompt": "You are an analytical expert. Examine the provided text and structure it by making numerical inferences.",
                "tools": {"web_search": False, "data_analyst": True},
            },
            {
                "id": "agent_translator",
                "name": "Translator Agent",
                "prompt": "You are a text translator. Translate the incoming text into English in a fluent and technical language.",
                "tools": {"web_search": False, "data_analyst": False},
            },
            {
                "id": "agent_critic",
                "name": "Critic Agent",
                "prompt": "You are a ruthless critic. Find logical errors and deficiencies in the incoming text, and give directives to make it better.",
                "tools": {"web_search": True, "data_analyst": False},
            },
        ]

    if "pipeline_steps" not in st.session_state:
        st.session_state.pipeline_steps = []

    tab1, tab2, tab3 = st.tabs(
        [
            "🚀 Pipeline Builder",
            "🤖 Custom Agents Factory",
            "⚙️ Run Flow",
        ]
    )

    with tab2:
        st.markdown("#### Define New Agent")
        with st.form("new_agent_form"):
            new_name = st.text_input("Agent Name", placeholder="E.g.: Researcher Agent")
            new_prompt = st.text_area(
                "System Prompt (What is the agent's role?)",
                placeholder="You are a researcher. Examine the incoming topic deeply...",
            )
            st.markdown("**Agent Tools (Capabilities)**")
            can_web = st.checkbox("🌐 Can Make Web Searches", value=False)
            can_db = st.checkbox("📊 Can Read Database (SQL)", value=False)

            submit_agent = st.form_submit_button("Save Agent")

            if submit_agent and new_name and new_prompt:
                agent_id = f"agent_{new_name.lower().replace(' ', '_')}"
                st.session_state.custom_agents.append(
                    {
                        "id": agent_id,
                        "name": new_name,
                        "prompt": new_prompt,
                        "tools": {"web_search": can_web, "data_analyst": can_db},
                    }
                )
                st.success(f"{new_name} added successfully!")

        st.markdown("#### Existing Agents")
        for agent in st.session_state.custom_agents:
            tools = agent.get("tools", {})
            badges = []
            if tools.get("web_search"):
                badges.append("🌐 Web")
            if tools.get("data_analyst"):
                badges.append("📊 SQL")

            st.markdown(f"**🕵️ {agent['name']}** {' '.join([f'`{b}`' for b in badges])}")
            st.caption(agent["prompt"])
            st.divider()

    with tab1:
        st.markdown("#### Create Agent Pipeline")
        st.info(
            "Every agent you add to the flow will use the output of the previous agent as its input. The first agent will use your main prompt."
        )

        agent_names = [a["name"] for a in st.session_state.custom_agents]

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_agent_name = st.selectbox("Add Agent to Flow", agent_names)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add Step"):
                st.session_state.pipeline_steps.append(selected_agent_name)
                st.rerun()

        st.markdown("#### Current Flow:")
        if not st.session_state.pipeline_steps:
            st.warning("The flow is currently empty. Please add agents.")
        else:
            for idx, step_name in enumerate(st.session_state.pipeline_steps):
                c1, c2 = st.columns([4, 1])
                with c1:
                    if idx == 0:
                        st.markdown(
                            f"🟢 **Step {idx+1}:** {step_name} *(Input: User Question)*"
                        )
                    else:
                        st.markdown(
                            f"🔵 **Step {idx+1}:** {step_name} *(Input: Step {idx}'s Output)*"
                        )
                with c2:
                    if st.button("🗑️ Delete", key=f"del_step_{idx}"):
                        st.session_state.pipeline_steps.pop(idx)
                        st.rerun()

            if st.button("🧹 Clear Entire Flow"):
                st.session_state.pipeline_steps = []
                st.rerun()

    with tab3:
        st.markdown("#### Run Custom Swarm Flow")

        if not st.session_state.pipeline_steps:
            st.error("Please add at least 1 agent from 'Pipeline Builder' first.")
        else:
            flow_prompt = st.text_area(
                "Main Input (Starter message for the first agent)", height=150
            )
            if st.button("▶️ Trigger Architecture (Run Pipeline)", type="primary"):
                if flow_prompt:
                    current_input = flow_prompt

                    st.markdown("### 📡 Live Operation Log")
                    log_area = st.empty()

                    progress_text = ""

                    # Pipeline Execution Loop
                    try:
                        for idx, step_name in enumerate(
                            st.session_state.pipeline_steps
                        ):
                            agent_config = next(
                                (
                                    a
                                    for a in st.session_state.custom_agents
                                    if a["name"] == step_name
                                ),
                                None,
                            )

                            progress_text += (
                                f"\n\n⏳ **Step {idx+1} ({step_name}) is running...**"
                            )
                            log_area.markdown(progress_text)

                            # Tool Execution Pre-computation
                            tools = agent_config.get("tools", {})
                            additional_context = ""

                            if tools.get("web_search"):
                                progress_text += f"\n🔍 *{step_name} is actively scanning the internet...*"
                                log_area.markdown(progress_text)
                                try:
                                    from duckduckgo_search import DDGS

                                    with DDGS() as ddgs:
                                        # Use the first 200 chars as query
                                        results = list(
                                            ddgs.text(
                                                current_input[:200], max_results=3
                                            )
                                        )
                                        additional_context += (
                                            "WEB SEARCH RESULTS:\n"
                                            + "\n".join([r["body"] for r in results])
                                            + "\n\n"
                                        )
                                except Exception as e:
                                    additional_context += f"Web search error: {e}\n\n"

                            if tools.get("data_analyst"):
                                progress_text += f"\n📈 *{step_name} is performing database analysis (SQL)...*"
                                log_area.markdown(progress_text)
                                try:
                                    from core.data_agent import dynamic_data_agent

                                    db_result = dynamic_data_agent(
                                        current_input, st.session_state.selected_model
                                    )
                                    additional_context += (
                                        "DATABASE ANALYSIS RESULTS:\n"
                                        + db_result
                                        + "\n\n"
                                    )
                                except Exception:
                                    pass

                            sys_prompt = agent_config["prompt"]
                            if additional_context:
                                sys_prompt += f"\n\n[SYSTEM TOOL OUTPUTS (Reply using these data)]\n{additional_context}"

                            messages = [
                                {"role": "system", "content": sys_prompt},
                                {
                                    "role": "user",
                                    "content": f"Process the data/text below:\n\n{current_input}",
                                },
                            ]

                            model = st.session_state.selected_model
                            # Use default if custom unavailable
                            response = chat_completion(
                                messages=messages,
                                model=model,
                                temperature=0.5,
                                max_tokens=4000,
                            )

                            current_input = response  # Input passed to next

                            progress_text += f"\n✅ **{step_name} Output:**\n```\n{response[:300]}...\n```\n"
                            log_area.markdown(progress_text)

                        st.success("🎉 Flow Completed Successfully!")
                        st.markdown("### 🏁 Final Result:")
                        st.markdown(
                            f"<div class='glass' style='padding:20px'>{current_input}</div>",
                            unsafe_allow_html=True,
                        )

                    except Exception as e:
                        st.error(f"Error During Flow: {e}")
                else:
                    st.error("Please enter a starter text.")
