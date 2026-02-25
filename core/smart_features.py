"""
LunarTech AI - Smart Features v1
Smart features: citation, follow-up questions, smart RAG mode,
auto summary, finding extraction, quiz, comparison, tagging.
"""

import os, sys, json, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services import llm_service


# ══════════════════════════════════════════════════════════
# 1. CITATION — Source Referencing
# ══════════════════════════════════════════════════════════


def extract_citations(rag_context: str) -> list[dict]:
    """Extracts page references from the RAG context."""
    citations = []
    if not rag_context:
        return citations

    # Find [Page X] format
    page_pattern = re.compile(r"\[Page\s+(\d+)\]|\[Sayfa\s+(\d+)\]")
    matches = page_pattern.findall(rag_context)

    if matches:
        seen = set()
        for pg in matches:
            if pg not in seen:
                citations.append({"page": int(pg), "type": "page"})
                seen.add(pg)

    # Chunk-based source (line by line)
    lines = rag_context.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("[Sayfa") or line.strip().startswith("[Page"):
            page_match = re.search(r"(\d+)", line)
            if page_match:
                pg = page_match.group(1)
                if pg not in {str(c["page"]) for c in citations}:
                    citations.append({"page": int(pg), "type": "chunk"})

    return citations


def format_answer_with_citations(answer: str, citations: list[dict]) -> str:
    """Adds source references to the answer."""
    if not citations:
        return answer

    ref_text = "\n\n---\n📚 **Sources:** "
    pages = sorted(set(c["page"] for c in citations))
    ref_text += ", ".join([f"Page {p}" for p in pages[:5]])

    return answer + ref_text


# ══════════════════════════════════════════════════════════
# 2. FOLLOW-UP QUESTION SUGGESTIONS
# ══════════════════════════════════════════════════════════

FOLLOWUP_PROMPT = """Based on the question and answer below, generate 3 relevant follow-up questions that the user is likely to ask.

Question: {question}
Answer summary: {answer_summary}

Rules:
- Make each question short and clear (max 15 words)
- Write the questions line by line, without numbers
- Ask questions from different angles
- Do not use emojis
- Write in English

Write only the 3 questions, do not add anything else:"""


def generate_followup_questions(
    question: str, answer: str, model: str = None
) -> list[str]:
    """Generates 3 follow-up questions based on the answer."""
    summary = answer[:500] if len(answer) > 500 else answer

    try:
        response = llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": FOLLOWUP_PROMPT.format(
                        question=question, answer_summary=summary
                    ),
                }
            ],
            model=model,
            max_tokens=200,
            temperature=0.7,
        )

        questions = [
            q.strip().lstrip("0123456789.-) ")
            for q in response.strip().split("\n")
            if q.strip() and len(q.strip()) > 5
        ]
        return questions[:3]
    except Exception:
        return []


# ══════════════════════════════════════════════════════════
# 3. SMART RAG MODE SELECTION
# ══════════════════════════════════════════════════════════


def smart_rag_mode(question: str) -> str:
    """Analyzes the question and selects the most appropriate RAG mode."""
    q = question.lower().strip()

    # Short, specific questions → local (entity-based)
    local_signals = [
        "ne demek",
        "nedir",
        "tanımı",
        "define",
        "what is",
        "kim",
        "who is",
        "kaç",
        "how many",
        "ne zaman",
        "when",
        "nerede",
        "where",
    ]

    # Broad, comparative questions → global (community-based)
    global_signals = [
        "karşılaştır",
        "compare",
        "fark",
        "difference",
        "genel olarak",
        "overall",
        "özetle",
        "summarize",
        "tüm",
        "all",
        "hepsi",
        "avantaj",
        "dezavantaj",
        "advantage",
        "disadvantage",
        "neden",
        "why",
        "nasıl etkiler",
        "how does it affect",
    ]

    # Naive signals (simple search)
    naive_signals = ["listele", "list", "sırala", "enumerate", "say", "bul", "find"]

    local_score = sum(1 for s in local_signals if s in q)
    global_score = sum(1 for s in global_signals if s in q)
    naive_score = sum(1 for s in naive_signals if s in q)

    if naive_score > local_score and naive_score > global_score:
        return "naive"
    if global_score > local_score:
        return "global"
    if local_score > 0:
        return "local"

    return "hybrid"  # Default


# ══════════════════════════════════════════════════════════
# 4. AUTO SUMMARY
# ══════════════════════════════════════════════════════════

SUMMARY_PROMPT = """Extract a short 3-5 sentence summary of the text below. Write in English, use an academic tone.

Text:
{text}

Summary:"""


def auto_summarize(text: str, model: str = None) -> str:
    """Extracts a short summary of the text."""
    chunk = text[:6000]
    try:
        return llm_service.chat_completion(
            messages=[{"role": "user", "content": SUMMARY_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=300,
            temperature=0.3,
        )
    except Exception as e:
        return f"Summary could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 5. KEY FINDING EXTRACTION
# ══════════════════════════════════════════════════════════

FINDINGS_PROMPT = """Extract the 10 most important key findings from the text below.

Text:
{text}

Rules:
- Make each finding 1-2 sentences
- Write in numbered list format
- Order from most important to least important
- Write in English

10 Key Findings:"""


def extract_key_findings(text: str, model: str = None) -> str:
    """Extracts key findings from the text."""
    chunk = text[:8000]
    try:
        return llm_service.chat_completion(
            messages=[{"role": "user", "content": FINDINGS_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=1000,
            temperature=0.3,
        )
    except Exception as e:
        return f"Findings could not be extracted: {str(e)}"


# ══════════════════════════════════════════════════════════
# 6. QUESTION GENERATION (QUIZ)
# ══════════════════════════════════════════════════════════

QUIZ_PROMPT = """Based on the text below, generate {count} {quiz_type} questions.

Text:
{text}

Rules:
- Each question must be based on information in the text
- {quiz_rules}
- Write in English
- Difficulty: {difficulty}

Questions:"""


def generate_quiz(
    text: str,
    count: int = 5,
    quiz_type: str = "multiple choice",
    difficulty: str = "medium",
    model: str = None,
) -> str:
    """Generates quiz questions from the text."""
    rules = {
        "multiple choice": "Each question should have 4 choices (A,B,C,D) and a correct answer",
        "open ended": "Each question should have a short model answer below it",
        "true/false": "State whether each statement is true or false",
    }
    chunk = text[:6000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": QUIZ_PROMPT.format(
                        text=chunk,
                        count=count,
                        quiz_type=quiz_type,
                        quiz_rules=rules.get(quiz_type, rules["multiple choice"]),
                        difficulty=difficulty,
                    ),
                }
            ],
            model=model,
            max_tokens=2000,
            temperature=0.5,
        )
    except Exception as e:
        return f"Quiz could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 7. DOCUMENT COMPARISON
# ══════════════════════════════════════════════════════════

COMPARE_PROMPT = """Compare the two documents below.

Document 1: {doc1_name}
{doc1_text}

Document 2: {doc2_name}
{doc2_text}

Analysis:
1. Common Topics (similarities)
2. Differences
3. Points Unique to Document 1
4. Points Unique to Document 2
5. Overall Evaluation

Write in English, provide a detailed and structured JSON answer:"""


def compare_documents(
    doc1_text: str, doc1_name: str, doc2_text: str, doc2_name: str, model: str = None
) -> str:
    """Compares two documents."""
    t1 = doc1_text[:4000]
    t2 = doc2_text[:4000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": COMPARE_PROMPT.format(
                        doc1_name=doc1_name,
                        doc1_text=t1,
                        doc2_name=doc2_name,
                        doc2_text=t2,
                    ),
                }
            ],
            model=model,
            max_tokens=2000,
            temperature=0.4,
        )
    except Exception as e:
        return f"Comparison could not be made: {str(e)}"


# ══════════════════════════════════════════════════════════
# 10. AUTO TAGGING
# ══════════════════════════════════════════════════════════

TAG_PROMPT = """Analyze the topic of the text below and determine appropriate category tags.

Text:
{text}

Respond in the following JSON format:
{{"category": "Main Category", "tags": ["tag1", "tag2", "tag3"], "difficulty": "beginner/intermediate/advanced"}}

Possible categories: Technology, Science, Law, Medicine, Education, Finance, Art, Engineering, Business, Other

Return ONLY JSON:"""


def auto_tag_document(text: str, model: str = None) -> dict:
    """Automatically tags the document."""
    chunk = text[:3000]
    try:
        response = llm_service.chat_completion(
            messages=[{"role": "user", "content": TAG_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=200,
            temperature=0.2,
        )
        # JSON parse
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return {"category": "Other", "tags": [], "difficulty": "intermediate"}


# ══════════════════════════════════════════════════════════
# 16. GÜVEN PUANI (CONFIDENCE SCORE)
# ══════════════════════════════════════════════════════════

CONFIDENCE_PROMPT = """Rate the reliability of the following question-answer pair between 0-100.

Question: {question}
Answer: {answer}
Source context available: {has_context}

Scoring criteria:
- If context is available and answer is based on it: 80-100
- Context is available but answer is partially from context: 50-80
- No context: 20-50
- Answer says 'I don't know': 10-30

Return ONLY a number (0-100), do not write anything else:"""


def confidence_score(
    question: str, answer: str, has_context: bool = False, model: str = None
) -> int:
    """Calculates the confidence score of the answer."""
    try:
        response = llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": CONFIDENCE_PROMPT.format(
                        question=question[:200],
                        answer=answer[:500],
                        has_context="Yes" if has_context else "No",
                    ),
                }
            ],
            model=model,
            max_tokens=10,
            temperature=0.1,
        )
        num = re.search(r"\d+", response.strip())
        return min(100, max(0, int(num.group()))) if num else 50
    except Exception:
        return 50


# ══════════════════════════════════════════════════════════
# 17. MIND MAP GENERATOR
# ══════════════════════════════════════════════════════════

MINDMAP_PROMPT = """Create the main topics and subtopics of the text below in Mermaid mindmap format.

Text:
{text}

Format rules:
- Use Mermaid mindmap syntax
- Central topic must be the root
- 3-5 main branches, 2-4 sub-branches per branch
- Use short labels (max 4 words)
- Write in English

Return ONLY the Mermaid code, do not add anything else:
```mermaid
mindmap
"""


def generate_mind_map(text: str, model: str = None) -> str:
    """Generates Mermaid mindmap code from the text."""
    chunk = text[:5000]
    try:
        response = llm_service.chat_completion(
            messages=[{"role": "user", "content": MINDMAP_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=1000,
            temperature=0.4,
        )
        # Extract only the mermaid code
        code = response.strip()
        if "```mermaid" in code:
            code = code.split("```mermaid")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        if not code.startswith("mindmap"):
            code = "mindmap\n" + code
        return code
    except Exception as e:
        return f"mindmap\n  root(Error: {str(e)[:50]})"


# ══════════════════════════════════════════════════════════
# 18. SWOT ANALYSIS
# ══════════════════════════════════════════════════════════

SWOT_PROMPT = """Perform a detailed SWOT analysis on the topic of the text below.

Text:
{text}

Output format (Markdown table):
| | Positive | Negative |
|---|---|---|
| **Internal** | **Strengths (S)** | **Weaknesses (W)** |
| **External** | **Opportunities (O)** | **Threats (T)** |

Write 3-5 items for each category. Make each item 1 sentence.
Add a 2-3 sentence strategic evaluation after the table.
Write in English:"""


def generate_swot(text: str, model: str = None) -> str:
    """Generates a SWOT analysis table."""
    chunk = text[:5000]
    try:
        return llm_service.chat_completion(
            messages=[{"role": "user", "content": SWOT_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=1500,
            temperature=0.4,
        )
    except Exception as e:
        return f"SWOT could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 19. FLASHCARD GENERATOR
# ══════════════════════════════════════════════════════════

FLASHCARD_PROMPT = """Create {count} educational flashcards from the text below.

Text:
{text}

Each flashcard must be in the following format:
**Question {n}:** [Question]
**Answer:** [Short but complete answer]

---

Rules:
- Questions must test knowledge (definition, explanation, comparison)
- Answers should be 1-3 sentences
- Difficulty: {difficulty}
- Write in English

Flashcards:"""


def generate_flashcards(
    text: str, count: int = 10, difficulty: str = "medium", model: str = None
) -> str:
    """Generates study flashcards."""
    chunk = text[:5000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": FLASHCARD_PROMPT.format(
                        text=chunk, count=count, difficulty=difficulty
                    ),
                }
            ],
            model=model,
            max_tokens=2000,
            temperature=0.5,
        )
    except Exception as e:
        return f"Flashcards could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 20. READING GUIDE
# ══════════════════════════════════════════════════════════

READING_GUIDE_PROMPT = """Analyze the document below and create a personalized reading guide.

Document:
{text}

The reading guide should contain:
1. **📊 Document Profile:** Topic, difficulty, estimated reading time, target audience
2. **🗺️ Reading Map:** Which sections to read first, which can be skipped
3. **⚡ Quick Start:** Understanding the core of the document in 5 minutes
4. **📚 In-Depth Reading Plan:** Daily/weekly reading schedule
5. **🔑 Prerequisites:** Background knowledge requirements
6. **💡 Reading Tips:** Strategies for this specific document type

Write in English, in Markdown format:"""


def generate_reading_guide(text: str, model: str = None) -> str:
    """Generates a personalized reading guide."""
    chunk = text[:6000]
    try:
        return llm_service.chat_completion(
            messages=[
                {"role": "user", "content": READING_GUIDE_PROMPT.format(text=chunk)}
            ],
            model=model,
            max_tokens=2000,
            temperature=0.5,
        )
    except Exception as e:
        return f"Reading guide could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 24. DOCUMENT HEALTH SCORE
# ══════════════════════════════════════════════════════════

HEALTH_PROMPT = """Analyze and score the quality of the document below.

Document:
{text}

Evaluation criteria (0-20 points each):
1. **Readability:** Sentence length, word choice, flow
2. **Consistency:** Any internal contradictions, tone consistency
3. **Completeness:** Is the topic covered sufficiently
4. **Structure:** Heading, paragraph, sectioning quality
5. **Clarity:** Ambiguous statements, use of jargon

Return in JSON format:
{{"readability": X, "consistency": X, "completeness": X, "structure": X, "clarity": X, "total": X, "grade": "A/B/C/D/F", "suggestions": ["suggestion1", "suggestion2", "suggestion3"]}}

Return ONLY JSON:"""


def document_health_score(text: str, model: str = None) -> dict:
    """Calculates document quality score."""
    chunk = text[:5000]
    try:
        response = llm_service.chat_completion(
            messages=[{"role": "user", "content": HEALTH_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=400,
            temperature=0.2,
        )
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return {
        "readability": 0,
        "consistency": 0,
        "completeness": 0,
        "structure": 0,
        "clarity": 0,
        "total": 0,
        "grade": "?",
        "suggestions": [],
    }


# ══════════════════════════════════════════════════════════
# 25. SENTIMENT & TONE ANALYSIS
# ══════════════════════════════════════════════════════════

SENTIMENT_PROMPT = """Analyze the emotional tone and writing style of the text below.

Text:
{text}

Return in JSON format:
{{"sentiment": "positive/negative/neutral/mixed", "tone": "formal/informal/academic/technical/literary", "emotion": "confidence/anxiety/excitement/objective/critical", "formality_score": 0-100, "subjectivity_score": 0-100, "analysis": "2-3 sentence detailed analysis"}}

Return ONLY JSON:"""


def sentiment_analysis(text: str, model: str = None) -> dict:
    """Text sentiment and tone analysis."""
    chunk = text[:4000]
    try:
        response = llm_service.chat_completion(
            messages=[{"role": "user", "content": SENTIMENT_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=300,
            temperature=0.2,
        )
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return {
        "sentiment": "?",
        "tone": "?",
        "emotion": "?",
        "formality_score": 0,
        "subjectivity_score": 0,
        "analysis": "Analysis could not be performed",
    }


# ══════════════════════════════════════════════════════════
# 26. CITATION GENERATOR
# ══════════════════════════════════════════════════════════

CITATION_PROMPT = """Create academic source references from the document information below.

Document name: {filename}
Information extracted from document content:
{text}

Create source references in 3 different formats:
1. **APA 7:** [format]
2. **MLA 9:** [format]
3. **Chicago:** [format]
4. **IEEE:** [format]

If information like author, year, publisher is not in the text, make reasonable estimates and mark them as [estimated].
Add English description:"""


def citation_generator(text: str, filename: str = "Document", model: str = None) -> str:
    """Generates an academic citation."""
    chunk = text[:3000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": CITATION_PROMPT.format(text=chunk, filename=filename),
                }
            ],
            model=model,
            max_tokens=600,
            temperature=0.2,
        )
    except Exception as e:
        return f"Citation could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 27. CODE EXTRACTION
# ══════════════════════════════════════════════════════════

CODE_PROMPT = """Identify and extract the code blocks from the text below.

Text:
{text}

For each code block:
1. **Language:** (Python, JavaScript, SQL, etc.)
2. **Code:** (cleanly formatted)
3. **Description:** (explain what the code does in 1 sentence)

If there is no code, write "No code blocks found in this document."
In Markdown format, wrap code blocks with ```:"""


def extract_code_blocks(text: str, model: str = None) -> str:
    """Extracts and explains code blocks from the text."""
    chunk = text[:6000]
    try:
        return llm_service.chat_completion(
            messages=[{"role": "user", "content": CODE_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=2000,
            temperature=0.2,
        )
    except Exception as e:
        return f"Code could not be extracted: {str(e)}"


# ══════════════════════════════════════════════════════════
# 28. DOCUMENT TIMELINE
# ══════════════════════════════════════════════════════════

TIMELINE_PROMPT = """Extract dates, events, and process information from the text below to create a chronological timeline.

Text:
{text}

Format:
| Date/Period | Event | Detail |
|---|---|---|
| YYYY or period | Event Name | Short description |

Rules:
- List in chronological order
- Specify approximate period if exact date is unknown
- Minimum 5, maximum 15 events
- Add a 1-2 sentence overall evaluation at the end
Write in English:"""


def document_timeline(text: str, model: str = None) -> str:
    """Generates a document timeline."""
    chunk = text[:5000]
    try:
        return llm_service.chat_completion(
            messages=[{"role": "user", "content": TIMELINE_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=1500,
            temperature=0.3,
        )
    except Exception as e:
        return f"Timeline could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 29. AI WRITING COACH
# ══════════════════════════════════════════════════════════

COACH_PROMPT = """You are an expert writing coach. Review the text below and offer suggestions for improvement.

Text:
{text}

Analysis:
1. **📝 Grammar & Spelling:** List errors and show the corrected version
2. **✨ Style:** Suggestions for better phrasing (before → after format)
3. **🔄 Sentence Structure:** Excessively long/short sentences, passive structures
4. **📊 Word Choice:** Repetitive words, stronger alternatives
5. **🎯 Overall Score:** Score out of 10 + a 1 sentence evaluation

Write in English, in Markdown format:"""


def writing_coach(text: str, model: str = None) -> str:
    """Writing coach — grammar, style, sentence structure analysis."""
    chunk = text[:4000]
    try:
        return llm_service.chat_completion(
            messages=[{"role": "user", "content": COACH_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=2000,
            temperature=0.3,
        )
    except Exception as e:
        return f"Writing analysis could not be performed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 30. PROMPT ENGINEERING HELPER
# ══════════════════════════════════════════════════════════

PROMPT_HELPER_PROMPT = """You are a prompt engineer. Analyze and improve the user's prompt below.

Original Prompt:
{prompt}

Do the following:
1. **📋 Analysis:** Strengths and weaknesses of the original prompt
2. **✨ Improved Version:** A more effective version of the prompt
3. **🔧 Techniques:** Optimization techniques used (chain-of-thought, few-shot, role-playing, etc.)
4. **📝 Alternative Versions:** Alternatives written with 2 different approaches
5. **💡 Tips:** General advice for these types of prompts

Write in English:"""


def prompt_helper(prompt: str, model: str = None) -> str:
    """Prompt improvement assistant."""
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": PROMPT_HELPER_PROMPT.format(prompt=prompt[:2000]),
                }
            ],
            model=model,
            max_tokens=2000,
            temperature=0.5,
        )
    except Exception as e:
        return f"Prompt analysis could not be performed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 31. PARAPHRASE ENGINE
# ══════════════════════════════════════════════════════════

PARAPHRASE_PROMPT = """Rewrite the text below in {style} style.

Original Text:
{text}

Style: {style}
Style description: {style_desc}

Rules:
- Preserve the meaning but completely change the phrasing
- Use vocabulary and sentence structures appropriate to the target style
- Write in Markdown format
- Write in English

Rewritten text:"""

PARAPHRASE_STYLES = {
    "academic": {
        "en": "Academic",
        "desc": "Formal, scientific tone, passive voice, technical terms",
    },
    "simple": {
        "en": "Simple",
        "desc": "Understandable by everyone, short sentences, everyday language",
    },
    "formal": {
        "en": "Formal",
        "desc": "Business tone, professional, clear and concise",
    },
    "creative": {
        "en": "Creative",
        "desc": "Literary expressions, metaphors, engaging narrative",
    },
    "technical": {
        "en": "Technical",
        "desc": "Engineering/IT tone, precise statements, jargon",
    },
    "journalistic": {
        "en": "Journalistic",
        "desc": "News style, inverted pyramid structure, objective tone",
    },
}


def paraphrase_text(text: str, style: str = "academic", model: str = None) -> str:
    """Rewrites the text in different styles."""
    s = PARAPHRASE_STYLES.get(style, PARAPHRASE_STYLES["academic"])
    chunk = text[:4000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": PARAPHRASE_PROMPT.format(
                        text=chunk, style=s["en"], style_desc=s["desc"]
                    ),
                }
            ],
            model=model,
            max_tokens=2000,
            temperature=0.6,
        )
    except Exception as e:
        return f"Could not rewrite: {str(e)}"


# ══════════════════════════════════════════════════════════
# 32. GAP ANALYSIS
# ══════════════════════════════════════════════════════════

GAP_PROMPT = """Review the document below and identify omitted topics.

Document:
{text}

Analysis:
1. **📋 Covered Topics:** Main topics covered by the document
2. **❌ Missing Topics:** Topics it should have covered but skipped
3. **⚠️ Insufficient Coverage:** Topics it touched upon but didn't detail enough
4. **💡 Suggestions:** Which sections should be added / expanded
5. **📊 Coverage Score:** Between 0-100 (how comprehensive is it in percentage?)

Write in English, in Markdown format:"""


def gap_analysis(text: str, model: str = None) -> str:
    """Document gap analysis."""
    chunk = text[:5000]
    try:
        return llm_service.chat_completion(
            messages=[{"role": "user", "content": GAP_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=2000,
            temperature=0.3,
        )
    except Exception as e:
        return f"Gap analysis could not be performed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 33. INTERACTIVE GLOSSARY
# ══════════════════════════════════════════════════════════

GLOSSARY_PROMPT = """Extract the technical terms and key concepts from the text below.

Text:
{text}

Return in JSON format for each term:
[{{"term": "term", "definition": "definition (1-2 sentences)", "category": "category"}}]

Rules:
- At least 10, at most 25 terms
- Categories: Technical, Scientific, Legal, Financial, Medical, General
- Definitions should fit the document context
- Write in English

Return ONLY a JSON array:"""


def interactive_glossary(text: str, model: str = None) -> list:
    """Creates a document glossary of terms."""
    chunk = text[:5000]
    try:
        response = llm_service.chat_completion(
            messages=[{"role": "user", "content": GLOSSARY_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=2000,
            temperature=0.2,
        )
        json_match = re.search(r"\[.*\]", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return []


# ══════════════════════════════════════════════════════════
# 34. TABLE EXTRACTOR
# ══════════════════════════════════════════════════════════

TABLE_PROMPT = """Identify and extract the tables from the text below.

Text:
{text}

For each table:
1. **Table Name/Title**
2. Extract in **Markdown Table** format
3. **CSV format** (comma-separated)
4. **Description** (what the table shows)

If there is no table, write "No tables found in this document."
Write in English:"""


def table_extractor(text: str, model: str = None) -> str:
    """Extracts and formats tables from the text."""
    chunk = text[:6000]
    try:
        return llm_service.chat_completion(
            messages=[{"role": "user", "content": TABLE_PROMPT.format(text=chunk)}],
            model=model,
            max_tokens=3000,
            temperature=0.2,
        )
    except Exception as e:
        return f"Tables could not be extracted: {str(e)}"


# ══════════════════════════════════════════════════════════
# 35. AI PERSONA CHAT
# ══════════════════════════════════════════════════════════

PERSONAS = {
    "teacher": {
        "en": "👨‍🏫 Teacher",
        "prompt": "You are an experienced teacher. Explain the topic simply and clearly. Give examples, use analogies. Go down to the student's level.",
    },
    "lawyer": {
        "en": "⚖️ Lawyer",
        "prompt": "You are an expert lawyer. Analyze from a legal perspective, explain point by point. Use legal terms but explain them.",
    },
    "scientist": {
        "en": "🔬 Scientist",
        "prompt": "You are a research scientist. Perform evidence-based analysis, propose hypotheses, critique methodology.",
    },
    "business": {
        "en": "💼 Business Advisor",
        "prompt": "You are a senior business advisor. Present ROI, market analysis, strategic recommendations. Be data-driven.",
    },
    "creative": {
        "en": "🎨 Creative Writer",
        "prompt": "You are a talented creative writer. Evaluate the text from a literary perspective, offer storytelling and rhetorical suggestions.",
    },
}


def ai_persona_chat(
    question: str, persona: str = "teacher", context: str = "", model: str = None
) -> str:
    """Chat with different AI personas."""
    p = PERSONAS.get(persona, PERSONAS["teacher"])
    system = p["prompt"]
    if context:
        system += f"\n\nContext:\n{context[:3000]}"
    try:
        return llm_service.chat_completion(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": question},
            ],
            model=model,
            max_tokens=2000,
            temperature=0.6,
        )
    except Exception as e:
        return f"Response could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 36. MULTI-FILE ANALYSIS
# ══════════════════════════════════════════════════════════

MULTI_PROMPT = """Analyze the following {count} documents collectively.

{docs_text}

Comprehensive analysis:
1. **📊 Overview:** The common theme of the documents
2. **🔗 Connections:** Relationships between documents
3. **📈 Trends:** Common trends and patterns
4. **⚡ Differences:** The unique contribution of each document
5. **📋 Synthesis:** Main conclusions drawn from all documents
6. **💡 Suggestions:** Action recommendations for this document set

Write in English, in Markdown format:"""


def multi_file_analysis(documents: list, model: str = None) -> str:
    """Performs bulk analysis of multiple documents."""
    docs_text = ""
    for i, doc in enumerate(documents[:8], 1):
        name = doc.get("name", f"Document {i}")
        text = doc.get("text", "")[:1500]
        docs_text += f"\n### Document {i}: {name}\n{text}\n"
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": MULTI_PROMPT.format(
                        count=len(documents), docs_text=docs_text
                    ),
                }
            ],
            model=model,
            max_tokens=3000,
            temperature=0.3,
        )
    except Exception as e:
        return f"Bulk analysis could not be performed: {str(e)}"


# ══════════════════════════════════════════════════════════
# 37. QUESTION BANK GENERATOR
# ══════════════════════════════════════════════════════════

QBANK_PROMPT = """Create a comprehensive question bank from the content of the document below.

Document:
{text}

Generate a total of {count} questions in these categories:
- **Knowledge (Recall):** Basic knowledge questions
- **Comprehension:** Understanding and interpretation questions
- **Application:** Applying knowledge to new situations
- **Analysis:** Comparison and associating
- **Evaluation:** Critical thinking questions

For each question:
1. Question text
2. Category (Bloom level)
3. Difficulty (⭐/⭐⭐/⭐⭐⭐)
4. Model answer (short)

Write in English, numbered list:"""


def question_bank_generator(text: str, count: int = 20, model: str = None) -> str:
    """Comprehensive question bank based on Bloom's taxonomy."""
    chunk = text[:5000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": QBANK_PROMPT.format(text=chunk, count=count),
                }
            ],
            model=model,
            max_tokens=4000,
            temperature=0.4,
        )
    except Exception as e:
        return f"Question bank could not be generated: {str(e)}"


# ══════════════════════════════════════════════════════════
# 38. DOCUMENT DIFF
# ══════════════════════════════════════════════════════════

DIFF_PROMPT = """Compare the differences between the two texts in detail.

### Text A:
{text_a}

### Text B:
{text_b}

Comparison:
1. **➕ Added:** Information present in B but not in A
2. **➖ Removed:** Information present in A but not in B
3. **✏️ Changed:** Information present in both texts but phrased differently
4. **📊 Similarity Rating:** As a percentage (0-100)
5. **💡 Summary:** Overall evaluation of the comparison

Write in English, in Markdown format:"""


def document_diff(
    text_a: str, name_a: str, text_b: str, name_b: str, model: str = None
) -> str:
    """Shows the differences between two texts."""
    chunk_a = text_a[:3000]
    chunk_b = text_b[:3000]
    try:
        return llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": DIFF_PROMPT.format(text_a=chunk_a, text_b=chunk_b),
                }
            ],
            model=model,
            max_tokens=2000,
            temperature=0.2,
        )
    except Exception as e:
        return f"Comparison could not be performed: {str(e)}"
