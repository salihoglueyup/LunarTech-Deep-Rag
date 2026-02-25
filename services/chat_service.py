"""
LunarTech AI - Chat Servisi v3
RAG + citation + smart mode + custom prompt + conversation memory.
"""

import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from services import llm_service, lightrag_service
from core.smart_features import (
    extract_citations,
    format_answer_with_citations,
    smart_rag_mode,
    generate_followup_questions,
)

SYSTEM_PROMPT = """You are the LunarTech AI assistant. You answer questions about PDF documents uploaded by the user.

Your rules:
1. ONLY base your answers on the provided context information
2. If the info is not in the context, say "This information was not found in the uploaded documents"
3. Keep your answers clear, structured and in English
4. Use bullet points, headers, and tables when necessary
5. If there is source info, state it in the format [Page X]
6. Do not provide info outside the user's question

Current context information:
{context}
"""

NO_CONTEXT_PROMPT = """You are the LunarTech AI assistant. No PDF document has been uploaded yet.

Tell the user they can do the following:
1. Upload one or more PDFs from the left menu
2. Ask questions about the uploaded PDF
3. Generate a handbook based on the PDF
4. View entities/relations from the Knowledge Graph page

Help with general questions too, but state that a PDF upload is needed for document-requiring questions.
"""


def build_messages(
    question,
    context=None,
    chat_history=None,
    custom_prompt=None,
    memory_summary=None,
    use_persona=False,
):
    messages = []
    if context:
        sys_content = SYSTEM_PROMPT.format(context=context)
    else:
        sys_content = NO_CONTEXT_PROMPT

    if custom_prompt:
        sys_content += f"\n\nEk talimatlar:\n{custom_prompt}"
    if memory_summary:
        sys_content += f"\n\nÖnceki sohbet özeti:\n{memory_summary}"

    if use_persona and chat_history:
        user_texts = [m["content"] for m in chat_history if m["role"] == "user"]
        if user_texts:
            recent_texts = " ".join(user_texts[-5:])
            sys_content += f"\n\n[CRITICAL INSTRUCTION: CORPORATE PERSONA AND TONE CLONING]\nYou are currently asked to mimic the tone of the User and their Company. EXACTLY CLONE the style, jargon, word choices, sentence lengths, and formality level from the past user messages below:\nExample Company Tone: \"'{recent_texts}'\"\nFORMAT your responses to be completely aligned with this tone."

    messages.append({"role": "system", "content": sys_content})
    if chat_history:
        for msg in chat_history[-20:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})
    return messages


def generate_answer(
    question,
    chat_history=None,
    model=None,
    has_documents=False,
    rag_mode="hybrid",
    temperature=0.7,
    max_tokens=4096,
    custom_prompt=None,
    memory_summary=None,
    auto_rag=False,
):
    context = None
    if auto_rag and rag_mode == "hybrid":
        rag_mode = smart_rag_mode(question)

    if has_documents:
        try:
            context = lightrag_service.query(question, mode=rag_mode)
        except Exception as e:
            context = f"Error retrieving context: {str(e)}"

    messages = build_messages(
        question, context, chat_history, custom_prompt, memory_summary
    )
    answer = llm_service.chat_completion(
        messages=messages, model=model, max_tokens=max_tokens, temperature=temperature
    )

    citations = extract_citations(context) if context else []
    answer = format_answer_with_citations(answer, citations)

    return answer


def stream_answer(
    question,
    chat_history=None,
    model=None,
    has_documents=False,
    rag_mode="hybrid",
    temperature=0.7,
    max_tokens=4096,
    custom_prompt=None,
    memory_summary=None,
    auto_rag=False,
    use_persona=False,
):
    context = None
    actual_mode = rag_mode
    if auto_rag and rag_mode == "hybrid":
        actual_mode = smart_rag_mode(question)

    yield {"type": "status", "state": "running", "text": "Scanning documents..."}

    if has_documents:
        try:
            yield {
                "type": "status",
                "state": "update",
                "text": f"Searching for context via LightRAG ({actual_mode} mode)...",
            }
            context = lightrag_service.query(question, mode=actual_mode)

            if not context or len(str(context)) < 50:
                yield {
                    "type": "status",
                    "state": "update",
                    "text": "Insufficient information found in document. Searching the web...",
                }
                try:
                    from duckduckgo_search import DDGS
                    import requests
                    from bs4 import BeautifulSoup

                    with DDGS() as ddgs:
                        res = list(ddgs.text(question, max_results=2))
                        if res:
                            scraped_texts = []
                            for r in res:
                                try:
                                    page = requests.get(r["href"], timeout=5)
                                    soup = BeautifulSoup(page.content, "html.parser")
                                    text_content = " ".join(
                                        [p.text for p in soup.find_all("p")]
                                    )
                                    truncated = (
                                        text_content[:1500]
                                        if len(text_content) > 100
                                        else r.get("body", "")
                                    )
                                    scraped_texts.append(
                                        f"- Source: {r['title']} ({r['href']})\n  Content: {truncated}"
                                    )
                                except Exception:
                                    scraped_texts.append(
                                        f"- Source: {r['title']}\n  Info: {r.get('body', '')}"
                                    )

                            context = "DYNAMIC WEB SCAN RESULTS:\n" + "\n\n".join(
                                scraped_texts
                            )
                            yield {
                                "type": "status",
                                "state": "update",
                                "text": "Live Web scan completed. Synthesizing page contents...",
                            }
                except Exception as web_e:
                    yield {
                        "type": "status",
                        "state": "update",
                        "text": f"Web search failed: {web_e}",
                    }
            else:
                yield {
                    "type": "status",
                    "state": "update",
                    "text": "Strong context found from documents.",
                }

        except Exception as e:
            yield {
                "type": "status",
                "state": "update",
                "text": f"Context error: {str(e)}",
            }
            context = None

    yield {
        "type": "status",
        "state": "update",
        "text": "Context process completed. Autonomous agents engaged.",
    }

    messages = build_messages(
        question, context, chat_history, custom_prompt, memory_summary, use_persona
    )

    # --- SWARM LOGIC ---
    from core.swarm import generate_draft, critique_draft, stream_refinement

    yield {
        "type": "status",
        "state": "update",
        "text": "Drafter agent is preparing the initial draft...",
    }
    draft = generate_draft(messages, model, max_tokens, temperature)

    yield {
        "type": "status",
        "state": "update",
        "text": f"✍️ **Drafter Agent Draft:**\n```text\n{draft[:300]}...\n```\n\nCritic agent is performing hallucination checks...",
    }
    critique = critique_draft(question, str(context) if context else "", draft, model)

    yield {
        "type": "status",
        "state": "update",
        "text": f"🧐 **Critic Agent Report:**\n```text\n{critique}\n```",
    }

    full_answer = ""
    if "APPROVED" in critique.upper():
        yield {
            "type": "status",
            "state": "complete",
            "text": "Draft found flawless. Publishing.",
        }
        # Metni küçük chunk'lar halinde stream et ki animasyon bozulmasın
        chunk_size = 8
        for i in range(0, len(draft), chunk_size):
            chunk = draft[i : i + chunk_size]
            full_answer += chunk
            yield {"type": "chunk", "text": chunk}
    else:
        yield {
            "type": "status",
            "state": "complete",
            "text": f"Critique received. Publishing with issues fixed...",
        }
        for chunk in stream_refinement(
            messages, critique, draft, model, max_tokens, temperature
        ):
            full_answer += chunk
            yield {"type": "chunk", "text": chunk}

    if context and "DYNAMIC WEB SCAN RESULTS" not in context:
        citations = extract_citations(context)
        if citations:
            citation_text = "\n\n---\n📚 **Sources:** " + ", ".join(
                [
                    f"Page {c['page']}"
                    for c in sorted(
                        set(tuple(ci.items()) for ci in citations),
                        key=lambda x: dict(x)["page"],
                    )
                ][:5]
            )
            yield {"type": "chunk", "text": citation_text}


def get_followup_questions(question, answer, model=None):
    """Cevap sonrası follow-up soru önerileri."""
    return generate_followup_questions(question, answer, model)


def auto_generate_title(message: str, model: str = None) -> str:
    """Mesajdan otomatik sohbet basligi uretir (3-5 kelime)."""
    try:
        result = llm_service.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a short title of 3-5 words for this message. Only write the title:\n\n{message[:200]}",
                }
            ],
            model=model,
            max_tokens=30,
            temperature=0.3,
            use_cache=True,
        )
        title = result.strip().strip('"').strip("'")[:50]
        return title if title else message[:30] + "..."
    except Exception:
        return message[:30] + "..."
