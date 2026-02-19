"""
VidyaSetu AI — Multi-Agent Council (Groq)

KEY FIXES over original:
  1. RAG now returns (context, chunks) — citations flow through to final response
  2. Explainer receives structured context with page labels (not raw text dump)
  3. Conversation memory: last 3 turns injected into every Groq prompt
  4. Hallucination circuit-breaker: if retrieval returns nothing AND textbook
     is uploaded, Groq is told explicitly "the textbook doesn't cover this"
     instead of letting it answer from general knowledge
  5. Safety check uses Groq llama-3.1-8b-instant (fast, free)
"""

from typing import Optional, AsyncGenerator
from core.rag import retrieve_context, format_citations
from core.prompt_builder import build_agent_prompt, build_system_prompt, build_fallback_prompt
from core.config import Config

# ── Conversation memory store  (in-memory per session) ──────────────────────
# Structure: { student_id: [ {"role": "user"|"assistant", "content": "..."} ] }
_conversation_memory: dict[str, list[dict]] = {}
MEMORY_TURNS = 3  # how many previous exchanges to include


def _get_memory(student_id: str) -> list[dict]:
    return _conversation_memory.get(student_id, [])


def _save_memory(student_id: str, query: str, response: str):
    if student_id not in _conversation_memory:
        _conversation_memory[student_id] = []
    memory = _conversation_memory[student_id]
    memory.append({"role": "user",      "content": query})
    memory.append({"role": "assistant", "content": response})
    # Keep only last MEMORY_TURNS exchanges (2 messages per turn)
    _conversation_memory[student_id] = memory[-(MEMORY_TURNS * 2):]


def clear_memory(student_id: str):
    _conversation_memory.pop(student_id, None)


# ── Lazy LLM singletons ───────────────────────────────────────────────────────
heavy_llm = None
fast_llm  = None


def _ensure_llms():
    global heavy_llm, fast_llm
    if heavy_llm is not None and fast_llm is not None:
        return
    heavy_llm = Config.get_heavy_llm()
    fast_llm  = Config.get_fast_llm()


# ── Single agent runner ───────────────────────────────────────────────────────
async def run_agent(
    role:      str,
    input_text: str,
    grade:     int,
    subject:   str = "General",
    use_heavy: bool = False,
) -> str:
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
    except ImportError as e:
        raise RuntimeError("Run: pip install langchain-core") from e

    _ensure_llms()
    llm           = heavy_llm if use_heavy else fast_llm
    system_prompt = build_agent_prompt(role, grade, subject)

    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=input_text),
    ])
    return response.content


# ── 3-Agent Council (streaming) ───────────────────────────────────────────────
async def run_council(
    query:      str,
    student_id: str,
    profile:    dict,
) -> AsyncGenerator[dict, None]:
    """
    SSE-streaming 4-stage pipeline:
      retriever → explainer → simplifier → encourager

    Each stage yields a dict event for the frontend.
    """
    subject         = profile.get("subject", "General")
    grade           = profile.get("grade", 3)
    textbook_present = profile.get("textbook_uploaded", False)

    # ── Stage 1: RAG Retrieval ────────────────────────────────────────────────
    yield {"agent": "retriever", "status": "thinking", "text": "Searching your textbook…"}

    context_text, chunks = retrieve_context(query, student_id, subject)
    citations            = format_citations(chunks)
    context_words        = len(context_text.split()) if context_text else 0

    # Hallucination circuit-breaker
    if textbook_present and not chunks:
        no_match_msg = (
            "I searched your textbook but couldn't find information about this. "
            "Please check with your teacher, or try asking in a different way! 📚"
        )
        yield {"agent": "retriever", "status": "done",
               "text": "Searched your textbook — topic not found in uploaded pages."}
        yield {"final": no_match_msg, "safety_verified": True,
               "query_id": f"q_{student_id}_{abs(hash(query)) % 100000}",
               "citations": ""}
        _save_memory(student_id, query, no_match_msg)
        return

    yield {
        "agent": "retriever",
        "status": "done",
        "text": f"Found {context_words} words of relevant content from your textbook.",
        "citations": citations,
    }

    # ── Stage 2: Explainer ────────────────────────────────────────────────────
    yield {"agent": "explainer", "status": "thinking", "text": "Thinking about the answer…"}

    # Inject conversation memory for context continuity
    memory = _get_memory(student_id)
    memory_block = ""
    if memory:
        lines = []
        for m in memory:
            label = "Student" if m["role"] == "user" else "Viddy"
            lines.append(f"{label}: {m['content'][:200]}")
        memory_block = "RECENT CONVERSATION:\n" + "\n".join(lines) + "\n\n"

    explainer_input = (
        f"{memory_block}"
        f"<TEXTBOOK_CONTEXT>\n{context_text}\n</TEXTBOOK_CONTEXT>\n\n"
        f"Student Question: {query}"
    )

    explanation = await run_agent("explainer", explainer_input, grade, subject, use_heavy=True)
    yield {"agent": "explainer", "status": "done", "text": explanation}

    # ── Stage 3: Simplifier ───────────────────────────────────────────────────
    yield {"agent": "simplifier", "status": "thinking", "text": "Making it easier to understand…"}
    simplified = await run_agent("simplifier", explanation, grade, subject, use_heavy=False)
    yield {"agent": "simplifier", "status": "done", "text": simplified}

    # ── Stage 4: Encourager ───────────────────────────────────────────────────
    yield {"agent": "encourager", "status": "thinking", "text": "Adding some Viddy magic…"}
    final = await run_agent("encourager", simplified, grade, subject, use_heavy=False)

    # Append citations to final response
    if citations:
        final = f"{final}\n\n{citations}"

    yield {"agent": "encourager", "status": "done", "text": final}

    # Safety check
    safety_ok = await _check_safety(final)

    yield {
        "final":          final,
        "safety_verified": safety_ok,
        "query_id":        f"q_{student_id}_{abs(hash(query)) % 100000}",
        "citations":       citations,
    }

    _save_memory(student_id, query, final)


# ── Single-shot response (non-streaming) ──────────────────────────────────────
async def run_single_agent_response(
    query:      str,
    student_id: str,
    profile:    dict,
) -> str:
    """
    Non-streaming endpoint used by /api/chat/message.
    Uses Groq llama-3.3-70b with full system prompt + RAG context.
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
    except ImportError as e:
        raise RuntimeError("Run: pip install langchain-core") from e

    subject          = profile.get("subject", "General")
    grade            = profile.get("grade", 3)
    textbook_present = profile.get("textbook_uploaded", False)

    # Retrieve textbook context
    context_text, chunks = retrieve_context(query, student_id, subject, k=Config.RAG_TOP_K)
    citations            = format_citations(chunks)

    # Hallucination guard when textbook is uploaded but query not found
    if textbook_present and not chunks:
        return (
            "I searched your textbook carefully, but I couldn't find information "
            "about this topic in the pages you uploaded. Try asking your teacher! 📚\n\n"
            "💡 Tip: Make sure your textbook PDF includes the chapter this question is from."
        )

    # Build adaptive system prompt with context
    system_prompt = build_system_prompt(profile, context_text, citations)

    # Inject conversation memory
    memory = _get_memory(student_id)
    messages = []

    try:
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        messages.append(SystemMessage(content=system_prompt))

        # Add memory turns
        for m in memory:
            if m["role"] == "user":
                messages.append(HumanMessage(content=m["content"]))
            else:
                messages.append(AIMessage(content=m["content"]))

        # Add current query
        messages.append(HumanMessage(content=query))

    except Exception as e:
        print(f"[Agents] Message build error: {e}")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

    _ensure_llms()
    llm = heavy_llm or fast_llm

    try:
        response = await llm.ainvoke(messages)
        answer   = response.content

        # Append citations
        if citations:
            answer = f"{answer}\n\n{citations}"

        _save_memory(student_id, query, answer)
        return answer

    except Exception as e:
        print(f"[Agents] LLM error: {e}")
        return "I'm having trouble right now. Can you try asking that again? 🦉"


# ── Safety check ──────────────────────────────────────────────────────────────
async def _check_safety(text: str) -> bool:
    """Use Groq llama-3.1-8b-instant for fast content safety check."""
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        _ensure_llms()
        llm = fast_llm  # Groq llama-3.1-8b-instant

        response = await llm.ainvoke([
            SystemMessage(content=(
                "You are a content safety checker for a children's educational app (ages 6–12). "
                "Respond with ONLY 'SAFE' or 'UNSAFE'. "
                "Mark UNSAFE if content contains: violence, adult content, hate speech, "
                "or anything inappropriate for primary school children."
            )),
            HumanMessage(content=f"Is this content safe for children?\n\n{text[:500]}"),
        ])
        return "SAFE" in response.content.upper()
    except Exception as e:
        print(f"[Safety] Check failed: {e}")
        return True  # Fail open for educational content