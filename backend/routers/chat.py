"""
Chat Router — VidyaSetu AI
SSE Streaming + Validator Integrated Properly
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from core.agents import run_council, run_single_agent_response
from services.validator import validate_question          # ← services.validator
from routers.auth import get_students_db
from core.database import db

router = APIRouter()

chat_history_db: Dict[str, List[Dict[str, Any]]] = {}


class ChatMessage(BaseModel):
    student_id: str
    query: str
    context: Optional[str] = None


@router.get("/stream")
async def chat_stream(query: str, student_id: str):

    students_db = get_students_db()

    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")

    profile = students_db[student_id]
    grade   = profile.get("grade", 3)
    subject = profile.get("subject", "General")

    # Validate BEFORE any AI call
    is_allowed, block_message = validate_question(query, grade, subject)

    async def event_generator():
        try:
            # ── BLOCKED ───────────────────────────────────────────────────────
            if not is_allowed:
                print(f"[Chat] Blocked: {query[:40]}")

                # Step events so frontend council animation works correctly
                yield f"data: {json.dumps({'agent': 'retriever', 'status': 'done', 'text': 'Question checked.'})}\n\n"
                yield f"data: {json.dumps({'agent': 'explainer', 'status': 'done', 'text': block_message})}\n\n"
                yield f"data: {json.dumps({'agent': 'simplifier', 'status': 'done', 'text': block_message})}\n\n"
                yield f"data: {json.dumps({'agent': 'encourager', 'status': 'done', 'text': block_message})}\n\n"

                # Final event — this is what the frontend renders as the answer
                yield f"data: {json.dumps({'final': block_message, 'blocked': True, 'safety_verified': True, 'query_id': f'blocked_{abs(hash(query)) % 100000}'})}\n\n"
                yield "data: [DONE]\n\n"
                return

            # ── NORMAL FLOW ───────────────────────────────────────────────────
            full_response = ""

            async for event in run_council(query, student_id, profile):
                if event.get("final"):
                    full_response = event["final"]
                yield f"data: {json.dumps(event)}\n\n"

            db.save_chat_message(
                student_id,
                query,
                full_response or "[No response]",
                datetime.now().isoformat()
            )

            yield "data: [DONE]\n\n"

        except Exception as e:
            print(f"[Chat] Stream error: {e}")
            yield f"data: {json.dumps({'final': 'I am having trouble right now. Try again 🦉', 'error': True})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "Connection":        "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/message")
async def send_message(message: ChatMessage):

    students_db = get_students_db()

    if message.student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")

    profile = students_db[message.student_id]
    grade   = profile.get("grade", 3)
    subject = profile.get("subject", "General")

    is_allowed, block_message = validate_question(message.query, grade, subject)

    if not is_allowed:
        return {
            "success":  False,
            "blocked":  True,
            "response": block_message,
        }

    response = await run_single_agent_response(
        message.query, message.student_id, profile
    )

    db.save_chat_message(
        message.student_id, message.query,
        response, datetime.now().isoformat()
    )

    return {"success": True, "response": response}


@router.get("/history/{student_id}")
async def get_chat_history_endpoint(student_id: str, limit: int = 50):
    history = db.get_chat_history(student_id, limit)
    return {"success": True, "history": history}


@router.delete("/history/{student_id}")
async def clear_chat_history(student_id: str):
    students_db = get_students_db()
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    chat_history_db[student_id] = []
    return {"success": True}