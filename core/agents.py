"""
LunarTech AI - Multi-Agent Sistemi
Araştırmacı, Eleştirmen, Çevirmen agentları.
"""

import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services import llm_service, lightrag_service


# ══════════════════════════════════════════════════════════
# 11. ARAŞTIRMACI AGENT
# ══════════════════════════════════════════════════════════

RESEARCH_DECOMPOSE = """Break down the following research question into 3-5 sub-questions. Each sub-question should be independently researchable.

Question: {question}

List the sub-questions line by line, do not add anything else:"""

RESEARCH_SYNTHESIZE = """You are an expert researcher. Create a comprehensive research report by synthesizing the answers received for the following sub-questions.

Main Question: {question}

Sub-Research Results:
{sub_results}

Rules:
- Write a comprehensive and structured report
- Use Markdown format (headings, bullet points, tables)
- Note any conflicting information
- Add a conclusion section
- Write in English

Research Report:"""


def research_agent(
    question: str, model: str = None, has_documents: bool = False
) -> dict:
    """Soruyu parçala → her parçayı araştır → birleştir."""
    # Adım 1: Soruyu alt sorulara böl
    try:
        decompose_resp = llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": RESEARCH_DECOMPOSE.format(question=question),
                }
            ],
            model=model,
            max_tokens=300,
            temperature=0.3,
        )
        sub_questions = [
            q.strip().lstrip("0123456789.-) ")
            for q in decompose_resp.strip().split("\n")
            if q.strip() and len(q.strip()) > 5
        ]
        sub_questions = sub_questions[:5]
    except Exception:
        sub_questions = [question]

    # Adım 2: Her alt soruyu araştır
    sub_results = []
    for sq in sub_questions:
        result = {"question": sq, "answer": ""}
        # RAG sorgusu
        if has_documents:
            try:
                context = lightrag_service.query(sq, mode="hybrid")
                if context and len(context) > 50:
                    result["answer"] = context[:2000]
            except Exception:
                pass

        # LLM ile zenginleştir
        if not result["answer"]:
            try:
                result["answer"] = llm_service.chat_completion(
                    messages=[{"role": "user", "content": f"Answer briefly: {sq}"}],
                    model=model,
                    max_tokens=500,
                    temperature=0.5,
                )
            except Exception:
                result["answer"] = "Information not found."

        sub_results.append(result)

    # Adım 3: Sentezle
    results_text = "\n\n".join(
        [
            f"**Sub-Question:** {r['question']}\n**Answer:** {r['answer']}"
            for r in sub_results
        ]
    )

    try:
        report = llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": RESEARCH_SYNTHESIZE.format(
                        question=question, sub_results=results_text
                    ),
                }
            ],
            model=model,
            max_tokens=4000,
            temperature=0.5,
        )
    except Exception as e:
        report = f"Report could not be generated: {str(e)}"

    return {
        "question": question,
        "sub_questions": sub_questions,
        "sub_results": sub_results,
        "report": report,
    }


# ══════════════════════════════════════════════════════════
# 12. ELEŞTİRMEN AGENT
# ══════════════════════════════════════════════════════════

CRITIC_PROMPT = """You are a meticulous editor and fact-checker. Critically review the following text.

Text:
{text}

Context (source document):
{context}

Analyze and determine:
1. **Fact Check:** Are there statements contradicting the source?
2. **Omissions:** Missed important points
3. **Inconsistencies:** Internal contradictions in the text
4. **Language/Style:** Grammar, flow, clarity
5. **Suggestions:** How to improve (bullet points)
6. **Score:** Quality score out of 10

Write in English in Markdown format:"""


def critic_agent(text: str, context: str = None, model: str = None) -> str:
    """Metni eleştirel olarak inceler."""
    ctx = context[:4000] if context else "Context not available."
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": CRITIC_PROMPT.format(text=text[:4000], context=ctx),
                }
            ],
            model=model,
            max_tokens=2000,
            temperature=0.3,
        )
    except Exception as e:
        return f"Critique could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 13. ÇEVİRMEN AGENT
# ══════════════════════════════════════════════════════════

TRANSLATE_PROMPT = """Translate the following text into {target_lang}.

Rules:
- Translate technical terms correctly, add the original in parentheses if necessary
- Preserve Markdown format
- Provide a natural and fluent translation
- Preserve semantic integrity

Text:
{text}

Translation:"""


def translator_agent(text: str, target_lang: str = "English", model: str = None) -> str:
    """Metni hedef dile çevirir."""
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": TRANSLATE_PROMPT.format(
                        text=text[:6000], target_lang=target_lang
                    ),
                }
            ],
            model=model,
            max_tokens=4000,
            temperature=0.3,
        )
    except Exception as e:
        return f"Translation failed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 15. KONUŞMA HAFIZASI
# ══════════════════════════════════════════════════════════

MEMORY_PROMPT = """Extract a 3-5 sentence summary of the following chat history. Identify important topics, the user's preferences, and the main themes of their questions.

Chat:
{chat_history}

Summary:"""


def summarize_conversation(messages: list[dict], model: str = None) -> str:
    """Sohbet geçmişini özetler (hafıza için)."""
    if not messages:
        return ""

    history = "\n".join(
        [
            f"{'User' if m.get('role', '') == 'user' else 'AI'}: {m.get('content', '')[:200]}"
            for m in messages[-20:]
            if m and isinstance(m, dict)
        ]
    )

    try:
        return llm_service.chat_completion(
            messages=[
                {"role": "user", "content": MEMORY_PROMPT.format(chat_history=history)}
            ],
            model=model,
            max_tokens=300,
            temperature=0.3,
        )
    except Exception:
        return ""


# ══════════════════════════════════════════════════════════
# 21. CHAIN-OF-THOUGHT AGENT
# ══════════════════════════════════════════════════════════

COT_PROMPT = """Answer the following question by thinking step by step.

Question: {question}

Context:
{context}

Clearly number each step and show your thought process:
- Step 1: [Problem analysis]
- Step 2: [Information gathering]
- Step 3: [Analysis]
- ...
- Result: [Final answer]

Rules:
- Explain what you are doing in each step
- Indicate intermediate results (mark with 💭)
- State your assumptions
- Give a definitive result in the last step
- Write in English in Markdown format"""


def chain_of_thought_agent(question: str, context: str = "", model: str = None) -> dict:
    """Adım adım düşünme ajanı. Ara sonuçları gösterir."""
    try:
        response = llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": COT_PROMPT.format(
                        question=question,
                        context=context[:4000] if context else "Context not available.",
                    ),
                }
            ],
            model=model,
            max_tokens=3000,
            temperature=0.4,
        )
        # Adımları parse et
        steps = []
        current = ""
        for line in response.split("\n"):
            if line.strip().startswith(
                ("Step", "- Step", "**Step", "Result", "**Result")
            ):
                if current:
                    steps.append(current.strip())
                current = line
            else:
                current += "\n" + line
        if current:
            steps.append(current.strip())

        return {
            "full_response": response,
            "steps": steps if steps else [response],
            "step_count": len(steps),
        }
    except Exception as e:
        return {"full_response": f"Error: {str(e)}", "steps": [], "step_count": 0}


# ══════════════════════════════════════════════════════════
# 22. FACT-CHECK PIPELINE
# ══════════════════════════════════════════════════════════

FACTCHECK_PROMPT = """You are a fact-checker. Verify the following claims one by one.

Claims/Text:
{claims}

Source context:
{context}

For each claim:
1. **Claim:** [The claim itself]
2. **Evidence:** [Relevant information found from the source]
3. **Result:** ✅ Verified / ⚠️ Partially True / ❌ False / ❓ Unverifiable
4. **Explanation:** [1-2 sentences]

---

Finally provide an overall reliability score (1-10).
Write in English:"""


def fact_check_agent(claims: str, context: str = "", model: str = None) -> str:
    """İddiaları kaynaklarla karşılaştırarak doğrular."""
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": FACTCHECK_PROMPT.format(
                        claims=claims[:3000],
                        context=(
                            context[:4000]
                            if context
                            else "Source context missing — verify with general knowledge."
                        ),
                    ),
                }
            ],
            model=model,
            max_tokens=3000,
            temperature=0.2,
        )
    except Exception as e:
        return f"Fact-check failed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 23. CONTENT PLANNER AGENT
# ══════════════════════════════════════════════════════════

CONTENT_PLAN_PROMPT = """You are an expert content strategist. Create a detailed {plan_type} plan for the following topic.

Topic: {topic}

Context info:
{context}

Plan type: {plan_type}

The plan should include:
1. **🎯 Target Audience:** Who is this for?
2. **📋 Content Calendar:** {timeline}
3. **📝 Titles and Summary:** Title + 2-sentence description for each content piece
4. **🔗 Internal Links:** How contents will connect to each other
5. **📊 Success Criteria:** How will it be measured?
6. **💡 Additional Suggestions:** Visuals, infographics, interactive elements

Write in English in Markdown format, make it detailed and actionable:"""

PLAN_TYPES = {
    "blog": {
        "label": "Blog Series",
        "timeline": "4-week blog post plan (2 posts per week)",
    },
    "course": {
        "label": "Online Course",
        "timeline": "8-module course plan (3-5 lessons per module)",
    },
    "training": {
        "label": "Training Curriculum",
        "timeline": "10-week training program",
    },
    "social": {
        "label": "Social Media",
        "timeline": "30-day social media content plan",
    },
}


def content_planner_agent(
    topic: str, plan_type: str = "blog", context: str = "", model: str = None
) -> str:
    """İçerik planı oluşturur."""
    pt = PLAN_TYPES.get(plan_type, PLAN_TYPES["blog"])
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": CONTENT_PLAN_PROMPT.format(
                        topic=topic,
                        plan_type=pt["label"],
                        timeline=pt["timeline"],
                        context=context[:3000] if context else "No additional context.",
                    ),
                }
            ],
            model=model,
            max_tokens=4000,
            temperature=0.5,
        )
    except Exception as e:
        return f"Content plan could not be created: {str(e)}"


# ══════════════════════════════════════════════════════════
# 34. CROSS-REFERENCE FINDER
# ══════════════════════════════════════════════════════════

CROSSREF_PROMPT = """Identify connections, common themes, and cross-references between the following documents.

{docs_text}

Analysis:
1. **🔗 Common Themes:** Concepts mentioned in both documents
2. **🔄 Cross References:** Information that complements each other
3. **⚡ Contradictions:** Points providing conflicting information
4. **📊 Connection Map:** Document relationship table
5. **💡 Integration Suggestions:** How these documents can be used together

Write in English in Markdown format:"""


def cross_reference_finder(documents: list, model: str = None) -> str:
    """Birden fazla doküman arasında çapraz referans bulur."""
    docs_text = ""
    for i, doc in enumerate(documents[:4], 1):
        name = doc.get("name", f"Document {i}")
        text = doc.get("text", "")[:2000]
        docs_text += f"\n### Document {i}: {name}\n{text}\n"
    try:
        return llm_service.chat_completion(
            messages=[
                {"role": "user", "content": CROSSREF_PROMPT.format(docs_text=docs_text)}
            ],
            model=model,
            max_tokens=2000,
            temperature=0.3,
        )
    except Exception as e:
        return f"Cross-reference analysis failed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 35. AUTO REPORT BUILDER
# ══════════════════════════════════════════════════════════

REPORT_PROMPT = """Create a comprehensive {report_type} from the following document(s).

{context}

Report structure:
1. **📋 Executive Summary** (1 paragraph)
2. **📊 Key Findings** (numbered list)
3. **🔍 Detailed Analysis** (divided into headings)
4. **📈 Data and Statistics** (in table format if available)
5. **⚠️ Risks and Warnings**
6. **💡 Recommendations and Next Steps**
7. **📎 Conclusion**

Write in English, professional tone, in Markdown format:"""

REPORT_TYPES = {
    "analysis": "Analysis Report",
    "summary": "Summary Report",
    "executive": "Executive Report",
    "technical": "Technical Report",
    "progress": "Progress Report",
}


def auto_report_builder(
    text: str, report_type: str = "analysis", model: str = None
) -> str:
    """Otomatik rapor oluşturur."""
    rt = REPORT_TYPES.get(report_type, "Analysis Report")
    chunk = text[:6000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": REPORT_PROMPT.format(context=chunk, report_type=rt),
                }
            ],
            model=model,
            max_tokens=4000,
            temperature=0.4,
        )
    except Exception as e:
        return f"Report generation failed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 36. PRESENTATION MAKER
# ══════════════════════════════════════════════════════════

PRESENTATION_PROMPT = """Create a {slide_count}-slide presentation from the following document content.

Document:
{text}

Format each slide as follows:

---
### 🎯 Slide {n}: [Title]
**Subtitle:** [if any]

- Point 1
- Point 2
- Point 3

> 💡 Speaker note: [Points to consider when presenting this slide]

---

Rules:
- First slide: Cover (title + subtitle)
- Last slide: Conclusion and Q&A
- Max 4-5 points per slide
- Add visual suggestions (with 🖼️)
- Write in English:"""


def presentation_maker(text: str, slide_count: int = 10, model: str = None) -> str:
    """Dokümanı sunum formatına çevirir."""
    chunk = text[:5000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": PRESENTATION_PROMPT.format(
                        text=chunk, slide_count=slide_count, n="{n}"
                    ),
                }
            ],
            model=model,
            max_tokens=4000,
            temperature=0.5,
        )
    except Exception as e:
        return f"Presentation generation failed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 37. EMAIL DRAFTER
# ══════════════════════════════════════════════════════════

EMAIL_PROMPT = """Draft an {email_type} email based on the following document context.

Document:
{text}

Email type: {email_type}
Tone: {tone}

Format:
**Subject:** [Email subject]

**To:** [Recipient description]

---

[Email body]

---

**Signature:** [Professional signature]

Rules:
- Use a {tone} tone
- Write clearly and concisely
- Specify required actions
- Write in English"""

EMAIL_TYPES = {
    "summary": {"label": "Summary", "tone": "professional and informative"},
    "request": {"label": "Request", "tone": "polite and clear"},
    "followup": {"label": "Follow-up", "tone": "reminding and polite"},
    "report": {"label": "Report", "tone": "formal and detailed"},
    "announcement": {"label": "Announcement", "tone": "exciting and informative"},
}


def email_drafter(text: str, email_type: str = "summary", model: str = None) -> str:
    """E-posta taslağı oluşturur."""
    et = EMAIL_TYPES.get(email_type, EMAIL_TYPES["summary"])
    chunk = text[:3000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": EMAIL_PROMPT.format(
                        text=chunk, email_type=et["label"], tone=et["tone"]
                    ),
                }
            ],
            model=model,
            max_tokens=1000,
            temperature=0.5,
        )
    except Exception as e:
        return f"Email generation failed: {str(e)}"
