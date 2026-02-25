"""
LunarTech AI — Prompt Template Library v2
20 ready-to-use analysis templates.
"""

TEMPLATES = {
    "swot": {
        "icon": "📊",
        "title_tr": "SWOT Analizi",
        "title_en": "SWOT Analysis",
        "prompt": "Perform a detailed SWOT analysis on the topic of this document. Strengths, weaknesses, opportunities, and threats.",
    },
    "executive_summary": {
        "icon": "📋",
        "title_tr": "Yönetici Özeti",
        "title_en": "Executive Summary",
        "prompt": "Prepare a 1-page executive summary of this document. Key findings, recommendations, and next steps.",
    },
    "pros_cons": {
        "icon": "⚖️",
        "title_tr": "Artılar ve Eksiler",
        "title_en": "Pros & Cons",
        "prompt": "List the pros and cons of the topic in this document in a table format.",
    },
    "action_items": {
        "icon": "✅",
        "title_tr": "Aksiyon Maddeleri",
        "title_en": "Action Items",
        "prompt": "List concrete action items that can be extracted from this document. For each item: what to do, who will do it, when.",
    },
    "timeline": {
        "icon": "📅",
        "title_tr": "Zaman Çizelgesi",
        "title_en": "Timeline",
        "prompt": "Draft a timeline for the events/processes in this document in chronological order.",
    },
    "glossary": {
        "icon": "📖",
        "title_tr": "Terimler Sözlüğü",
        "title_en": "Glossary",
        "prompt": "List the technical terms and key concepts in this document as an annotated glossary.",
    },
    "faq": {
        "icon": "❓",
        "title_tr": "SSS (FAQ)",
        "title_en": "FAQ",
        "prompt": "Create the top 10 most likely asked questions and their answers about this document in an FAQ format.",
    },
    "elevator_pitch": {
        "icon": "🚀",
        "title_tr": "Asansör Konuşması",
        "title_en": "Elevator Pitch",
        "prompt": "Prepare an elevator pitch that can explain the main topic of this document in 60 seconds.",
    },
    # ── Level 5: 12 New Templates ──
    "risk_analysis": {
        "icon": "⚠️",
        "title_tr": "Risk Analizi",
        "title_en": "Risk Analysis",
        "prompt": "Identify risks related to the topic in this document. For each risk: determine a description, probability (low/medium/high), impact level, and mitigation strategy. Present it in a table format.",
    },
    "okr_generator": {
        "icon": "🎯",
        "title_tr": "OKR Oluşturucu",
        "title_en": "OKR Generator",
        "prompt": "Create OKRs (Objectives & Key Results) from the content of this document. Determine 3-5 objectives and 3-4 key results for each objective. They must comply with SMART criteria.",
    },
    "trend_analysis": {
        "icon": "📈",
        "title_tr": "Trend Analizi",
        "title_en": "Trend Analysis",
        "prompt": "Predict future trends by analyzing the data and information in this document. Organize it as current state, rising trends, declining trends, and predictions.",
    },
    "roadmap": {
        "icon": "🗺️",
        "title_tr": "Yol Haritası",
        "title_en": "Roadmap",
        "prompt": "Create a project roadmap based on the topic of this document. Determine short-term (1-3 months), medium-term (3-6 months), and long-term (6-12 months) goals and milestones.",
    },
    "checklist": {
        "icon": "📋",
        "title_tr": "Kontrol Listesi",
        "title_en": "Checklist",
        "prompt": "Extract a comprehensive checklist from the content of this document. Categorize it, use checkbox format for each item. Order by priority.",
    },
    "stakeholder": {
        "icon": "👥",
        "title_tr": "Paydaş Analizi",
        "title_en": "Stakeholder Analysis",
        "prompt": "Identify stakeholders related to the topic in this document. For each stakeholder: determine role, impact level, interest level, and communication strategy. Create a Power/Interest matrix.",
    },
    "process_map": {
        "icon": "🔄",
        "title_tr": "Süreç Haritası",
        "title_en": "Process Map",
        "prompt": "Identify the workflows/processes in this document and create a step-by-step process map. For each step: specify input, output, responsible person, and duration. Mark decision points.",
    },
    "case_study": {
        "icon": "📖",
        "title_tr": "Vaka Çalışması",
        "title_en": "Case Study",
        "prompt": "Rewrite the topic of this document in a professional case study format. Sections: Background, Problem Definition, Solution Approach, Implementation, Results, Lessons Learned.",
    },
    "lesson_plan": {
        "icon": "🎓",
        "title_tr": "Ders Planı",
        "title_en": "Lesson Plan",
        "prompt": "Create a detailed lesson plan based on the content of this document. Sections: Learning objectives, prerequisite knowledge, lecture plan (minute by minute), activities, evaluation questions, homework suggestions.",
    },
    "proposal": {
        "icon": "💼",
        "title_tr": "İş Teklifi",
        "title_en": "Business Proposal",
        "prompt": "Draft a professional business proposal based on the topic of this document. Sections: Executive summary, problem definition, solution proposal, approach, timeline, budget estimate, expected results.",
    },
    "press_release": {
        "icon": "📰",
        "title_tr": "Basın Bülteni",
        "title_en": "Press Release",
        "prompt": "Write a professional press release covering the topic of this document. Format: Title, subtitle, date/location, main body (who/what/when/where/why), quotes, company information.",
    },
    "literature_review": {
        "icon": "🔬",
        "title_tr": "Literatür Taraması",
        "title_en": "Literature Review",
        "prompt": "Write an academic literature review on the topic in this document. It should include main themes, comparative analysis, gaps, future research directions, and conclusion sections.",
    },
}


def get_template_list(lang="en"):
    """Returns the template list."""
    key = "title_tr" if lang == "tr" else "title_en"
    return {
        tid: {"icon": t["icon"], "title": t[key], "prompt": t["prompt"]}
        for tid, t in TEMPLATES.items()
    }
