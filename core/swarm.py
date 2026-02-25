from services import llm_service

CRITIC_SYSTEM_PROMPT = """You are the Executive Critic agent.
Task: Inspect the draft response prepared by the drafter agent in light of the provided context and the user query.

Rules:
1. Does the response fully address the user's question?
2. Is the response based purely on the given 'Context' data? Are there any hallucinations?
3. Is the response written in an institutional, polite, and clear language? Is the output format proper?
4. If there is missing or incorrect information in the answer, clearly state it.

If the response is FLAWLESS, ONLY write the word "APPROVED".
If a CORRECTION is needed, briefly state the error and what needs to be done (Never write APPROVED).
"""


def generate_draft(
    messages: list, model: str, max_tokens: int, temperature: float
) -> str:
    """Drafter agent prepares the initial draft."""
    messages_draft = messages.copy()
    messages_draft.append(
        {
            "role": "system",
            "content": "You are a Drafter agent. Prepare a draft based on the provided information.",
        }
    )
    return llm_service.chat_completion(
        messages=messages_draft,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        use_cache=False,
    )


def critique_draft(question: str, context: str, draft: str, model: str) -> str:
    """Critic agent inspects the draft."""
    user_prompt = f"""
USER QUESTION: {question}

CONTEXT:
{context}

DRAFTER AGENT'S DRAFT:
{draft}

Make your decision:
"""
    messages = [
        {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    return llm_service.chat_completion(
        messages=messages, model=model, max_tokens=500, temperature=0.1, use_cache=False
    )


def stream_refinement(
    messages: list,
    critique: str,
    draft: str,
    model: str,
    max_tokens: int,
    temperature: float,
):
    """Refines the draft according to the critic's notes and broadcasts live."""
    messages_refine = messages.copy()
    refine_prompt = f"""
Your previous draft: {draft}

Critic's note: {critique}

Please create your final and flawless response taking these criticisms into account (Only broadcast the final text, do not apologize or make explanations).
"""
    messages_refine.append({"role": "user", "content": refine_prompt})

    for chunk in llm_service.stream_completion(
        messages=messages_refine,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    ):
        yield chunk
