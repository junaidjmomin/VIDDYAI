"""
Authentication & Student Registration Router
Handles student login/profile creation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage (replace with SQLite/PostgreSQL for production)
students_db: Dict[str, Dict[str, Any]] = {}


class LoginRequest(BaseModel):
    name: str
    grade: int
    subject: str
    learning_style: Optional[str] = "visual"
    motivation: Optional[str] = "extrinsic"


class LoginResponse(BaseModel):
    success: bool
    student_id: str
    message: str
    profile: Dict[str, Any]


@router.post("/api/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    """
    Student login/registration endpoint
    Creates new student if doesn't exist, returns existing if does
    """
    
    # Check if student already exists (by name+grade+subject combo)
    student_key = f"{data.name.lower()}_{data.grade}_{data.subject.lower()}"
    
    existing_student = None
    for sid, profile in students_db.items():
        if profile.get("lookup_key") == student_key:
            existing_student = sid
            break
    
    if existing_student:
        # Return existing student
        student_id = existing_student
        profile = students_db[student_id]
        
        # Update last login
        profile["last_login"] = datetime.now().isoformat()
        
        return LoginResponse(
            success=True,
            student_id=student_id,
            message=f"Welcome back, {data.name}! 🎉",
            profile=profile
        )
    else:
        # Create new student
        student_id = str(uuid.uuid4())
        
        # Initialize profile with EQ/IQ scores from profile games
        profile = {
            "student_id": student_id,
            "name": data.name,
            "grade": data.grade,
            "subject": data.subject,
            "learning_style": data.learning_style,
            "motivation": data.motivation,
            "xp": 0,
            "level": 1,
            "iq_scores": {
                "math": 0,
                "logical_reasoning": 0,
                "pattern_recognition": 0
            },
            "eq_scores": {
                "empathy": 0,
                "self_awareness": 0,
                "social_skills": 0
            },
            "confidence_band": "medium",  # Will be updated after games
            "textbook_uploaded": False,
            "total_questions_asked": 0,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "lookup_key": student_key
        }
        
        students_db[student_id] = profile
        
        return LoginResponse(
            success=True,
            student_id=student_id,
            message=f"Welcome to VidyaSetu AI, {data.name}! Let's start learning! 🚀",
            profile=profile
        )


@router.get("/api/profile/{student_id}")
async def get_profile(student_id: str):
    """
    Get student profile by ID
    """
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "success": True,
        "profile": students_db[student_id]
    }


@router.put("/api/profile/{student_id}")
async def update_profile(student_id: str, updates: Dict[str, Any]):
    """
    Update student profile
    """
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    profile = students_db[student_id]
    
    # Update allowed fields
    allowed_fields = [
        "learning_style", "motivation", "confidence_band", 
        "subject", "textbook_uploaded"
    ]
    
    for field, value in updates.items():
        if field in allowed_fields:
            profile[field] = value
    
    return {
        "success": True,
        "message": "Profile updated",
        "profile": profile
    }


# Export students_db for use in other routers
def get_students_db():
    return students_db
