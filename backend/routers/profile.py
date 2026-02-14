"""
Profile Games Router
Handles IQ/EQ game submissions and profile building
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from routers.auth import get_students_db

router = APIRouter()


class GameResult(BaseModel):
    student_id: str
    game_type: str  # 'math', 'logical_reasoning', 'pattern_recognition', 'empathy', etc.
    score: float  # 0-100
    time_taken: int  # seconds
    answers: Optional[Dict[str, Any]] = None


@router.post("/api/profile/games/submit")
async def submit_game_result(result: GameResult):
    """
    Submit game result and update student profile
    
    Games:
    IQ Games: math, logical_reasoning, pattern_recognition
    EQ Games: empathy, self_awareness, social_skills
    """
    students_db = get_students_db()
    
    if result.student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    profile = students_db[result.student_id]
    
    # Update appropriate scores
    if result.game_type in profile["iq_scores"]:
        profile["iq_scores"][result.game_type] = result.score
    elif result.game_type in profile["eq_scores"]:
        profile["eq_scores"][result.game_type] = result.score
    else:
        raise HTTPException(status_code=400, detail=f"Unknown game type: {result.game_type}")
    
    # Calculate average scores
    iq_avg = sum(profile["iq_scores"].values()) / len(profile["iq_scores"]) if profile["iq_scores"] else 0
    eq_avg = sum(profile["eq_scores"].values()) / len(profile["eq_scores"]) if profile["eq_scores"] else 0
    
    # Determine confidence band based on scores
    if iq_avg < 50 or eq_avg < 50:
        profile["confidence_band"] = "low"
    elif iq_avg > 75 and eq_avg > 75:
        profile["confidence_band"] = "high"
    else:
        profile["confidence_band"] = "medium"
    
    # Award XP for completing game
    xp_earned = int(result.score / 10)  # 0-10 XP based on score
    profile["xp"] += xp_earned
    
    # Update level (every 50 XP = 1 level)
    profile["level"] = (profile["xp"] // 50) + 1
    
    # Determine learning style based on game performance patterns
    if not profile.get("learning_style_locked"):
        if iq_avg > eq_avg + 20:
            profile["learning_style"] = "visual"
        elif eq_avg > iq_avg + 20:
            profile["learning_style"] = "social"
        else:
            profile["learning_style"] = "kinesthetic"
    
    # Store game history
    if "game_history" not in profile:
        profile["game_history"] = []
    
    profile["game_history"].append({
        "game_type": result.game_type,
        "score": result.score,
        "time_taken": result.time_taken,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "message": f"Game completed! You earned {xp_earned} XP! ⭐",
        "xp_earned": xp_earned,
        "total_xp": profile["xp"],
        "level": profile["level"],
        "confidence_band": profile["confidence_band"],
        "iq_avg": round(iq_avg, 1),
        "eq_avg": round(eq_avg, 1),
        "profile": profile
    }


@router.get("/api/profile/{student_id}/stats")
async def get_student_stats(student_id: str):
    """
    Get student statistics and game history
    """
    students_db = get_students_db()
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    profile = students_db[student_id]
    
    iq_avg = sum(profile["iq_scores"].values()) / len(profile["iq_scores"]) if profile["iq_scores"] else 0
    eq_avg = sum(profile["eq_scores"].values()) / len(profile["eq_scores"]) if profile["eq_scores"] else 0
    
    return {
        "success": True,
        "stats": {
            "student_id": student_id,
            "name": profile["name"],
            "grade": profile["grade"],
            "level": profile["level"],
            "xp": profile["xp"],
            "iq_scores": profile["iq_scores"],
            "eq_scores": profile["eq_scores"],
            "iq_avg": round(iq_avg, 1),
            "eq_avg": round(eq_avg, 1),
            "confidence_band": profile["confidence_band"],
            "learning_style": profile["learning_style"],
            "total_questions_asked": profile.get("total_questions_asked", 0),
            "game_history": profile.get("game_history", [])
        }
    }
