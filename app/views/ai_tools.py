import os, sys

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


from services import llm_service
from core import smart_features, agents
import json


def render_ai_tools_page():
    st.markdown(
        f'<div class="pg-header"><div class="pg-title" style="background:linear-gradient(135deg,#f472b6,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{t("ai_tools")}</div><div class="pg-sub">28 AI-powered tools</div></div>',
        unsafe_allow_html=True,
    )
    doc_names = [d["filename"] for d in st.session_state.documents]
    model = st.session_state.selected_model
    if "session_notes" not in st.session_state:
        st.session_state.session_notes = []
    if "favorites" not in st.session_state:
        st.session_state.favorites = []

    cat = st.selectbox(
        t("tool_category"),
        [
            t("grp_doc_intel"),
            t("grp_writing"),
            t("grp_analysis"),
            t("grp_reporting"),
            t("grp_ux"),
        ],
        key="tool_cat",
    )

    # ── CATEGORY 1: Document Intelligence ──
    if cat == t("grp_doc_intel"):
        tabs = st.tabs(
            [
                t("auto_summary"),
                t("key_findings"),
                t("quiz_generator"),
                t("doc_compare"),
                t("health_score"),
                t("sentiment"),
                t("citation_gen"),
                t("doc_timeline"),
            ]
        )
        with tabs[0]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="sum_doc")
                if st.button(t("run_btn"), key="run_sum", type="primary"):
                    with st.spinner(t("generating")):
                        result = auto_summarize(_get_doc_text(sel), model)
                    st.markdown(
                        f'<div class="glass">{result}</div>', unsafe_allow_html=True
                    )
            else:
                st.info(t("no_doc_selected"))
        with tabs[1]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="find_doc")
                if st.button(t("run_btn"), key="run_find", type="primary"):
                    with st.spinner(t("generating")):
                        result = extract_key_findings(_get_doc_text(sel), model)
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[2]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="quiz_doc")
                qc1, qc2, qc3 = st.columns(3)
                with qc1:
                    qt_map = {
                        t("quiz_mc"): "multiple choice",
                        t("quiz_open"): "open ended",
                        t("quiz_tf"): "true/false",
                    }
                    quiz_type = qt_map[
                        st.selectbox(t("quiz_type"), list(qt_map.keys()))
                    ]
                with qc2:
                    quiz_count = st.number_input(t("quiz_count"), 3, 20, 5)
                with qc3:
                    df_map = {
                        t("diff_easy"): "beginner",
                        t("diff_medium"): "intermediate",
                        t("diff_hard"): "advanced",
                    }
                    diff = df_map[st.selectbox(t("quiz_diff"), list(df_map.keys()))]
                if st.button(t("run_btn"), key="run_quiz", type="primary"):
                    with st.spinner(t("generating")):
                        result = generate_quiz(
                            _get_doc_text(sel), quiz_count, quiz_type, diff, model
                        )
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[3]:
            if len(doc_names) >= 2:
                cc1, cc2 = st.columns(2)
                with cc1:
                    d1 = st.selectbox(t("select_doc"), doc_names, key="cmp1")
                with cc2:
                    d2 = st.selectbox(
                        t("select_doc2"),
                        doc_names,
                        key="cmp2",
                        index=min(1, len(doc_names) - 1),
                    )
                if st.button(t("run_btn"), key="run_cmp", type="primary"):
                    with st.spinner(t("generating")):
                        result = compare_documents(
                            _get_doc_text(d1), d1, _get_doc_text(d2), d2, model
                        )
                    st.markdown(result)
            else:
                st.info(f"📄 2+ {t('docs_label')}")
        with tabs[4]:  # Health score
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="hlth_doc")
                if st.button(t("run_btn"), key="run_hlth", type="primary"):
                    with st.spinner(t("generating")):
                        result = document_health_score(_get_doc_text(sel), model)
                    st.markdown(f"#### {t('health_result')}")
                    mc = st.columns(6)
                    labels = [
                        "readability",
                        "consistency",
                        "completeness",
                        "structure",
                        "clarity",
                        "total",
                    ]
                    tl = [
                        t("readability"),
                        t("consistency"),
                        t("completeness"),
                        t("structure"),
                        t("clarity"),
                        t("total"),
                    ]
                    for i, (k, lab) in enumerate(zip(labels, tl)):
                        with mc[i]:
                            st.metric(lab, result.get(k, 0))
                    st.markdown(f"**{t('grade')}:** {result.get('grade', '?')}")
                    for s in result.get("suggestions", []):
                        st.markdown(f"- 💡 {s}")
            else:
                st.info(t("no_doc_selected"))
        with tabs[5]:  # Sentiment
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="sent_doc")
                if st.button(t("run_btn"), key="run_sent", type="primary"):
                    with st.spinner(t("generating")):
                        result = sentiment_analysis(_get_doc_text(sel), model)
                    st.markdown(f"#### {t('sentiment_result')}")
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        st.metric("Sentiment", result.get("sentiment", "?"))
                    with sc2:
                        st.metric("Tone", result.get("tone", "?"))
                    with sc3:
                        st.metric("Emotion", result.get("emotion", "?"))
                    fc1, fc2 = st.columns(2)
                    with fc1:
                        st.progress(
                            result.get("formality_score", 0) / 100, t("formality")
                        )
                    with fc2:
                        st.progress(
                            result.get("subjectivity_score", 0) / 100, t("subjectivity")
                        )
                    st.markdown(result.get("analysis", ""))
            else:
                st.info(t("no_doc_selected"))
        with tabs[6]:  # Citation
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="cite_doc")
                if st.button(t("run_btn"), key="run_cite", type="primary"):
                    with st.spinner(t("generating")):
                        result = citation_generator(_get_doc_text(sel), sel, model)
                    st.markdown(f"#### {t('citation_result')}")
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[7]:  # Timeline
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="tl_doc")
                if st.button(t("run_btn"), key="run_tl", type="primary"):
                    with st.spinner(t("generating")):
                        result = document_timeline(_get_doc_text(sel), model)
                    st.markdown(f"#### {t('timeline_result')}")
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))

    # ── CATEGORY 2: Writing Assistant ──
    elif cat == t("grp_writing"):
        tabs = st.tabs(
            [
                t("writing_coach"),
                t("prompt_helper"),
                t("paraphrase"),
                t("translator_agent"),
            ]
        )
        with tabs[0]:
            coach_text = st.text_area(t("text_to_coach"), height=200, key="coach_txt")
            if st.button(
                t("run_btn"), key="run_coach", type="primary", disabled=not coach_text
            ):
                with st.spinner(t("generating")):
                    result = writing_coach(coach_text, model)
                st.markdown(result)
        with tabs[1]:
            pmp = st.text_area(t("prompt_to_improve"), height=150, key="pmp_txt")
            if st.button(t("run_btn"), key="run_pmp", type="primary", disabled=not pmp):
                with st.spinner(t("generating")):
                    result = prompt_helper(pmp, model)
                st.markdown(result)
        with tabs[2]:
            par_text = st.text_area(t("text_to_paraphrase"), height=200, key="par_txt")
            sty_map = {
                t("style_academic"): "academic",
                t("style_simple"): "simple",
                t("style_formal"): "formal",
                t("style_creative"): "creative",
                t("style_technical"): "technical",
                t("style_journalistic"): "journalistic",
            }
            par_style = sty_map[
                st.selectbox(t("paraphrase_style"), list(sty_map.keys()), key="par_sty")
            ]
            if st.button(
                t("run_btn"), key="run_par", type="primary", disabled=not par_text
            ):
                with st.spinner(t("generating")):
                    result = paraphrase_text(par_text, par_style, model)
                st.markdown(f"#### {t('paraphrase_result')}")
                st.markdown(result)
        with tabs[3]:
            tr_text = st.text_area(t("text_to_critique"), height=200, key="tr_text")
            tr_lang = st.selectbox(
                t("translate_to"),
                [
                    "English",
                    "English",
                    "Deutsch",
                    "Français",
                    "Español",
                    "日本語",
                    "中文",
                ],
                key="tr_lang",
            )
            if st.button(
                t("run_btn"), key="run_tr", type="primary", disabled=not tr_text
            ):
                with st.spinner(t("generating")):
                    result = translator_agent(tr_text, tr_lang, model)
                st.markdown(
                    f'<div class="glass">{result}</div>', unsafe_allow_html=True
                )

    # ── CATEGORY 3: Analysis & Search ──
    elif cat == t("grp_analysis"):
        tabs = st.tabs(
            [t("mind_map"), t("swot"), t("gap_analysis"), t("cross_ref"), t("glossary")]
        )
        with tabs[0]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="mm_doc")
                if st.button(t("run_btn"), key="run_mm", type="primary"):
                    with st.spinner(t("generating")):
                        mermaid_code = generate_mind_map(_get_doc_text(sel), model)
                    st.markdown(f"#### {t('mind_map_result')}")
                    st.code(mermaid_code, language="mermaid")
            else:
                st.info(t("no_doc_selected"))
        with tabs[1]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="swot_doc")
                if st.button(t("run_btn"), key="run_swot", type="primary"):
                    with st.spinner(t("generating")):
                        result = generate_swot(_get_doc_text(sel), model)
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[2]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="gap_doc")
                if st.button(t("run_btn"), key="run_gap", type="primary"):
                    with st.spinner(t("generating")):
                        result = gap_analysis(_get_doc_text(sel), model)
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[3]:
            if len(doc_names) >= 2:
                sel_docs = st.multiselect(
                    t("select_doc"), doc_names, default=doc_names[:2], key="xref_docs"
                )
                if st.button(
                    t("run_btn"),
                    key="run_xref",
                    type="primary",
                    disabled=len(sel_docs) < 2,
                ):
                    with st.spinner(t("generating")):
                        docs = [{"name": n, "text": _get_doc_text(n)} for n in sel_docs]
                        result = cross_reference_finder(docs, model)
                    st.markdown(result)
            else:
                st.info(f"📄 2+ {t('docs_label')}")
        with tabs[4]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="glos_doc")
                if st.button(t("run_btn"), key="run_glos", type="primary"):
                    with st.spinner(t("generating")):
                        terms = interactive_glossary(_get_doc_text(sel), model)
                    if terms:
                        st.markdown(
                            f"#### {t('glossary_result')} ({len(terms)} {t('term')})"
                        )
                        for tm in terms:
                            with st.expander(
                                f"📌 {tm.get('term', '?')} — _{tm.get('category', '')}_"
                            ):
                                st.markdown(tm.get("definition", ""))
                    else:
                        st.warning("No terms found")
            else:
                st.info(t("no_doc_selected"))

    # ── CATEGORY 4: Reporting ──
    elif cat == t("grp_reporting"):
        tabs = st.tabs(
            [
                t("report_builder"),
                t("pres_maker"),
                t("email_drafter"),
                t("content_planner"),
                t("templates"),
            ]
        )
        with tabs[0]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="rpt_doc")
                rt_map = {
                    t("rpt_analysis"): "analysis",
                    t("rpt_summary"): "summary",
                    t("rpt_executive"): "executive",
                    t("rpt_technical"): "technical",
                    t("rpt_progress"): "progress",
                }
                rpt_type = rt_map[
                    st.selectbox(t("report_type"), list(rt_map.keys()), key="rpt_type")
                ]
                if st.button(t("run_btn"), key="run_rpt", type="primary"):
                    with st.spinner(t("generating")):
                        result = auto_report_builder(
                            _get_doc_text(sel), rpt_type, model
                        )
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[1]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="pres_doc")
                sl_count = st.number_input(t("slide_count"), 5, 25, 10, key="sl_count")
                if st.button(t("run_btn"), key="run_pres", type="primary"):
                    with st.spinner(t("generating")):
                        result = presentation_maker(_get_doc_text(sel), sl_count, model)
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[2]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="eml_doc")
                em_map = {
                    t("email_summary"): "summary",
                    t("email_request"): "request",
                    t("email_followup"): "followup",
                    t("email_report"): "report",
                    t("email_announce"): "announcement",
                }
                eml_type = em_map[
                    st.selectbox(t("email_type"), list(em_map.keys()), key="eml_type")
                ]
                if st.button(t("run_btn"), key="run_eml", type="primary"):
                    with st.spinner(t("generating")):
                        result = email_drafter(_get_doc_text(sel), eml_type, model)
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[3]:
            cp_topic = st.text_input(t("plan_topic"), key="cp_topic")
            pt_map = {
                t("plan_blog"): "blog",
                t("plan_course"): "course",
                t("plan_training"): "training",
                t("plan_social"): "social",
            }
            cp_type = pt_map[
                st.selectbox(t("plan_type"), list(pt_map.keys()), key="cp_type")
            ]
            if st.button(
                t("run_btn"), key="run_cp", type="primary", disabled=not cp_topic
            ):
                with st.spinner(t("generating")):
                    ctx = _get_doc_text(doc_names[0]) if doc_names else ""
                    result = content_planner_agent(cp_topic, cp_type, ctx, model)
                st.markdown(result)
        with tabs[4]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="tpl_doc")
                tpl_list = get_template_list(st.session_state.lang)
                tpl_options = {
                    f"{v['icon']} {v['title']}": tid for tid, v in tpl_list.items()
                }
                tpl_sel = st.selectbox(
                    t("template_select"), list(tpl_options.keys()), key="tpl_sel"
                )
                if st.button(t("template_run"), key="run_tpl", type="primary"):
                    tid = tpl_options[tpl_sel]
                    prompt = tpl_list[tid]["prompt"]
                    with st.spinner(t("generating")):
                        full_prompt = (
                            f"{prompt}\n\nDocument:\n{_get_doc_text(sel)[:5000]}"
                        )
                        result = llm_service.chat_completion(
                            messages=[{"role": "user", "content": full_prompt}],
                            model=model,
                            max_tokens=2000,
                            temperature=0.4,
                        )
                    st.markdown(f"#### {tpl_sel}")
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))

    # ── CATEGORY 5: Tools ──
    elif cat == t("grp_ux"):
        tabs = st.tabs(
            [
                t("research_agent"),
                t("cot_agent"),
                t("fact_check"),
                t("code_extract"),
                t("flashcards"),
                t("reading_guide"),
                t("critic_agent"),
                t("auto_tagging"),
                t("table_extract"),
                t("persona_chat"),
                t("multi_analysis"),
                t("question_bank"),
                t("doc_diff"),
                t("session_notes"),
                t("favorites"),
            ]
        )
        with tabs[0]:
            rq = st.text_input(t("research_question"), key="research_q")
            if st.button(
                t("run_btn"), key="run_research", type="primary", disabled=not rq
            ):
                with st.spinner(t("generating")):
                    result = research_agent(rq, model, st.session_state.has_documents)
                for i, sq in enumerate(result["sub_questions"], 1):
                    st.markdown(
                        f'<span class="e-chip">{i}. {sq}</span>', unsafe_allow_html=True
                    )
                st.markdown(result["report"])
        with tabs[1]:
            cot_q = st.text_input(t("cot_question"), key="cot_q")
            if st.button(
                t("run_btn"), key="run_cot", type="primary", disabled=not cot_q
            ):
                with st.spinner(t("generating")):
                    ctx = _get_doc_text(doc_names[0]) if doc_names else ""
                    result = chain_of_thought_agent(cot_q, ctx, model)
                for i, step in enumerate(result["steps"], 1):
                    with st.expander(f"💭 {t('step_n')} {i}", expanded=(i <= 2)):
                        st.markdown(step)
        with tabs[2]:
            claims = st.text_area(t("claims_text"), height=200, key="fc_claims")
            if st.button(
                t("run_btn"), key="run_factcheck", type="primary", disabled=not claims
            ):
                with st.spinner(t("generating")):
                    ctx = _get_doc_text(doc_names[0]) if doc_names else ""
                    result = fact_check_agent(claims, ctx, model)
                st.markdown(result)
        with tabs[3]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="code_doc")
                if st.button(t("run_btn"), key="run_code", type="primary"):
                    with st.spinner(t("generating")):
                        result = extract_code_blocks(_get_doc_text(sel), model)
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[4]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="fc_doc")
                fc1, fc2 = st.columns(2)
                with fc1:
                    fc_count = st.number_input(
                        t("flashcard_count"), 5, 30, 10, key="fc_count"
                    )
                with fc2:
                    df_map = {
                        t("diff_easy"): "beginner",
                        t("diff_medium"): "intermediate",
                        t("diff_hard"): "advanced",
                    }
                    fc_diff = df_map[
                        st.selectbox(t("quiz_diff"), list(df_map.keys()), key="fc_diff")
                    ]
                if st.button(t("run_btn"), key="run_fc", type="primary"):
                    with st.spinner(t("generating")):
                        result = generate_flashcards(
                            _get_doc_text(sel), fc_count, fc_diff, model
                        )
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[5]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="rg_doc")
                if st.button(t("run_btn"), key="run_rg", type="primary"):
                    with st.spinner(t("generating")):
                        result = generate_reading_guide(_get_doc_text(sel), model)
                    st.markdown(result)
            else:
                st.info(t("no_doc_selected"))
        with tabs[6]:
            crit_text = st.text_area(t("text_to_critique"), height=200, key="crit_text")
            if st.button(
                t("run_btn"), key="run_crit", type="primary", disabled=not crit_text
            ):
                with st.spinner(t("generating")):
                    ctx = _get_doc_text(doc_names[0]) if doc_names else ""
                    result = critic_agent(crit_text, ctx, model)
                st.markdown(result)
        with tabs[7]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="tag_doc")
                if st.button(t("run_btn"), key="run_tag", type="primary"):
                    with st.spinner(t("generating")):
                        result = auto_tag_document(_get_doc_text(sel), model)
                    tc1, tc2, tc3 = st.columns(3)
                    with tc1:
                        st.metric(t("category"), result.get("category", "?"))
                    with tc2:
                        st.metric(t("difficulty"), result.get("difficulty", "?"))
                    with tc3:
                        st.metric(t("tags"), str(len(result.get("tags", []))))
                    if result.get("tags"):
                        chips = "".join(
                            [
                                f'<span class="e-chip">{tg}</span>'
                                for tg in result["tags"]
                            ]
                        )
                        st.markdown(
                            f'<div style="margin-top:.5rem">{chips}</div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.info(t("no_doc_selected"))

        # ── Level 4: Table Extraction ──
        with tabs[8]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="tbl_doc")
                if st.button(t("run_btn"), key="run_tbl", type="primary"):
                    with st.spinner(t("generating")):
                        result = table_extractor(_get_doc_text(sel), model)
                    st.markdown(
                        f'<div class="glass">{result}</div>', unsafe_allow_html=True
                    )
                    st.download_button(
                        t("download_result"), result, "tables.md", key="dl_tbl"
                    )
            else:
                st.info(t("no_doc_selected"))

        # ── Level 4: AI Persona ──
        with tabs[9]:
            persona_keys = list(PERSONAS.keys())
            persona_labels = [
                PERSONAS[k][st.session_state.get("lang", "tr")] for k in persona_keys
            ]
            sel_persona = st.selectbox(
                t("persona_select"), persona_labels, key="persona_sel"
            )
            persona_id = persona_keys[persona_labels.index(sel_persona)]
            ctx = ""
            if doc_names:
                use_ctx = st.checkbox(t("use_doc_context"), key="persona_ctx_chk")
                if use_ctx:
                    sel_d = st.selectbox(t("select_doc"), doc_names, key="persona_doc")
                    ctx = _get_doc_text(sel_d)
            q = st.text_area(t("persona_question"), key="persona_q", height=100)
            if st.button(t("run_btn"), key="run_persona", type="primary") and q:
                with st.spinner(t("generating")):
                    result = ai_persona_chat(q, persona_id, ctx, model)
                st.markdown(
                    f'<div class="glass">{result}</div>', unsafe_allow_html=True
                )

        # ── Level 4: Batch Analysis ──
        with tabs[10]:
            if len(doc_names) >= 2:
                docs = []
                for dn in doc_names:
                    docs.append({"name": dn, "text": _get_doc_text(dn)})
                st.info(f"📚 {len(docs)} documents detected")
                if st.button(t("run_btn"), key="run_multi", type="primary"):
                    with st.spinner(t("generating")):
                        result = multi_file_analysis(docs, model)
                    st.markdown(
                        f'<div class="glass">{result}</div>', unsafe_allow_html=True
                    )
                    st.download_button(
                        t("download_result"),
                        result,
                        "multi_analysis.md",
                        key="dl_multi",
                    )
            else:
                st.warning("You must upload at least 2 documents.")

        # ── Level 4: Question Bank ──
        with tabs[11]:
            if doc_names:
                sel = st.selectbox(t("select_doc"), doc_names, key="qbank_doc")
                count = st.slider(t("qbank_count"), 5, 50, 20, key="qbank_count_sl")
                if st.button(t("run_btn"), key="run_qbank", type="primary"):
                    with st.spinner(t("generating")):
                        result = question_bank_generator(
                            _get_doc_text(sel), count, model
                        )
                    st.markdown(
                        f'<div class="glass">{result}</div>', unsafe_allow_html=True
                    )
                    st.download_button(
                        t("download_result"), result, "question_bank.md", key="dl_qbank"
                    )
            else:
                st.info(t("no_doc_selected"))

        # ── Level 4: Document Diff ──
        with tabs[12]:
            if len(doc_names) >= 2:
                c1, c2 = st.columns(2)
                with c1:
                    sel_a = st.selectbox("Document A", doc_names, key="diff_a")
                with c2:
                    sel_b = st.selectbox(
                        "Document B",
                        [d for d in doc_names if d != sel_a] or doc_names,
                        key="diff_b",
                    )
                if st.button(t("run_btn"), key="run_diff", type="primary"):
                    with st.spinner(t("generating")):
                        result = document_diff(
                            _get_doc_text(sel_a),
                            sel_a,
                            _get_doc_text(sel_b),
                            sel_b,
                            model,
                        )
                    st.markdown(
                        f'<div class="glass">{result}</div>', unsafe_allow_html=True
                    )
            else:
                st.warning("You must upload at least 2 documents.")

        with tabs[13]:  # Session notes
            note = st.text_input(t("note_text"), key="note_input")
            if st.button(t("add_note"), key="add_note_btn") and note:
                st.session_state.session_notes.append(
                    {"text": note, "time": time.strftime("%H:%M")}
                )
                st.rerun()
            if st.session_state.session_notes:
                for i, n in enumerate(reversed(st.session_state.session_notes)):
                    st.markdown(f"**{n['time']}** — {n['text']}")
                nc1, nc2 = st.columns(2)
                with nc1:
                    if st.button(t("clear_notes"), key="clear_notes"):
                        st.session_state.session_notes = []
                        st.rerun()
                with nc2:
                    notes_md = "\n".join(
                        [
                            f"- [{n['time']}] {n['text']}"
                            for n in st.session_state.session_notes
                        ]
                    )
                    st.download_button(
                        t("export_notes"), notes_md, "notes.md", key="dl_notes"
                    )
            else:
                st.info(t("no_notes"))
        with tabs[14]:  # Favorites
            if st.session_state.favorites:
                for i, fav in enumerate(reversed(st.session_state.favorites)):
                    with st.expander(f"⭐ {fav.get('title', 'Result')[:50]}..."):
                        st.markdown(fav.get("content", "")[:500])
                if st.button(t("clear_favorites"), key="clear_favs"):
                    st.session_state.favorites = []
                    st.rerun()
            else:
                st.info(t("no_favorites"))


def _get_doc_text(filename):
    for d in st.session_state.documents:
        if d["filename"] == filename and d.get("full_text"):
            return d["full_text"]
    try:
        return lightrag_service.query(f"content of {filename}", mode="naive") or ""
    except:
        return ""


# UTILITIES
# ══════════════════════════════════════════════════════════
