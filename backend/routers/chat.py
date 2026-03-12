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
import re

from core.agents import run_council, run_single_agent_response
from services.validator import validate_question
from routers.auth import get_students_db
from core.database import db

router = APIRouter()

chat_history_db: Dict[str, List[Dict[str, Any]]] = {}


# ───────────────── SAFE QUESTION NORMALIZER ─────────────────

COMMON_CORRECTIONS = {
    "waat": "what",
    "wat": "what",
    "wht": "what",
    "isment": "is meant",
    "ment": "meant",
    "mathh": "math",
    "algera": "algebra",
    "binry": "binary",
    "serch": "search"
}


def normalize_question(question: str) -> str:
    """
    Safely normalize student questions without changing meaning.
    """

    q = question.lower()

    # Fix common typos
    words = q.split()
    fixed_words = []

    for w in words:
        if w in COMMON_CORRECTIONS:
            fixed_words.append(COMMON_CORRECTIONS[w])
        else:
            fixed_words.append(w)

    corrected = " ".join(fixed_words)

    # Capitalize first letter
    corrected = corrected.capitalize()

    # Ensure question mark
    if not corrected.endswith("?"):
        corrected += "?"

    return corrected


# ───────────────── RESPONSE CLEANER ─────────────────
def clean_response(text: str) -> str:

    if not text:
        return text

    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"^\s*[-•]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ───────────────── MODEL ─────────────────
class ChatMessage(BaseModel):
    student_id: str
    query: str
    context: Optional[str] = None


# ───────────────── STREAM CHAT ─────────────────
@router.get("/stream")
async def chat_stream(query: str, student_id: str):

    students_db = get_students_db()

    if student_id not in students_db:
        students_db[student_id] = {
            "grade": 5,
            "subject": "Science",
            "xp": 0,
            "level": 1,
            "total_questions_asked": 0
        }

    profile = students_db[student_id]
    grade = profile.get("grade", 3)
    subject = profile.get("subject", "General")

    is_allowed, block_message = validate_question(query, grade, subject)

    async def event_generator():

        try:

            # ── BLOCKED ─────────────────
            if not is_allowed:

                block_message_clean = clean_response(block_message)

                yield f"data: {json.dumps({'agent': 'retriever', 'status': 'done', 'text': 'Question checked.'})}\n\n"
                yield f"data: {json.dumps({'agent': 'explainer', 'status': 'done', 'text': block_message_clean})}\n\n"
                yield f"data: {json.dumps({'agent': 'simplifier', 'status': 'done', 'text': block_message_clean})}\n\n"
                yield f"data: {json.dumps({'agent': 'encourager', 'status': 'done', 'text': block_message_clean})}\n\n"

                yield f"data: {json.dumps({'final': block_message_clean, 'blocked': True})}\n\n"
                yield "data: [DONE]\n\n"
                return

            # ── NORMAL FLOW ─────────────────

            corrected_query = normalize_question(query)

            full_response = ""

            async for event in run_council(corrected_query, student_id, profile):

                if "text" in event:
                    event["text"] = clean_response(event["text"])

                if event.get("final"):

                    full_response = clean_response(event["final"])

                    full_response = f'📌 You asked: "{corrected_query}"\n\n' + full_response

                    event["final"] = full_response

                yield f"data: {json.dumps(event)}\n\n"

            yield "data: [DONE]\n\n"

        except Exception:

            yield f"data: {json.dumps({'final': 'Error occurred'})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ───────────────── NORMAL CHAT ─────────────────
@router.post("/message")
async def send_message(message: ChatMessage):

    students_db = get_students_db()

    if message.student_id not in students_db:
        students_db[message.student_id] = {
            "grade": 5,
            "subject": "Science",
            "xp": 0,
            "level": 1,
            "total_questions_asked": 0
        }

    profile = students_db[message.student_id]
    grade = profile.get("grade", 3)
    subject = profile.get("subject", "General")

    is_allowed, block_message = validate_question(message.query, grade, subject)

    if not is_allowed:
        return {
            "success": False,
            "blocked": True,
            "response": clean_response(block_message),
        }

    corrected_query = normalize_question(message.query)

    response = await run_single_agent_response(
        corrected_query,
        message.student_id,
        profile
    )

    response = clean_response(response)

    response = f'📌 You asked: "{corrected_query}"\n\n' + response

    db.save_chat_message(
        message.student_id,
        message.query,
        response,
        datetime.now().isoformat()
    )

    return {"success": True, "response": response}


# ───────────────── HISTORY ─────────────────
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