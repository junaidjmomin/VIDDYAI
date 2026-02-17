"""
Chat Router - SSE Streaming with Multi-Agent Council
Real-time streaming responses using Server-Sent Events
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from core.agents import run_council, run_single_agent_response
from routers.auth import get_students_db
from core.database import db

router = APIRouter()

# In-memory chat history
chat_history_db: Dict[str, List[Dict[str, Any]]] = {}


class ChatMessage(BaseModel):
    student_id: str
    query: str
    context: Optional[str] = None


@router.get("/stream")
async def chat_stream(query: str, student_id: str):
    """
    Server-Sent Events (SSE) streaming endpoint for AI chat
    
    Streams events from the 3-agent council:
    - Retriever: Finding textbook context
    - Explainer: Creating factual explanation
    - Simplifier: Making it simple with examples
    - Encourager: Adding motivation and fun
    
    Query params:
        query: Student's question
        student_id: Unique student identifier
        
    Returns:
        SSE stream with JSON events
    """
    students_db = get_students_db()
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    profile = students_db[student_id]
    
    async def event_generator():
        """Generate SSE events from agent pipeline"""
        try:
            # Run the council and stream events
            full_response = ""
            async for event in run_council(query, student_id, profile):
                if not event.get("agent") and event.get("content"):
                    full_response = event.get("content")
                # Send each event as SSE
                yield f"data: {json.dumps(event)}\n\n"
            
            # Persist chat history
            db.save_chat_message(student_id, query, full_response or "[Analysis Complete]", datetime.now().isoformat())
            
            # Final completion signal
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            print(f"Chat stream error: {e}")
            # Send error event
            error_event = {
                "error": True,
                "message": "I'm having trouble right now. Can you try asking again?",
                "details": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable buffering for Nginx
            "Connection": "keep-alive",
        }
    )


@router.post("/message")
async def send_message(message: ChatMessage):
    """
    Non-streaming chat endpoint (faster, single response)
    Use this if SSE streaming is not needed
    """
    students_db = get_students_db()
    
    if message.student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    profile = students_db[message.student_id]
    
    try:
        # Get single response
        response = await run_single_agent_response(
            message.query,
            message.student_id,
            profile
        )
        
        # Store in history
        if message.student_id not in chat_history_db:
            chat_history_db[message.student_id] = []
        
        chat_entry = {
            "query_id": f"q_{message.student_id}_{len(chat_history_db[message.student_id])}",
            "query": message.query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "grade": profile["grade"],
            "subject": profile["subject"]
        }
        
        chat_history_db[message.student_id].append(chat_entry)
        
        # Update profile stats
        profile["total_questions_asked"] = profile.get("total_questions_asked", 0) + 1
        profile["xp"] += 2  # Award 2 XP for asking a question
        profile["level"] = (profile["xp"] // 50) + 1
        
        return {
            "success": True,
            "response": response,
            "query_id": chat_entry["query_id"],
            "xp_earned": 2,
            "total_xp": profile["xp"]
        }
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{student_id}")
async def get_chat_history_endpoint(student_id: str, limit: int = 50):
    """
    Get chat history for a student
    """
    from core.database import db
    history = db.get_chat_history(student_id, limit)
    
    return {
        "success": True,
        "student_id": student_id,
        "total_messages": len(history),
        "history": history
    }


@router.delete("/history/{student_id}")
async def clear_chat_history(student_id: str):
    """
    Clear chat history for a student
    """
    students_db = get_students_db()
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student_id in chat_history_db:
        chat_history_db[student_id] = []
    
    return {
        "success": True,
        "message": "Chat history cleared"
    }
