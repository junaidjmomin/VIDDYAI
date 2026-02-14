"""
Feedback & Analytics Router
Handles satisfaction tracking, feedback logging, and analytics
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from routers.auth import get_students_db

router = APIRouter()

# In-memory feedback storage
feedback_db: Dict[str, List[Dict[str, Any]]] = {}


class FeedbackData(BaseModel):
    student_id: str
    query_id: Optional[str] = None
    rating: int  # 1-5 stars or thumbs up (1) / thumbs down (0)
    feedback_type: str  # 'satisfaction', 'response_quality', 'bug_report'
    comment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/api/feedback")
async def log_feedback(data: FeedbackData):
    """
    Log user feedback (thumbs up/down, star ratings, comments)
    """
    students_db = get_students_db()
    
    if data.student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Initialize feedback list for student if doesn't exist
    if data.student_id not in feedback_db:
        feedback_db[data.student_id] = []
    
    # Create feedback entry
    feedback_entry = {
        "feedback_id": f"fb_{data.student_id}_{len(feedback_db[data.student_id])}",
        "student_id": data.student_id,
        "query_id": data.query_id,
        "rating": data.rating,
        "feedback_type": data.feedback_type,
        "comment": data.comment,
        "metadata": data.metadata or {},
        "timestamp": datetime.now().isoformat()
    }
    
    feedback_db[data.student_id].append(feedback_entry)
    
    # Award XP for providing feedback (encourage engagement)
    profile = students_db[data.student_id]
    profile["xp"] += 1
    profile["level"] = (profile["xp"] // 50) + 1
    
    return {
        "success": True,
        "message": "Thank you for your feedback! 💙",
        "feedback_id": feedback_entry["feedback_id"],
        "xp_earned": 1,
        "total_xp": profile["xp"]
    }


@router.get("/api/feedback/{student_id}")
async def get_student_feedback(student_id: str):
    """
    Get all feedback for a student
    """
    students_db = get_students_db()
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    feedback_list = feedback_db.get(student_id, [])
    
    return {
        "success": True,
        "student_id": student_id,
        "feedback": feedback_list,
        "total_feedback": len(feedback_list)
    }


@router.get("/api/satisfaction/{student_id}")
async def get_satisfaction_chart(student_id: str, days: int = 7):
    """
    Get satisfaction trend data for charts
    
    Returns daily satisfaction averages for the last N days
    Used for the satisfaction chart in the UI
    
    Args:
        student_id: Unique student identifier
        days: Number of days to include (default: 7)
    """
    students_db = get_students_db()
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    feedback_list = feedback_db.get(student_id, [])
    
    # Filter satisfaction ratings
    satisfaction_ratings = [
        fb for fb in feedback_list
        if fb["feedback_type"] == "satisfaction"
    ]
    
    if not satisfaction_ratings:
        # Return mock data if no feedback yet
        mock_data = []
        today = datetime.now()
        for i in range(days):
            date = today - timedelta(days=days - i - 1)
            mock_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": date.strftime("%a"),
                "satisfaction": 85 + (i * 2),  # Gradual increase
                "responses": 0
            })
        
        return {
            "success": True,
            "student_id": student_id,
            "period_days": days,
            "data": mock_data,
            "mock": True
        }
    
    # Calculate daily averages
    today = datetime.now()
    daily_data = []
    
    for i in range(days):
        date = today - timedelta(days=days - i - 1)
        date_str = date.strftime("%Y-%m-%d")
        
        # Get ratings for this day
        day_ratings = [
            fb["rating"] for fb in satisfaction_ratings
            if fb["timestamp"].startswith(date_str)
        ]
        
        if day_ratings:
            avg_satisfaction = (sum(day_ratings) / len(day_ratings)) * 20  # Convert 1-5 to 0-100
        else:
            avg_satisfaction = None  # No data for this day
        
        daily_data.append({
            "date": date_str,
            "day": date.strftime("%a"),
            "satisfaction": round(avg_satisfaction, 1) if avg_satisfaction else None,
            "responses": len(day_ratings)
        })
    
    return {
        "success": True,
        "student_id": student_id,
        "period_days": days,
        "data": daily_data,
        "mock": False
    }


@router.get("/api/analytics/{student_id}")
async def get_analytics(student_id: str):
    """
    Get comprehensive analytics for a student
    """
    students_db = get_students_db()
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    profile = students_db[student_id]
    feedback_list = feedback_db.get(student_id, [])
    
    # Calculate metrics
    total_feedback = len(feedback_list)
    positive_feedback = len([fb for fb in feedback_list if fb["rating"] >= 4])
    negative_feedback = len([fb for fb in feedback_list if fb["rating"] <= 2])
    
    satisfaction_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
    
    return {
        "success": True,
        "student_id": student_id,
        "analytics": {
            "total_questions": profile.get("total_questions_asked", 0),
            "total_feedback": total_feedback,
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "satisfaction_rate": round(satisfaction_rate, 1),
            "level": profile["level"],
            "xp": profile["xp"],
            "textbook_uploaded": profile.get("textbook_uploaded", False),
            "learning_style": profile["learning_style"],
            "confidence_band": profile["confidence_band"]
        }
    }
