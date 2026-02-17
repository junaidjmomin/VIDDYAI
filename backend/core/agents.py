from typing import Optional
from core.rag import retrieve_context
from core.prompt_builder import build_agent_prompt, build_system_prompt
from core.config import Config

# Lazy LLM references — initialize at runtime to avoid import-time failures
heavy_llm = None  # type: Optional[object]
fast_llm = None   # type: Optional[object]


def _ensure_llms():
    """Initialize LLM clients on first use."""
    global heavy_llm, fast_llm
    if heavy_llm is not None and fast_llm is not None:
        return

    # Use Config helpers which import provider-specific SDKs lazily
    heavy_llm = Config.get_heavy_llm()
    fast_llm = Config.get_fast_llm()


async def run_agent(role: str, input_text: str, grade: int, use_heavy: bool = False) -> str:
    """Run a single agent using the configured LLM (imports LangChain message schema at runtime)."""
    # Import LangChain message objects lazily so module import doesn't fail if langchain
    # isn't installed. This allows the FastAPI app to start while optional packages are absent.
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
    except Exception as e:
        raise RuntimeError("Missing dependency 'langchain' — install the Python package to enable LLM calls") from e

    _ensure_llms()
    llm = heavy_llm if use_heavy else fast_llm
    system_prompt = build_agent_prompt(role, grade)

    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=input_text)
    ])
    return response.content


async def run_council(query: str, student_id: str, profile: dict):
    subject = profile.get("subject", "General")
    grade = profile.get("grade", 3)

    # Step 1 — RAG retrieval
    yield {
        "agent": "retriever",
        "status": "thinking",
        "text": "Searching your textbook..."
    }

    context = retrieve_context(query, student_id, subject)
    context_words = len(context.split()) if context else 0

    yield {
        "agent": "retriever",
        "status": "done",
        "text": f"Found {context_words} words of relevant content from your textbook."
    }

    # Step 2 — Explainer (uses heavy model for accuracy)
    yield {"agent": "explainer", "status": "thinking", "text": "Thinking about the answer..."}

    explainer_input = f"Textbook Context:\n{context}\n\nStudent Question: {query}"
    explanation = await run_agent("explainer", explainer_input, grade, use_heavy=True)

    yield {"agent": "explainer", "status": "done", "text": explanation}

    # Step 3 — Simplifier (fast model is fine)
    yield {"agent": "simplifier", "status": "thinking", "text": "Making it easier to understand..."}

    simplified = await run_agent("simplifier", explanation, grade, use_heavy=False)

    yield {"agent": "simplifier", "status": "done", "text": simplified}

    # Step 4 — Encourager (fast model)
    yield {"agent": "encourager", "status": "thinking", "text": "Adding some Viddy magic..."}

    final = await run_agent("encourager", simplified, grade, use_heavy=False)

    yield {"agent": "encourager", "status": "done", "text": final}

    # Safety check via Groq — simple prompt-based check, no external API needed
    safety_passed = await check_safety(final)

    yield {
        "final": final,
        "safety_verified": safety_passed,
        "query_id": f"q_{student_id}_{abs(hash(query)) % 100000}"
    }


async def check_safety(text: str) -> bool:
    """Simple safety check using the fast Groq model — no OpenAI Moderation API needed."""
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
    except Exception:
        # If langchain isn't installed, treat content as unsafe-safe fallback policy
        return False

    _ensure_llms()
    response = await fast_llm.ainvoke([
        SystemMessage(content="You are a content safety checker for a children's educational app (ages 6-11). Respond with only 'SAFE' or 'UNSAFE'. Content is UNSAFE if it contains violence, adult content, hate speech, or anything inappropriate for primary school children."),
        HumanMessage(content=f"Is this content safe for children?\n\n{text}")
    ])
    return "SAFE" in response.content.upper()


async def run_single_agent_response(
    query: str,
    student_id: str,
    profile: dict
) -> str:
    """Single-agent (non-streaming) response used by `/api/chat/message`.

    Builds the adaptive system prompt with textbook context and returns LLM output.
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
    except Exception:
        raise RuntimeError("Missing dependency 'langchain' — install langchain in the environment to enable single-agent responses")

    subject = profile.get("subject", "General")
    grade = profile.get("grade", 3)

    # Retrieve context
    context = retrieve_context(query, student_id, subject, k=5)

    # Build adaptive system prompt
    system_prompt = build_system_prompt(profile, context)

    _ensure_llms()
    llm = heavy_llm or fast_llm

    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ])
        return response.content
    except Exception as e:
        print(f"Single-agent LLM error: {e}")
        return "I'm having trouble right now. Can you try asking that again?"

