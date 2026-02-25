import os, sys
import re

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import streamlit as st
import config
from app.lang import LANG


def t(key):
    lang = st.session_state.get("lang", "tr")
    return LANG.get(lang, LANG["tr"]).get(key, key)


from services import chat_service, lightrag_service, llm_service, supabase_service
from utils.helpers import count_words
from app.templates import get_template_list
import re


def _render_pdf_viewer(filename):
    import base64

    uid = (
        st.session_state.workspace_id
        if st.session_state.get("workspace_id")
        else (
            st.session_state.user.id
            if hasattr(st.session_state.get("user"), "id")
            else "guest"
        )
    )
    doc_path = os.path.join(config.LIGHTRAG_WORK_DIR, "documents", f"{uid}_{filename}")

    if os.path.exists(doc_path) and filename.lower().endswith(".pdf"):
        try:
            with open(doc_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0" width="100%" height="700" type="application/pdf" style="border-radius:12px;border:1px solid rgba(255,255,255,0.1);"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception:
            st.error("Viewer error.")
    else:
        st.info("PDF Viewer: Only local files in PDF format are supported.")


def _render_canvas_interface():
    st.markdown(
        '<div class="pg-header"><div class="pg-title pg-title-chat">🎨 Interactive Workspace (Canvas)</div></div>',
        unsafe_allow_html=True,
    )
    content = st.session_state.get("canvas_content", "")

    # Show highlight or Edit
    mode = st.radio(
        "View Mode",
        ["Preview", "Edit"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if mode == "Edit":
        new_content = st.text_area(
            "Content Editor (Markdown/Code)",
            value=content,
            height=600,
            label_visibility="collapsed",
        )
        if new_content != content:
            st.session_state.canvas_content = new_content
            # Auto-save changes dynamically
    else:
        st.markdown(
            f'<div style="max-height: 600px; overflow-y: auto; padding: 10px; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;">',
            unsafe_allow_html=True,
        )
        st.markdown(content)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🪄 Rewrite with AI (Revise)"):
        # Put the user instruction to the main chat
        st.session_state.messages.append(
            {
                "role": "user",
                "content": f"Improve this content from the Canvas:\n\n```\n{content}\n```\n\nMake it more professional.",
            }
        )
        st.session_state.conversations[st.session_state.current_conv] = (
            st.session_state.messages
        )
        st.rerun()


def render_chat_page():
    st.markdown(
        f'<div class="pg-header"><div class="pg-title pg-title-chat">{t("chat_title")}</div><div class="pg-sub">{st.session_state.rag_mode} · {st.session_state.selected_model.split("/")[-1]}</div></div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.has_documents and not st.session_state.messages:
        _render_welcome()
        return

    col1, col2 = st.columns([1, 5])
    with col1:
        show_pdf = st.toggle(
            "📖 Show PDF",
            value=st.session_state.get("show_pdf_viewer", False),
            key="show_pdf_viewer",
        )
    with col2:
        show_canvas = st.toggle(
            "🎨 Workspace (Canvas)",
            value=st.session_state.get("show_canvas_viewer", False),
            key="show_canvas_viewer",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if show_canvas and st.session_state.get("canvas_content"):
        left, right = st.columns([1, 1], gap="large")
        with left:
            _render_chat_interface()
        with right:
            _render_canvas_interface()
    elif show_pdf and st.session_state.current_doc_id:
        current_doc = next(
            (
                d
                for d in st.session_state.documents
                if d["id"] == st.session_state.current_doc_id
            ),
            None,
        )
        if current_doc:
            left, right = st.columns([1, 1], gap="large")
            with left:
                st.markdown(f"#### 📄 {current_doc['filename']}")
                _render_pdf_viewer(current_doc["filename"])
            with right:
                _render_chat_interface()
        else:
            _render_chat_interface()
    else:
        _render_chat_interface()


def _render_chat_interface():
    import streamlit.components.v1 as components

    components.html(
        """
    <script>
    const doc = window.parent.document;
    if (!doc.getElementById('lunartech_shortcuts')) {
        const s = doc.createElement('style');
        s.id = 'lunartech_shortcuts';
        doc.head.appendChild(s);
        doc.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const btns = Array.from(doc.querySelectorAll('button'));
                const newChat = btns.find(b => b.innerText.includes('Yeni Sohbet'));
                if (newChat) newChat.click();
            }
        });
    }
    </script>
    """,
        height=0,
        width=0,
    )

    # --- Export Toolbar ---
    if st.session_state.messages:
        with st.expander("📥 Export Current Chat as Report", expanded=False):
            c1, c2, c3 = st.columns(3)
            full_text = "\n\n".join(
                [
                    f"{'User' if m['role'] == 'user' else 'Assistant'}:\n{m['content']}"
                    for m in st.session_state.messages
                    if m["role"] in ["user", "assistant"]
                ]
            )

            try:
                from utils.exporter import (
                    export_pdf,
                    export_docx,
                    extract_tables_to_excel,
                )

                pdf_data = export_pdf(full_text)
                c1.download_button(
                    "📄 Download PDF",
                    data=pdf_data,
                    file_name="LunarTech_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

                docx_data = export_docx(full_text)
                c2.download_button(
                    "📝 Download Word (DOCX)",
                    data=docx_data,
                    file_name="LunarTech_Report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

                excel_data = extract_tables_to_excel(full_text)
                if excel_data:
                    c3.download_button(
                        "📊 Excel (Tables)",
                        data=excel_data,
                        file_name="LunarTech_Data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                else:
                    c3.button(
                        "📊 Excel (No Data)", disabled=True, use_container_width=True
                    )
            except Exception as e:
                st.error(f"Export module could not be loaded: {e}")

    for i, msg in enumerate(st.session_state.messages):
        av = "🧑‍💻" if msg["role"] == "user" else "🌙"
        with st.chat_message(msg["role"], avatar=av):
            if isinstance(msg["content"], str):
                st.markdown(msg["content"])
            elif isinstance(msg["content"], list):
                for part in msg["content"]:
                    if part.get("type") == "text":
                        st.markdown(part["text"])
                    elif part.get("type") == "image_url":
                        st.image(part["image_url"]["url"], width=250)

            # Micro-Export
            if msg["role"] == "assistant" and isinstance(msg["content"], str):
                c1, c2 = st.columns([1, 4])
                with c1:
                    try:
                        from utils.exporter import export_pdf

                        pdf_data = export_pdf(
                            msg["content"], title="LunarTech AI - Selected Response"
                        )
                        st.download_button(
                            "📥 Download PDF",
                            data=pdf_data,
                            file_name=f"LunarTech_Resp_{i}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{i}",
                        )
                    except Exception:
                        pass

                # Canvas'a aktarım butonu (Eğer kod veya uzun metin varsa)
                if len(msg["content"]) > 500 or "```" in msg["content"]:
                    with c2:

                        def open_in_canvas(content):
                            st.session_state.canvas_content = content
                            st.session_state.show_canvas_viewer = True

                        st.button(
                            (
                                "🎨 Çalışma Alanında (Canvas) Aç"
                                if st.session_state.get("lang") == "tr"
                                else "🎨 Open in Canvas"
                            ),
                            key=f"canvas_btn_{i}",
                            on_click=open_in_canvas,
                            args=(msg["content"],),
                        )

    # Voice Assistant Input
    prompt = None
    chat_val = st.chat_input(t("chat_input"))

    with st.popover("🎙️ Advanced Modes & Media", use_container_width=True):
        dev_mode = st.toggle(
            "💻 Developer Agent (Dev Mode)",
            value=st.session_state.get("dev_mode", False),
            help="Grants full access to the system, allowing reading and modifying code files and running terminal commands.",
        )
        st.session_state.dev_mode = dev_mode

        realtime_voice = st.toggle(
            "📞 Live Voice Chat (WebSocket)",
            value=st.session_state.get("realtime_voice", False),
            help="Starts a seamless, real-time phone call with LunarTech.",
        )
        st.session_state.realtime_voice = realtime_voice

        data_analyst_mode = st.toggle(
            "📊 Data Analyst (Table & SQL) Mode",
            value=st.session_state.get("data_analyst_mode", False),
            help="Allows questioning the database records directly instead of uploaded documents to get Excel/Chart outputs.",
        )
        st.session_state.data_analyst_mode = data_analyst_mode
        st.divider()
        audio_val = st.audio_input("🎤 Speak with Microphone")
        image_val = st.file_uploader(
            "📷 Upload Image (Chart/Table)", type=["png", "jpg", "jpeg"]
        )
        csv_file_val = None
        if st.session_state.get("data_analyst_mode", False):
            csv_file_val = st.file_uploader(
                "📂 Upload Custom Data (Excel/CSV)",
                type=["csv", "xlsx", "xls"],
                help="Instant chart generation using Pandas",
            )

        if audio_val and not chat_val:
            with st.spinner("Transcribing audio..."):
                import speech_recognition as sr

                r = sr.Recognizer()
                with sr.AudioFile(audio_val) as source:
                    audio_data = r.record(source)
                    try:
                        prompt = r.recognize_google(audio_data, language="en-US")
                    except Exception as e:
                        st.error("Audio could not be transcribed to text successfully.")
            st.session_state.audio_key = str(audio_val)  # prevent re-triggering

    if st.session_state.get("realtime_voice", False):
        import streamlit.components.v1 as components

        st.info(
            "🟢 Live Voice Connection is Active. As you speak, your voice is transmitted via WebSocket to the backend."
        )
        components.html(
            """
            <div style="font-family: sans-serif; padding: 10px; border: 1px solid #334155; border-radius: 8px; background: #0f172a; color: #f8fafc;">
                <h4 style="margin-top: 0; color: #38bdf8;">🎙️ WebSocket Communication Terminal</h4>
                <div id="status" style="margin-bottom: 10px; color: #fbbf24;">Connecting...</div>
                <div id="logs" style="height: 100px; overflow-y: auto; font-size: 12px; color: #94a3b8; background: #1e293b; padding: 5px; border-radius: 4px;"></div>
                <button id="stopBtn" style="margin-top:10px; padding: 5px 10px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">Disconnect</button>
            </div>
            
            <script>
                const statusDiv = document.getElementById('status');
                const logsDiv = document.getElementById('logs');
                const stopBtn = document.getElementById('stopBtn');
                
                let ws = new WebSocket("ws://localhost:8001/ws/voice");
                let mediaRecorder;
                let audioChunks = [];
                let stream;
                
                function log(msg) {
                    logsDiv.innerHTML += `<div>[${new Date().toLocaleTimeString()}] ${msg}</div>`;
                    logsDiv.scrollTop = logsDiv.scrollHeight;
                }
                
                ws.onopen = () => {
                    statusDiv.innerText = "Connected (Waiting for Data)";
                    statusDiv.style.color = "#4ade80";
                    log("WebSocket connection established.");
                    
                    navigator.mediaDevices.getUserMedia({ audio: true }).then(s => {
                        stream = s;
                        mediaRecorder = new MediaRecorder(stream);
                        mediaRecorder.ondataavailable = e => {
                            if (e.data.size > 0) {
                                let reader = new FileReader();
                                reader.readAsDataURL(e.data);
                                reader.onloadend = function() {
                                    let base64data = reader.result.split(',')[1];
                                    if(ws.readyState === WebSocket.OPEN) {
                                        ws.send(JSON.stringify({audio: base64data}));
                                    }
                                }
                            }
                        };
                        mediaRecorder.start(2000); // Send chunks every 2 seconds
                        log("Microphone transmission started (1 Packet per Second).");
                    }).catch(err => {
                        log("Microphone error: " + err);
                    });
                };
                
                ws.onmessage = (event) => {
                    log("Server: " + event.data);
                };
                
                ws.onclose = () => {
                    statusDiv.innerText = "Disconnected";
                    statusDiv.style.color = "#ef4444";
                    if(mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
                    if(stream) stream.getTracks().forEach(t => t.stop());
                    log("WebSocket connection closed.");
                };
                
                stopBtn.onclick = () => {
                    ws.close();
                };
            </script>
            """,
            height=250,
        )

    if chat_val:
        prompt = chat_val

    if csv_file_val and st.session_state.get("data_analyst_mode", False):
        import pandas as pd

        try:
            if csv_file_val.name.endswith(".csv"):
                df = pd.read_csv(csv_file_val)
            else:
                df = pd.read_excel(csv_file_val)
            st.session_state.data_analyst_csv_payload = f"File: {csv_file_val.name}\n\nColumns: {list(df.columns)}\nData Types:\n{df.dtypes.to_string()}\nRow Count: {len(df)}\n\nSummary Statistics:\n{df.describe().to_markdown()}\n\nSample Data:\n{df.head(10).to_markdown()}"
            if not prompt:
                prompt = f"Extract a general business intelligence (BI) summary from the uploaded data table '{csv_file_val.name}'. Generate a chart if necessary."
        except Exception as e:
            st.error(f"Error! Excel/CSV file could not be read: {e}")

    if prompt or image_val or csv_file_val:
        if not prompt:
            prompt = "Analyze this document in detail."

        # Build multimodal payload if image is present
        content_payload = prompt
        if image_val:
            import base64

            base64_image = base64.b64encode(image_val.getvalue()).decode("utf-8")
            img_format = image_val.name.split(".")[-1].lower()
            if img_format == "jpg":
                img_format = "jpeg"
            content_payload = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{img_format};base64,{base64_image}"
                    },
                },
            ]

        st.session_state.messages.append({"role": "user", "content": content_payload})
        st.session_state.conversations[st.session_state.current_conv] = (
            st.session_state.messages
        )
        st.session_state.total_queries += 1
        with st.chat_message("user", avatar="🧑‍💻"):
            if image_val:
                st.image(image_val, width=250)
            st.markdown(prompt)
        try:
            uid = (
                st.session_state.workspace_id
                if st.session_state.get("workspace_id")
                else (
                    st.session_state.user.id
                    if hasattr(st.session_state.get("user"), "id")
                    else None
                )
            )
            supabase_service.save_chat_message(
                role="user",
                content=prompt,
                document_id=st.session_state.current_doc_id,
                user_id=uid,
            )
        except Exception:
            pass

        with st.chat_message("assistant", avatar="🌙"):
            import time

            start_t = time.time()
            status_obj = None
            resp_area = st.empty()
            full = ""
            try:
                echarts_json = None

                if st.session_state.get("dev_mode", False):
                    # --- Dev Mode ---
                    from core.dev_agent import (
                        DEV_TOOLS_SCHEMA,
                        read_file,
                        write_file,
                        execute_bash,
                    )
                    import json

                    status_obj = st.status(
                        "💻 Autonomous Developer activated, examining system...",
                        expanded=True,
                    )

                    messages_for_dev = [
                        {
                            "role": "system",
                            "content": "You are LunarTech AI's autonomous Core Developer. You have permissions to read files, write code, and use the terminal. Code the given task completely. When the task is completed, explain what you did to the user nicely using Markdown.",
                        }
                    ] + st.session_state.messages

                    current_msg = chat_service.chat_completion(
                        messages=messages_for_dev,
                        model=st.session_state.selected_model,
                        temperature=0.2,
                        tools=DEV_TOOLS_SCHEMA,
                        use_cache=False,
                    )

                    iterations = 0
                    max_iterations = 8  # Limit recursive calls

                    while (
                        hasattr(current_msg, "tool_calls")
                        and current_msg.tool_calls
                        and iterations < max_iterations
                    ):
                        iterations += 1
                        status_obj.write(
                            f"🔄 Tool Call ({iterations}): LLM triggering {len(current_msg.tool_calls)} function(s)."
                        )

                        tool_calls_dict = []
                        for tc in current_msg.tool_calls:
                            tool_calls_dict.append(
                                {
                                    "id": tc.id,
                                    "type": tc.type,
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments,
                                    },
                                }
                            )

                        messages_for_dev.append(
                            {
                                "role": "assistant",
                                "content": current_msg.content or "",
                                "tool_calls": tool_calls_dict,
                            }
                        )

                        for tc in current_msg.tool_calls:
                            func_name = tc.function.name
                            try:
                                args = json.loads(tc.function.arguments)
                                if func_name == "read_file":
                                    status_obj.write(
                                        f"📄 Reading: `{args.get('filepath')}`"
                                    )
                                    res = read_file(args.get("filepath"))
                                elif func_name == "write_file":
                                    status_obj.write(
                                        f"✏️ Writing: `{args.get('filepath')}`"
                                    )
                                    res = write_file(
                                        args.get("filepath"), args.get("content")
                                    )
                                elif func_name == "execute_bash":
                                    status_obj.write(
                                        f"🖥️ Terminal: `{args.get('command')}`"
                                    )
                                    res = execute_bash(args.get("command"))
                                else:
                                    res = f"Unknown function: {func_name}"
                            except Exception as e:
                                res = f"Error: {str(e)}"

                            messages_for_dev.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tc.id,
                                    "name": func_name,
                                    "content": str(res),
                                }
                            )

                        current_msg = chat_service.chat_completion(
                            messages=messages_for_dev,
                            model=st.session_state.selected_model,
                            temperature=0.2,
                            tools=DEV_TOOLS_SCHEMA,
                            use_cache=False,
                        )

                    status_obj.update(
                        label=f"Autonomous Development Completed ({iterations} rounds)",
                        state="complete",
                        expanded=False,
                    )
                    full = (
                        current_msg.content
                        if not hasattr(current_msg, "tool_calls")
                        else (current_msg.content or "All tools executed.")
                    )

                    chunk_size = 15
                    for j in range(0, len(full), chunk_size):
                        resp_area.markdown(full[: j + chunk_size] + "▌")
                        time.sleep(0.01)
                    resp_area.markdown(full)

                elif st.session_state.get("data_analyst_mode", False):
                    # --- Data Analyst Mode --
                    from core.data_agent import dynamic_data_agent

                    status_obj = st.status(
                        "Data is being analyzed, Pandas/SQL metrics are being calculated...",
                        expanded=True,
                    )
                    raw_response = dynamic_data_agent(
                        prompt if isinstance(prompt, str) else str(prompt),
                        st.session_state.selected_model,
                        csv_data=st.session_state.get("data_analyst_csv_payload"),
                    )
                    status_obj.update(
                        label="Analysis Completed", state="complete", expanded=False
                    )

                    echarts_match = re.search(
                        r"<echarts>(.*?)</echarts>",
                        raw_response,
                        re.DOTALL | re.IGNORECASE,
                    )
                    if echarts_match:
                        echarts_json = echarts_match.group(1).strip()
                        full = raw_response.replace(echarts_match.group(0), "").strip()
                    else:
                        full = raw_response

                    # Pseudo streaming
                    chunk_size = 15
                    for j in range(0, len(full), chunk_size):
                        resp_area.markdown(full[: j + chunk_size] + "▌")
                        time.sleep(0.01)
                    resp_area.markdown(full)

                    if echarts_json:
                        try:
                            import json
                            from streamlit_echarts import st_echarts

                            chart_options = json.loads(echarts_json)
                            st_echarts(options=chart_options, height="450px")
                        except Exception as e:
                            st.error(f"Chart could not be drawn: {e}")

                elif re.search(
                    r"(?i)^(?:create a handbook|handbook olu[sş]tur|kitap yaz|el kitab[ıi] yaz)(?:\s+(?:on|hakk[ıi]nda|for|i[cç]in|about))?\s*(.*)",
                    prompt,
                ):
                    # --- Handbook Intent Router (Engineering Assignment) ---
                    from core.longwriter import generate_handbook

                    match = re.search(
                        r"(?i)^(?:create a handbook|handbook olu[sş]tur|kitap yaz|el kitab[ıi] yaz)(?:\s+(?:on|hakk[ıi]nda|for|i[cç]in|about))?\s*(.*)",
                        prompt,
                    )
                    topic = match.group(1).strip() if match.group(1) else prompt

                    status_obj = st.status(
                        f"📚 A 20,000-word handbook on '{topic}' is being generated. This may take a few minutes...",
                        expanded=True,
                    )

                    def _update_progress(current, total, message, word_count):
                        status_obj.write(f"[{current}/{total}] {message}")

                    # Placeholder for full context loading if documents exist
                    context_text = "Scanning reference documents..."
                    if st.session_state.has_documents:
                        context_text = lightrag_service.query(
                            topic, mode=st.session_state.rag_mode
                        )

                    handbook_result = generate_handbook(
                        topic=topic,
                        context=context_text,
                        target_words=20000,
                        model=st.session_state.selected_model,
                        progress_callback=_update_progress,
                    )

                    status_obj.update(
                        label="Handbook Generation Completed!",
                        state="complete",
                        expanded=False,
                    )

                    # Assemble sections
                    full = f"# {topic} - Comprehensive Handbook\n\n"
                    for sec in handbook_result.get("sections", []):
                        full += f"## {sec.get('title')}\n\n{sec.get('content')}\n\n"

                    # Pseudo streaming output to chat
                    chunk_size = 50
                    for j in range(0, len(full), chunk_size):
                        resp_area.markdown(full[: j + chunk_size] + "▌")
                        time.sleep(0.005)
                    resp_area.markdown(full)

                else:
                    # --- Standard RAG Swarm Mode ---
                    for item in chat_service.stream_answer(
                        question=prompt,
                        chat_history=st.session_state.messages[:-1],
                        model=st.session_state.selected_model,
                        has_documents=st.session_state.has_documents,
                        rag_mode=st.session_state.rag_mode,
                        temperature=st.session_state.temperature,
                        max_tokens=st.session_state.max_tokens,
                        custom_prompt=st.session_state.custom_prompt,
                        auto_rag=st.session_state.get("auto_rag", False),
                        use_persona=st.session_state.get("use_persona", False),
                    ):
                        if isinstance(item, dict):
                            t_item = item.get("type", "chunk")
                            text_val = item.get("text", "")
                            if t_item == "status":
                                st_state = item.get("state")
                                if st_state == "running":
                                    status_obj = st.status(text_val, expanded=True)
                                elif st_state == "update" and status_obj:
                                    status_obj.write(text_val)
                                elif st_state == "complete" and status_obj:
                                    status_obj.update(
                                        label=text_val, state="complete", expanded=False
                                    )
                            elif t_item == "chunk":
                                full += text_val
                                resp_area.markdown(full + "▌")
                        else:
                            full += str(item)
                            resp_area.markdown(full + "▌")
                    resp_area.markdown(full)
                elapsed = time.time() - start_t
                st.toast(f"Response generated in {elapsed:.1f} seconds.", icon="⏱️")
            except Exception as e:
                full = f"{t('error_prefix')}: {str(e)}"
                st.error(full)

        st.session_state.messages.append({"role": "assistant", "content": full})
        st.session_state.conversations[st.session_state.current_conv] = (
            st.session_state.messages
        )
        try:
            uid = (
                st.session_state.workspace_id
                if st.session_state.get("workspace_id")
                else (
                    st.session_state.user.id
                    if hasattr(st.session_state.get("user"), "id")
                    else None
                )
            )
            supabase_service.save_chat_message(
                role="assistant",
                content=full,
                document_id=st.session_state.current_doc_id,
                user_id=uid,
            )

            # Save estimated token usage
            if uid:
                estimated_tokens = int((len(prompt) + len(full)) / 4)
                supabase_service.save_token_usage(
                    user_id=uid,
                    model=st.session_state.selected_model,
                    tokens=estimated_tokens,
                )
        except Exception:
            pass

        # Text-To-Speech (Seslendir) Butonu
        if full and not full.startswith(t("error_prefix")):
            col1, col2 = st.columns([2, 5])
            if col1.button(
                "🔊 Read Aloud", key=f"tts_{st.session_state.total_queries}"
            ):
                with st.spinner("Synthesizing audio..."):
                    from gtts import gTTS
                    import io

                    # Limit TTS strictly to raw textual data by stripping Markdown/Emojis
                    clean_tts = re.sub(r"[*#\_~]", "", full).strip()[
                        :1000
                    ]  # Limiting to 1000 chars to avoid lag
                    tts = gTTS(text=clean_tts, lang="tr")
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    st.audio(fp.getvalue(), format="audio/mp3")

        # Follow-up soru önerileri
        if full and not full.startswith(t("error_prefix")):
            followups = chat_service.get_followup_questions(
                prompt, full, st.session_state.selected_model
            )
            if followups:
                st.markdown(
                    f'<div class="glass" style="margin-top:1rem;padding:.8rem 1rem"><div style="color:#818cf8;font-weight:600;font-size:.8rem;margin-bottom:.5rem">{t("followup_title")}</div></div>',
                    unsafe_allow_html=True,
                )
                for fq in followups:
                    if st.button(f"💡 {fq}", key=f"fq_{hash(fq)}"):
                        st.session_state.messages.append(
                            {"role": "user", "content": fq}
                        )
                        st.session_state.conversations[
                            st.session_state.current_conv
                        ] = st.session_state.messages
                        st.rerun()


def _render_welcome():
    st.markdown(
        f'<div class="welcome"><h2>{t("welcome_title")}</h2><p>{t("welcome_desc")}</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    feats = [
        ("📄", "PDF", t("upload_feat")),
        ("🧠", "KG", t("kg_feat")),
        ("💬", t("chat"), t("chat_feat")),
        ("📚", "Handbook", t("hb_feat")),
    ]
    cols = st.columns(4)
    for col, (ic, ti, de) in zip(cols, feats):
        with col:
            st.markdown(
                f'<div class="feat"><div class="feat-icon">{ic}</div><div class="feat-title">{ti}</div><div class="feat-desc">{de}</div></div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════
# PAGE: HANDBOOK
# ══════════════════════════════════════════════════════════
