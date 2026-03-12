"""
VidyaSetu AI — Multi-Agent Council (Groq)

Stabilized version
Fixes:
• Prevents metaphor / philosophy hallucinations
• Explainer forced to answer factually
• Encourager cannot rewrite meaning
• Adds response sanity guard
"""

from typing import Optional, AsyncGenerator
from core.rag import retrieve_context, format_citations
from core.prompt_builder import build_agent_prompt
from core.config import Config


# ── Conversation memory store ─────────────────────────────────────
_conversation_memory: dict[str, list[dict]] = {}
MEMORY_TURNS = 3


def _get_memory(student_id: str) -> list[dict]:
    return _conversation_memory.get(student_id, [])


def _save_memory(student_id: str, query: str, response: str):
    if student_id not in _conversation_memory:
        _conversation_memory[student_id] = []

    memory = _conversation_memory[student_id]

    memory.append({"role": "user", "content": query})
    memory.append({"role": "assistant", "content": response})

    _conversation_memory[student_id] = memory[-(MEMORY_TURNS * 2):]


def clear_memory(student_id: str):
    _conversation_memory.pop(student_id, None)


# ── Lazy LLM singletons ──────────────────────────────────────────
heavy_llm = None
fast_llm = None


def _ensure_llms():
    global heavy_llm, fast_llm

    if heavy_llm is not None and fast_llm is not None:
        return

    heavy_llm = Config.get_heavy_llm()
    fast_llm = Config.get_fast_llm()


# ── Agent Runner ─────────────────────────────────────────────────
async def run_agent(role: str, input_text: str, grade: int, subject: str, use_heavy=False):

    from langchain_core.messages import SystemMessage, HumanMessage

    _ensure_llms()

    llm = heavy_llm if use_heavy else fast_llm

    system_prompt = build_agent_prompt(role, grade, subject)

    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=input_text)
    ])

    return response.content


# ── Multi-Agent Council Pipeline ─────────────────────────────────
async def run_council(query: str, student_id: str, profile: dict) -> AsyncGenerator[dict, None]:

    subject = profile.get("subject", "General")
    grade = profile.get("grade", 3)

    textbook_present = profile.get("textbook_uploaded", False)

    # ── Stage 1: Retrieval ───────────────────────────────────────
    yield {"agent": "retriever", "status": "thinking", "text": "Searching your textbook..."}

    context_text, chunks = retrieve_context(query, student_id, subject)

    citations = format_citations(chunks)

    if textbook_present and not chunks:

        msg = (
            "I searched your textbook but couldn't find this topic.\n"
            "Try asking your teacher or upload the correct chapter."
        )

        yield {"agent": "retriever", "status": "done", "text": "Topic not found in textbook."}

        yield {
            "final": msg,
            "safety_verified": True,
            "query_id": f"q_{student_id}",
            "citations": ""
        }

        _save_memory(student_id, query, msg)

        return

    yield {
        "agent": "retriever",
        "status": "done",
        "text": "Relevant textbook content retrieved.",
        "citations": citations
    }

    # ── Stage 2: Explainer ───────────────────────────────────────
    yield {"agent": "explainer", "status": "thinking", "text": "Preparing explanation..."}

    memory = _get_memory(student_id)

    memory_block = ""

    if memory:

        lines = []

        for m in memory:

            label = "Student" if m["role"] == "user" else "Viddy"

            lines.append(f"{label}: {m['content'][:200]}")

        memory_block = "\n".join(lines)

    explainer_input = f"""
Previous conversation:
{memory_block}

Context:
{context_text}

Student Question:
{query}

Answer the question clearly and factually.
Do NOT create stories or analogies.
"""

    explanation = await run_agent("explainer", explainer_input, grade, subject, use_heavy=True)

    # Guard against nonsense answers
    if len(explanation.split()) < 6:

        explanation = "I could not understand the question clearly. Could you please rephrase it?"

    yield {"agent": "explainer", "status": "done", "text": explanation}

    # ── Stage 3: Simplifier ──────────────────────────────────────
    yield {"agent": "simplifier", "status": "thinking", "text": "Simplifying explanation..."}

    simplified = await run_agent("simplifier", explanation, grade, subject)

    yield {"agent": "simplifier", "status": "done", "text": simplified}

    # ── Stage 4: Encourager ──────────────────────────────────────
    yield {"agent": "encourager", "status": "thinking", "text": "Adding encouragement..."}

    encouragement = await run_agent("encourager", simplified, grade, subject)

    final = simplified + "\n\n" + encouragement

    if citations:
        final = f"{final}\n\n{citations}"

    yield {"agent": "encourager", "status": "done", "text": final}

    safety_ok = await _check_safety(final)

    yield {
        "final": final,
        "safety_verified": safety_ok,
        "query_id": f"q_{student_id}",
        "citations": citations
    }

    _save_memory(student_id, query, final)


# ── Single Agent (Non-streaming) ─────────────────────────────────
async def run_single_agent_response(query: str, student_id: str, profile: dict) -> str:

    from langchain_core.messages import SystemMessage, HumanMessage

    subject = profile.get("subject", "General")
    grade = profile.get("grade", 3)

    context_text, chunks = retrieve_context(query, student_id, subject)

    citations = format_citations(chunks)

    system_prompt = build_agent_prompt("explainer", grade, subject)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"{context_text}\n\nQuestion: {query}")
    ]

    _ensure_llms()

    response = await heavy_llm.ainvoke(messages)

    answer = response.content

    if citations:
        answer = f"{answer}\n\n{citations}"

    _save_memory(student_id, query, answer)

    return answer


# ── Safety Checker ──────────────────────────────────────────────
async def _check_safety(text: str):

    from langchain_core.messages import SystemMessage, HumanMessage

    _ensure_llms()

    response = await fast_llm.ainvoke([
        SystemMessage(content="Reply SAFE or UNSAFE."),
        HumanMessage(content=text[:400])
    ])

    return "SAFE" in response.content.upper()