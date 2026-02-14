"""
VidyaSetu AI - Backend API
FastAPI server for AI-powered educational chatbot
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(title="VidyaSetu AI Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
students_db = {}
textbooks_db = {}
chat_history_db = {}
feedback_db = []

# --- Models ---
class StudentLogin(BaseModel):
    name: str
    grade: int
    subject: str

class StudentProfile(BaseModel):
    student_id: str
    name: str
    grade: int
    subject: str
    iq_scores: Dict[str, int] = {}
    eq_scores: Dict[str, int] = {}
    learning_style: str = "visual"
    xp: int = 0

class GameResult(BaseModel):
    student_id: str
    game_type: str  # "pattern", "memory", "emotion"
    score: int
    time_taken: float

class FeedbackLog(BaseModel):
    student_id: str
    message_id: str
    feedback_type: str  # "thumbs_up", "thumbs_down"
    timestamp: str

class ChatMessage(BaseModel):
    student_id: str
    message: str

# --- Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "VidyaSetu AI",
        "version": "1.0.0"
    }

@app.post("/api/login")
async def login(student: StudentLogin):
    """Student login/registration endpoint"""
    student_id = str(uuid.uuid4())
    
    profile = {
        "student_id": student_id,
        "name": student.name,
        "grade": student.grade,
        "subject": student.subject,
        "iq_scores": {},
        "eq_scores": {},
        "learning_style": "visual",
        "xp": 1240,
        "created_at": datetime.now().isoformat()
    }
    
    students_db[student_id] = profile
    
    return {
        "success": True,
        "student_id": student_id,
        "profile": profile
    }

@app.post("/api/profile/games/submit")
async def submit_game_result(result: GameResult):
    """Submit game results and update profile scores"""
    if result.student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[result.student_id]
    
    # Update scores based on game type
    if result.game_type == "pattern":
        student["iq_scores"]["pattern_recognition"] = result.score
        student["xp"] += 15
    elif result.game_type == "memory":
        student["iq_scores"]["working_memory"] = result.score
        student["xp"] += 15
    elif result.game_type == "emotion":
        student["eq_scores"]["emotion_recognition"] = result.score
        student["xp"] += 10
    
    # Determine learning style based on scores
    if student["iq_scores"].get("pattern_recognition", 0) > 80:
        student["learning_style"] = "visual"
    elif student["eq_scores"].get("emotion_recognition", 0) > 75:
        student["learning_style"] = "social"
    else:
        student["learning_style"] = "kinesthetic"
    
    return {
        "success": True,
        "xp_earned": 15 if "iq" in result.game_type else 10,
        "total_xp": student["xp"],
        "profile_updated": student
    }

@app.post("/api/textbook/upload")
async def upload_textbook(
    file: UploadFile = File(...),
    student_id: str = Query(...),
    subject: str = Query(...)
):
    """Upload and process textbook PDF"""
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create upload directory if it doesn't exist
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = upload_dir / f"{student_id}_{file.filename}"
    
    # Read and save file in chunks
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Store textbook metadata
    textbook_id = str(uuid.uuid4())
    textbooks_db[textbook_id] = {
        "textbook_id": textbook_id,
        "student_id": student_id,
        "subject": subject,
        "filename": file.filename,
        "file_path": str(file_path),
        "pages": 247,  # Mock value
        "status": "processed",
        "uploaded_at": datetime.now().isoformat()
    }
    
    # Link to student
    students_db[student_id]["textbook_id"] = textbook_id
    
    return {
        "success": True,
        "textbook_id": textbook_id,
        "pages_indexed": 247,
        "knowledge_stars": 247,
        "status": "ready"
    }

@app.get("/api/textbook/status/{textbook_id}")
async def get_textbook_status(textbook_id: str):
    """Get textbook processing status"""
    if textbook_id not in textbooks_db:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    return textbooks_db[textbook_id]

async def generate_ai_response_stream(query: str, student_id: str):
    """Generate streaming AI response with agent steps"""
    
    # Get student profile for personalization
    student = students_db.get(student_id, {})
    grade = student.get("grade", 3)
    subject = student.get("subject", "Science")
    learning_style = student.get("learning_style", "visual")
    
    # Agent 1: Explainer Agent
    yield f"data: {json.dumps({'agent': 'explainer', 'status': 'analyzing', 'message': 'Analyzing key concepts from your textbook...'})}\n\n"
    await asyncio.sleep(0.8)
    
    # Agent 2: Simplifier Agent
    yield f"data: {json.dumps({'agent': 'simplifier', 'status': 'processing', 'message': f'Adapting language for Grade {grade} reading level...'})}\n\n"
    await asyncio.sleep(0.8)
    
    # Agent 3: Encourager Agent
    yield f"data: {json.dumps({'agent': 'encourager', 'status': 'enhancing', 'message': 'Adding positive reinforcement and curiosity hooks...'})}\n\n"
    await asyncio.sleep(0.8)
    
    # Generate mock response based on query
    response_base = f"""
Great question about {subject}! Let me explain this concept in a way that's perfect for you.

Based on what we learned in your textbook, this is how it works:

🔭 **The Big Picture**: Think of it like a cosmic adventure! When you look up at the stars, each one has its own story.

💡 **Key Concept**: Just like how Viddy the owl can see in the dark, this {subject} concept helps us understand how things work around us. It's like having super powers!

🎯 **Remember This**: The most important thing to know is that everything connects together, just like the constellations in the night sky.

🚀 **Fun Fact**: Did you know that scientists discovered this by observing patterns - just like the game you played earlier!

What part would you like me to explain more? I can also create a visual summary to help you remember this better!
    """.strip()
    
    # Stream the response word by word for effect
    words = response_base.split()
    current_text = ""
    
    for i, word in enumerate(words):
        current_text += word + " "
        if i % 5 == 0:  # Send chunk every 5 words
            yield f"data: {json.dumps({'type': 'text', 'content': current_text})}\n\n"
            await asyncio.sleep(0.1)
    
    # Send final complete message
    message_id = str(uuid.uuid4())
    final_response = {
        "type": "complete",
        "message_id": message_id,
        "content": response_base,
        "metadata": {
            "sources": ["Chapter 4: Page 47-52"],
            "confidence": 0.92,
            "agent_steps": [
                {"agent": "Explainer Agent", "action": "Analyzing key scientific concepts from page 47..."},
                {"agent": "Simplifier Agent", "action": f"Adapting language for Grade {grade} reading level..."},
                {"agent": "Encourager Agent", "action": "Adding positive reinforcement and curiosity hooks..."}
            ]
        },
        "safety_verified": True
    }
    
    yield f"data: {json.dumps(final_response)}\n\n"
    
    # Store in chat history
    if student_id not in chat_history_db:
        chat_history_db[student_id] = []
    
    chat_history_db[student_id].append({
        "message_id": message_id,
        "query": query,
        "response": response_base,
        "timestamp": datetime.now().isoformat()
    })

@app.get("/api/chat/stream")
async def chat_stream(
    query: str = Query(...),
    student_id: str = Query(...)
):
    """Streaming chat endpoint using Server-Sent Events (SSE)"""
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return StreamingResponse(
        generate_ai_response_stream(query, student_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/feedback")
async def log_feedback(feedback: FeedbackLog):
    """Log user feedback on AI responses"""
    feedback_entry = {
        "student_id": feedback.student_id,
        "message_id": feedback.message_id,
        "feedback_type": feedback.feedback_type,
        "timestamp": feedback.timestamp
    }
    
    feedback_db.append(feedback_entry)
    
    return {
        "success": True,
        "message": "Feedback recorded"
    }

@app.get("/api/satisfaction/{student_id}")
async def get_satisfaction_chart(student_id: str):
    """Get satisfaction trend data for charts"""
    # Mock satisfaction data
    satisfaction_data = [
        {"day": "Mon", "score": 65, "date": "2026-02-10"},
        {"day": "Tue", "score": 72, "date": "2026-02-11"},
        {"day": "Wed", "score": 68, "date": "2026-02-12"},
        {"day": "Thu", "score": 85, "date": "2026-02-13"},
        {"day": "Fri", "score": 82, "date": "2026-02-14"},
        {"day": "Sat", "score": 92, "date": "2026-02-15"},
    ]
    
    return {
        "student_id": student_id,
        "data": satisfaction_data,
        "average": 77.3,
        "trend": "+12%"
    }

@app.post("/api/generate/ppt")
async def generate_ppt(chat_message: ChatMessage):
    """Generate PowerPoint presentation from chat context"""
    student_id = chat_message.student_id
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get chat history
    history = chat_history_db.get(student_id, [])
    
    # Mock PPT generation
    ppt_id = str(uuid.uuid4())
    ppt_url = f"/api/download/ppt/{ppt_id}"
    
    return {
        "success": True,
        "ppt_id": ppt_id,
        "download_url": ppt_url,
        "slides": 8,
        "title": f"{students_db[student_id]['subject']} Visual Summary",
        "message": "PowerPoint presentation created successfully!"
    }

@app.get("/api/video/search")
async def search_educational_videos(
    topic: str = Query(...),
    grade: int = Query(default=3)
):
    """Search for educational videos (YouTube API integration)"""
    
    # Mock video results (replace with actual YouTube API call)
    mock_videos = [
        {
            "video_id": "dQw4w9WgXcQ",
            "title": f"Understanding {topic} - Grade {grade}",
            "thumbnail": "https://images.unsplash.com/photo-1602979082099-7971376fce79",
            "duration": "8:45",
            "channel": "VidyaSetu Education",
            "views": "125K"
        },
        {
            "video_id": "abc123def45",
            "title": f"{topic} Explained Simply",
            "thumbnail": "https://images.unsplash.com/photo-1581726707445-75cbe4efc586",
            "duration": "12:30",
            "channel": "CBSE Learning Hub",
            "views": "89K"
        }
    ]
    
    return {
        "success": True,
        "topic": topic,
        "videos": mock_videos
    }

@app.get("/api/profile/{student_id}")
async def get_student_profile(student_id: str):
    """Get complete student profile"""
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return students_db[student_id]

@app.get("/api/chat/history/{student_id}")
async def get_chat_history(student_id: str):
    """Get chat history for a student"""
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "student_id": student_id,
        "messages": chat_history_db.get(student_id, [])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
