"""
Multi-Agent Council System
3-agent pipeline: Explainer → Simplifier → Encourager
Uses LangChain with OpenAI for real-time streaming responses
"""

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from core.rag import retrieve_context
from core.prompt_builder import build_system_prompt, build_agent_prompt
import asyncio
import os
from dotenv import load_dotenv
from typing import Dict, Any, AsyncGenerator

load_dotenv()

# Initialize LLMs
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Non-streaming LLM for agent steps
llm = ChatOpenAI(
    model=OPENAI_MODEL, 
    temperature=LLM_TEMPERATURE, 
    streaming=False
)

# Streaming LLM for final response (if needed for real-time typing effect)
llm_stream = ChatOpenAI(
    model=OPENAI_MODEL, 
    temperature=LLM_TEMPERATURE, 
    streaming=True
)


async def run_agent(role: str, input_text: str, grade: int, subject: str = "General") -> str:
    """
    Run a single agent in the council
    
    Args:
        role: 'explainer', 'simplifier', or 'encourager'
        input_text: Input prompt for this agent
        grade: Student's grade level
        subject: Subject area
        
    Returns:
        Agent's text output
    """
    system_prompt = build_agent_prompt(role, grade, subject)
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=input_text)
        ])
        return response.content
    except Exception as e:
        print(f"Error in {role} agent: {e}")
        return f"[Agent {role} encountered an error]"


async def run_council(
    query: str, 
    student_id: str, 
    profile: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Run the full 3-agent council pipeline with streaming events
    
    Pipeline:
    1. Retrieve context from ChromaDB (RAG)
    2. Explainer agent: Create factual explanation from textbook
    3. Simplifier agent: Convert to simple language with examples
    4. Encourager agent: Wrap with encouragement and memory tips
    
    Args:
        query: Student's question
        student_id: Unique student identifier
        profile: Student profile dict (grade, subject, learning_style, etc.)
        
    Yields:
        Event dictionaries for SSE streaming:
        - {"agent": "retriever", "status": "done", "text": "..."}
        - {"agent": "explainer", "status": "thinking"}
        - {"agent": "explainer", "status": "done", "text": "..."}
        - etc.
        - {"final": "...", "query_id": "..."}
    """
    subject = profile.get("subject", "General")
    grade = profile.get("grade", 3)
    
    # STEP 1: Retrieve context from textbook (RAG)
    yield {"agent": "retriever", "status": "thinking", "text": ""}
    
    try:
        context = retrieve_context(query, student_id, subject, k=5)
        
        if context and context.strip():
            word_count = len(context.split())
            yield {
                "agent": "retriever", 
                "status": "done", 
                "text": f"Found {word_count} words of context from your {subject} textbook."
            }
        else:
            yield {
                "agent": "retriever", 
                "status": "done", 
                "text": "No textbook uploaded yet. Answering from general CBSE knowledge."
            }
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        context = ""
        yield {
            "agent": "retriever", 
            "status": "done", 
            "text": "Using general knowledge (textbook retrieval unavailable)."
        }
    
    # STEP 2: Explainer Agent
    yield {"agent": "explainer", "status": "thinking", "text": ""}
    
    explainer_input = f"""Context from textbook:
{context if context else "[No textbook context - use general CBSE curriculum knowledge]"}

Student's question: {query}

Provide a clear, factual explanation suitable for Grade {grade}."""
    
    try:
        explanation = await run_agent("explainer", explainer_input, grade, subject)
        yield {"agent": "explainer", "status": "done", "text": explanation}
    except Exception as e:
        print(f"Explainer error: {e}")
        explanation = f"I understand you're asking about: {query}. Let me help explain this clearly."
        yield {"agent": "explainer", "status": "done", "text": explanation}
    
    # STEP 3: Simplifier Agent
    yield {"agent": "simplifier", "status": "thinking", "text": ""}
    
    simplifier_input = f"""Teacher's explanation:
{explanation}

Student's question was: {query}

Simplify this for a Grade {grade} Indian student with a real-life example."""
    
    try:
        simplified = await run_agent("simplifier", simplifier_input, grade, subject)
        yield {"agent": "simplifier", "status": "done", "text": simplified}
    except Exception as e:
        print(f"Simplifier error: {e}")
        simplified = explanation  # Fallback to explainer output
        yield {"agent": "simplifier", "status": "done", "text": simplified}
    
    # STEP 4: Encourager Agent (Final Response)
    yield {"agent": "encourager", "status": "thinking", "text": ""}
    
    encourager_input = f"""Simplified explanation:
{simplified}

Original question: {query}

Wrap this with an exciting opening and encouraging closing. Add a memory tip or fun fact."""
    
    try:
        final_response = await run_agent("encourager", encourager_input, grade, subject)
        yield {"agent": "encourager", "status": "done", "text": final_response}
    except Exception as e:
        print(f"Encourager error: {e}")
        final_response = simplified  # Fallback to simplified
        yield {"agent": "encourager", "status": "done", "text": final_response}
    
    # Final event with complete response and metadata
    query_id = f"q_{student_id}_{abs(hash(query)) % 100000}"
    
    yield {
        "final": final_response,
        "query_id": query_id,
        "query": query,
        "student_id": student_id,
        "subject": subject,
        "grade": grade,
        "has_context": bool(context and context.strip())
    }


async def run_single_agent_response(
    query: str,
    student_id: str,
    profile: Dict[str, Any]
) -> str:
    """
    Simplified single-agent response (fallback or faster mode)
    Uses Viddy's complete system prompt instead of council
    
    Args:
        query: Student's question
        student_id: Unique student identifier
        profile: Student profile
        
    Returns:
        Complete response string
    """
    subject = profile.get("subject", "General")
    
    # Retrieve context
    context = retrieve_context(query, student_id, subject, k=5)
    
    # Build adaptive system prompt
    system_prompt = build_system_prompt(profile, context)
    
    # Get response
    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ])
        return response.content
    except Exception as e:
        print(f"Single agent error: {e}")
        return "I'm having trouble right now. Can you try asking that again?"


async def run_council_simple(
    query: str,
    student_id: str,
    profile: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Simplified council that streams only the final response
    (useful if 3-agent pipeline is too slow)
    
    This still shows agent steps but runs faster with single LLM call
    """
    subject = profile.get("subject", "General")
    grade = profile.get("grade", 3)
    
    # Step 1: Retrieval
    yield {"agent": "retriever", "status": "thinking", "text": ""}
    context = retrieve_context(query, student_id, subject, k=5)
    
    if context:
        yield {"agent": "retriever", "status": "done", "text": f"Found relevant content from your {subject} book."}
    else:
        yield {"agent": "retriever", "status": "done", "text": "Using general knowledge."}
    
    # Step 2-4: Single LLM call (shows agent steps for UI consistency)
    yield {"agent": "explainer", "status": "thinking", "text": ""}
    await asyncio.sleep(0.3)  # Small delay for UX
    yield {"agent": "explainer", "status": "done", "text": "Creating explanation..."}
    
    yield {"agent": "simplifier", "status": "thinking", "text": ""}
    await asyncio.sleep(0.3)
    yield {"agent": "simplifier", "status": "done", "text": "Making it simple..."}
    
    yield {"agent": "encourager", "status": "thinking", "text": ""}
    
    # Single LLM call with full prompt
    system_prompt = build_system_prompt(profile, context)
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ])
        final_response = response.content
    except Exception as e:
        print(f"LLM error: {e}")
        final_response = "I'm having trouble right now. Can you ask that again?"
    
    yield {"agent": "encourager", "status": "done", "text": final_response}
    
    query_id = f"q_{student_id}_{abs(hash(query)) % 100000}"
    
    yield {
        "final": final_response,
        "query_id": query_id,
        "query": query,
        "student_id": student_id,
        "subject": subject,
        "grade": grade
    }
