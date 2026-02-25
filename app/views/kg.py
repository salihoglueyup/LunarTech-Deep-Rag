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


from services import lightrag_service
import os, xml.etree.ElementTree as ET


def render_kg_page():
    st.markdown(
        f'<div class="pg-header"><div class="pg-title pg-title-kg">{t("kg_title")}</div><div class="pg-sub">{t("kg_desc")}</div></div>',
        unsafe_allow_html=True,
    )
    if not st.session_state.has_documents:
        st.markdown(
            f'<div class="welcome"><h2>📄</h2><p>{t("kg_no_doc")}</p></div>',
            unsafe_allow_html=True,
        )
        return
    graph_file = os.path.join(
        config.LIGHTRAG_WORK_DIR, "graph_chunk_entity_relation.graphml"
    )
    if not os.path.exists(graph_file):
        st.markdown(
            f'<div class="empty-state"><div class="empty-icon">⏳</div><div class="empty-text">Graph not ready</div></div>',
            unsafe_allow_html=True,
        )
        return
    try:
        entities, relations = _parse_graphml(graph_file)

        # ── 3D KNOWLEDGE GRAPH & TIMELINE ──
        st.markdown(f"#### ⏳ Timeline")
        st.info(
            "Drag the slider to see how the knowledge graph evolves over time as documents are added to the system."
        )
        max_steps = max(1, len(entities))
        timeline_step = st.slider(
            "Steps",
            min_value=1,
            max_value=max_steps,
            value=max_steps,
            label_visibility="collapsed",
        )

        # Slicing the graph to simulate temporal building
        entities = entities[:timeline_step]
        valid_set = set(entities)
        relations = [
            r
            for r in relations
            if r.split(" → ")[0] in valid_set and r.split(" → ")[1] in valid_set
        ]

        cols = st.columns(3)
        km = [
            ("🔵", t("entity_label"), str(len(entities))),
            ("🔗", t("relation_label"), str(len(relations))),
            ("📊", t("density_label"), f"{len(relations)/max(len(entities),1):.1f}"),
        ]
        for col, (ic, lb, vl) in zip(cols, km):
            with col:
                st.markdown(
                    f'<div class="m-card"><div class="m-val">{vl}</div><div class="m-lbl">{ic} {lb}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)
        search = st.text_input(t("kg_search"), placeholder="...", key="kg_search")
        left, right = st.columns(2)
        with left:
            st.markdown(f"#### 🔵 {t('entity_label')}")
            fe = (
                [e for e in entities if not search or search.lower() in e.lower()]
                if search
                else entities
            )
            chips = "".join([f'<span class="e-chip">{e}</span>' for e in fe[:60]])
            st.markdown(
                f'<div class="glass" style="max-height:400px;overflow-y:auto">{chips or "<span style=color:#475569>—</span>"}</div>',
                unsafe_allow_html=True,
            )
            if len(fe) > 60:
                st.caption(f"... +{len(fe)-60}")
        with right:
            st.markdown(f"#### 🔗 {t('relation_label')}")
            fr = (
                [r for r in relations if not search or search.lower() in r.lower()]
                if search
                else relations
            )
            rchips = "".join([f'<span class="r-chip">{r}</span>' for r in fr[:60]])
            st.markdown(
                f'<div class="glass" style="max-height:400px;overflow-y:auto">{rchips or "<span style=color:#475569>—</span>"}</div>',
                unsafe_allow_html=True,
            )
            if len(fr) > 60:
                st.caption(f"... +{len(fr)-60}")
        if fe:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"#### {t('network_view')}")
            clicked_node = _render_echarts(fe, fr)

            if clicked_node:
                st.markdown(f"### 📍 Selected Node: **{clicked_node}**")
                node_relations = [r for r in relations if clicked_node in r]
                if node_relations:
                    st.markdown("**Connections:**")
                    for nr in node_relations[:20]:  # Show up to 20
                        parts = nr.split(" → ")
                        if len(parts) == 2:
                            other_node = (
                                parts[1] if parts[0] == clicked_node else parts[0]
                            )
                            st.markdown(f"- 🔗 **{clicked_node}** ↔ **{other_node}**")
                else:
                    st.info("No specific connections found for this node.")

    except Exception as e:
        st.error(f"Graph parse error: {str(e)}")


def _render_echarts(entities, relations):
    try:
        from streamlit_echarts import st_echarts
    except ImportError:
        st.warning("streamlit-echarts library is missing.")
        return None

    # Graph Pruning: Delete isolated nodes if too crowded
    if len(entities) > 100:
        from collections import Counter

        node_counts = Counter()
        for r in relations:
            parts = r.split(" → ")
            if len(parts) == 2:
                node_counts[parts[0]] += 1
                node_counts[parts[1]] += 1

        entities = [e for e in entities if node_counts[e] > 1]
        valid_set = set(entities)
        relations = [
            r
            for r in relations
            if r.split(" → ")[0] in valid_set and r.split(" → ")[1] in valid_set
        ]

    nodes = []
    links = []

    for r in relations:
        parts = r.split(" → ")
        if len(parts) == 2:
            links.append({"source": parts[0], "target": parts[1]})

    for e in entities:
        cat = abs(hash(e)) % 5
        base_size = 15 + cat * 5
        nodes.append(
            {
                "name": e,
                "value": 1,
                "category": cat,
                "symbolSize": base_size,
                "itemStyle": {
                    "shadowBlur": 25,
                    "shadowColor": [
                        "#3b82f6",
                        "#8b5cf6",
                        "#ec4899",
                        "#14b8a6",
                        "#f59e0b",
                    ][cat],
                },
            }
        )

    option = {
        "backgroundColor": "#0f172a",  # Deep space 3D feel background
        "tooltip": {"formatter": "{b}"},
        "color": ["#3b82f6", "#8b5cf6", "#ec4899", "#14b8a6", "#f59e0b"],
        "animationDurationUpdate": 1500,
        "animationEasingUpdate": "quinticInOut",
        "series": [
            {
                "type": "graph",
                "layout": "force",
                "data": nodes[:300],
                "links": links[:500],
                "roam": True,
                "label": {
                    "show": True,
                    "position": "right",
                    "formatter": "{b}",
                    "color": "#e2e8f0",
                    "fontSize": 11,
                    "fontWeight": "bold",
                },
                "force": {"repulsion": 300, "edgeLength": [50, 120], "gravity": 0.15},
                "lineStyle": {
                    "color": "source",
                    "curveness": 0.3,
                    "opacity": 0.8,
                    "width": 2,
                },
            }
        ],
    }

    events = {"click": "function(params) { return params.data.name; }"}

    return st_echarts(options=option, events=events, height="600px", key="kg_echarts")


def _parse_graphml(filepath):
    import xml.etree.ElementTree as ET

    entities, relations = [], []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for node in root.iter():
            if node.tag.endswith("node"):
                nid = node.get("id", "")
                if nid:
                    entities.append(nid)
            elif node.tag.endswith("edge"):
                s, t2 = node.get("source", ""), node.get("target", "")
                if s and t2:
                    relations.append(f"{s} → {t2}")
    except:
        pass
    return entities, relations


# ══════════════════════════════════════════════════════════
# PAGE: AI TOOLS (28 tools in 5 categories)
# ══════════════════════════════════════════════════════════
