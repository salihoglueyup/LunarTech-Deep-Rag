"""
LunarTech AI - AgentWrite v3
LongWriter tekniğinin çekirdeği: Plan → Bölüm Bölüm Yaz

Yenilikler v3:
- Format desteği (handbook, akademik, sunum, blog)
- Görsel/tablo önerileri
- Bölüm başına özel RAG sorgusu
- Retry mekanizması (başarısız bölüm 2 kez tekrar)
"""

import os, sys, json, re, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from services import llm_service
from utils import logger
from utils.helpers import count_words

# ── Format tanımları ──
FORMAT_INSTRUCTIONS = {
    "handbook": "Use an academic and professional tone. Include detailed explanations, tables, and examples.",
    "academic": "Write in scientific paper format. Use hypothesis, methodology, findings, and conclusion structure. Use formal academic language.",
    "presentation": "Write as presentation notes. Use short bullet points. Summarize each section to fit on a single slide.",
    "blog": "Write in blog post format. Use a friendly and accessible tone. Ask questions to the reader, and include examples and stories.",
}


# ── Plan Promptları ───────────────────────────────────────

PLAN_PROMPT = """You are an expert technical writer and content planner. Based on the context information below, create a detailed writing plan for a comprehensive handbook about the requested topic.

## Context Information (Extracted from Documents):
{context}

## Requested Topic:
{topic}

## Target Word Count: Approximately 20000 words

## Instructions (CRITICAL):
1. Outline the handbook by dividing it into exactly **5 Main Parts** (e.g., Introduction, Literature Review, Methodology, Analysis, Conclusion).
2. For each Main Part, create **exactly 6 Sub-Chapters** underneath it.
3. There MUST be **exactly 30 Sub-Chapters** in total (5 Parts x 6 Chapters = 30).
4. For each sub-chapter, define a comprehensive title, a rich 3-sentence description, and a database search query (rag_query) so the writer can generate 700-800 words on that specific topic.
5. Start with a "Preface" and end with a "Conclusion and Evaluation".
6. The entire plan, all titles, and all descriptions MUST be written in English.

## Output Format:
Return ONLY JSON. The JSON structure MUST NOT be hierarchical; it must be a flat array containing exactly 30 elements:
```json
[
  {{
    "section_number": 1,
    "title": "Chapter Title (e.g., 1.1 Introduction to Technology)",
    "description": "What will be discussed in this section (3 detailed sentences in English)",
    "target_words": 800,
    "key_points": ["Detail 1", "Detail 2", "Detail 3"],
    "rag_query": "A very clear, specific 1-sentence query to search the database for this section in English"
  }}
]
```
"""

WRITE_SECTION_PROMPT = """You are an expert technical writer writing a specific chapter of a handbook.

## Handbook Topic: {topic}

## Context Specific to this Chapter:
{section_context}

## General Context:
{general_context}

## Current Chapter Plan:
- **Title:** {section_title}
- **Description:** {section_description}
- **Target Word Count:** {target_words} words
- **Key Points:** {key_points}

## Summary of Previous Chapters:
{previous_summary}

## Instructions:
1. Write this chapter in Markdown format.
2. Start the chapter title with ##
3. Use ### for subheadings.
4. Try to reach the target word count ({target_words} words) as closely as possible.
5. Base the information strictly on the context provided.
6. Use fluent and cohesive language.
7. Be consistent with previous chapters but do not repeat information.
8. Use bullet points, tables, and examples when necessary.
9. Use an academic and professional tone.
10. Add a transition sentence to the next chapter at the end of this chapter.
11. Add table, diagram, or figure suggestions where appropriate (in text format: [📊 Table Suggestion: description]).
12. YOU MUST WRITE THE ENTIRE CONTENT IN ENGLISH. Do not use Turkish.

Write the chapter content directly, do not add extra explanations.
"""


def create_plan(
    topic: str,
    context: str,
    target_words: int = None,
    model: str = None,
    output_format: str = "handbook",
) -> list[dict]:
    """Creates a detailed writing plan for the Handbook."""
    target_words = target_words or config.MAX_HANDBOOK_WORDS
    fmt_instruction = FORMAT_INSTRUCTIONS.get(
        output_format, FORMAT_INSTRUCTIONS["handbook"]
    )

    prompt = PLAN_PROMPT.format(
        context=context[:15000],
        topic=topic,
        target_words=target_words,
    )
    prompt += f"\n\nFormat instruction: {fmt_instruction}"

    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that produces structured plans in JSON format. Return only valid JSON.",
        },
        {"role": "user", "content": prompt},
    ]

    response = llm_service.chat_completion(
        messages=messages,
        model=model,
        max_tokens=4096,
        temperature=0.3,
    )

    plan = _parse_plan_json(response)
    plan = _balance_word_counts(plan, target_words)
    return plan


def write_section(
    topic: str,
    section: dict,
    context: str,
    previous_sections: list[str] = None,
    model: str = None,
    section_context: str = None,
    max_retries: int = 2,
) -> str:
    """
    Writes the specific section. With retry mechanism.
    section_context: result of section-specific RAG query
    """
    # Prepare outline of previous sections
    previous_summary = "This is the first chapter."
    if previous_sections:
        recent = previous_sections[-2:]
        summaries = []
        for sec in recent:
            summary = sec[:500] + "..." if len(sec) > 500 else sec
            summaries.append(f"Chapter: {summary}")
        previous_summary = "\n\n".join(summaries)

    prompt = WRITE_SECTION_PROMPT.format(
        topic=topic,
        section_context=section_context or "No specific context available.",
        general_context=context[:8000],
        section_title=section.get("title", ""),
        section_description=section.get("description", ""),
        target_words=section.get("target_words", 2000),
        key_points=", ".join(section.get("key_points", [])),
        previous_summary=previous_summary,
    )

    messages = [
        {
            "role": "system",
            "content": "You are an expert technical writer. You produce comprehensive content in Markdown format.",
        },
        {"role": "user", "content": prompt},
    ]

    target_words = section.get("target_words", 900)
    max_tokens = min(max(2048, int(target_words * 1.5)), 8192)

    # Retry mechanism
    last_error = None
    last_content = ""
    for attempt in range(max_retries + 1):
        try:
            response = llm_service.chat_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=0.7,
            )

            if not response:
                continue

            if not last_content:
                last_content = response
            else:
                last_content += "\n\n" + response

            word_count = count_words(last_content)

            if word_count >= target_words * 0.9:
                return last_content

            # Prompt expansion if short
            messages.append({"role": "assistant", "content": response})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"The chapter is currently at {word_count} words but needs to be at least {target_words} words.\n"
                        f"Continue exactly from where you left off. Add entirely new advanced concepts, detailed technical examples, and case studies.\n"
                        f"Do NOT repeat the introduction, headings, or your previous points. Just write the next parts."
                    ),
                }
            )

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(2 * (attempt + 1))  # Exponential backoff

    # All retries failed
    if last_error and not last_content:
        return f"## {section.get('title', 'Chapter')}\n\n*Error occurred while generating this chapter: {str(last_error)}*\n"

    if last_content:
        return last_content

    return f"## {section.get('title', 'Chapter')}\n\n*This chapter could not be generated.*\n"


# ── Helper Functions ─────────────────────────────────


def _parse_plan_json(response: str) -> list[dict]:
    """Parses the JSON plan from the LLM response."""
    json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response.strip()
        bracket_start = json_str.find("[")
        bracket_end = json_str.rfind("]")
        if bracket_start >= 0 and bracket_end >= 0:
            json_str = json_str[bracket_start : bracket_end + 1]

    try:
        plan = json.loads(json_str)
        if isinstance(plan, list):
            # Check for hallucinated duplications common in small models
            titles = [p.get("title", "") for p in plan]
            if len(titles) > 0:
                highest_duplicate = max([titles.count(t) for t in titles])
                if highest_duplicate >= 3:
                    logger.warning(
                        f"AgentWrite JSON Parse: Model hallucinated duplicate titles (Found {highest_duplicate} copies of same title). Falling back to safe default plan."
                    )
                    return _create_default_plan()
            return plan
    except json.JSONDecodeError:
        pass

    return _create_default_plan()


def _create_default_plan() -> list[dict]:
    """Default 30-chapter plan if JSON parsing fails."""
    parts = [
        "Introduction",
        "Literature Review",
        "Methodology",
        "Analysis",
        "Conclusion",
    ]
    plan = []
    sec_num = 1
    for part in parts:
        for j in range(1, 7):
            title = f"{part} - Chapter {j}"
            plan.append(
                {
                    "section_number": sec_num,
                    "title": title,
                    "description": f"Detailed and comprehensive analysis regarding {title}.",
                    "target_words": 900,
                    "key_points": [],
                    "rag_query": f"In-depth information and details about {title}",
                }
            )
            sec_num += 1
    return plan


def _balance_word_counts(plan: list[dict], target_total: int) -> list[dict]:
    """Logically distributes chapter word counts relative to the target total."""
    if not plan:
        return plan

    # Safety: filter LLM null (None) elements
    plan = [s for s in plan if s and isinstance(s, dict)]
    if not plan:
        return []

    per_section = max(900, target_total // len(plan))

    for section in plan:
        section["target_words"] = per_section
        section["hard_constraints"] = {
            "minimum_words": int(per_section * 0.9),
            "enforce": True,
        }

    return plan
