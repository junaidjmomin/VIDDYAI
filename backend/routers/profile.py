"""
Profile Games Router
Handles IQ/EQ game submissions and profile building
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from routers.auth import get_students_db
from core.database import db
import core.agents as agents
from core.config import Config
from core.fallbacks import get_random_fallback
from langchain_core.messages import SystemMessage, HumanMessage
import json
import asyncio

router = APIRouter()


class GameResult(BaseModel):
    student_id: str
    game_type: str  # 'math', 'logical_reasoning', 'pattern_recognition', 'empathy', etc.
    score: float  # 0-100
    time_taken: float  # seconds
    answers: Optional[Dict[str, Any]] = None
    is_dynamic: bool = False

class DynamicChallengeRequest(BaseModel):
    student_id: str
    subject: str
    grade: int
    challenge_type: str  # 'iq', 'eq', 'concept'


@router.post("/games/submit")
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
    target_score_key = result.game_type
    
    # Normalize keys if needed
    if target_score_key == "logic": target_score_key = "logical_reasoning"
    if target_score_key == "pattern": target_score_key = "pattern_recognition"
    if target_score_key == "reasoning": target_score_key = "logical_reasoning"
    
    if target_score_key in profile["iq_scores"]:
        profile["iq_scores"][target_score_key] = result.score
    elif target_score_key in profile["eq_scores"]:
        profile["eq_scores"][target_score_key] = result.score
    elif result.game_type == "concept_challenge":
        # XP only for generic concepts
        pass
    else:
        # Just use math as fallback for iq if it's dynamic
        if "iq" in result.game_type.lower():
            profile["iq_scores"]["logical_reasoning"] = result.score
        elif "eq" in result.game_type.lower():
            profile["eq_scores"]["empathy"] = result.score
    
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
    
    # Persist profile
    db.save_student(profile)
    
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


@router.post("/game/generate")
async def generate_dynamic_challenge(data: DynamicChallengeRequest):
    """
    Generate a dynamic IQ/EQ/Concept challenge using Groq
    """
    # 1. Check if configured — if not, return fallback INSTANTLY (zero loading time)
    if not Config.is_llm_configured():
        print(f"Using instant fallback for {data.subject} (Groq not configured)")
        return {
            "success": True,
            "challenge": get_random_fallback(data.subject, data.challenge_type),
            "is_fallback": True
        }

    agents._ensure_llms()
    llm = agents.fast_llm
    
    if llm is None:
        return {
            "success": True,
            "challenge": get_random_fallback(data.subject, data.challenge_type),
            "is_fallback": True
        }
    
    system_prompt = f"""You are an educational psychologist creating a quick assessment for a Grade {data.grade} student in India.
    
    TASK: Create a single multiple-choice question to assess the student's {data.challenge_type} level in the context of {data.subject}.
    
    IQ Categories: math, logical_reasoning, pattern_recognition
    EQ Categories: empathy, self_awareness, social_skills
    
    RULES:
    - Language: Grade {data.grade} appropriate (super simple).
    - Format: JSON ONLY.
    - Fields: "question", "options" (list of 4), "correct" (string matching one option), "explanation", "trait" (must be one of the 6 categories above).
    """

    try:
        # Use a 10-second timeout for the LLM call
        response = await asyncio.wait_for(
            agents.fast_llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Create a {data.challenge_type} challenge for a Grade {data.grade} student about {data.subject}.")
            ]),
            timeout=10.0
        )
        
        # Parse JSON from response
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        challenge = json.loads(content)
        return {
            "success": True,
            "challenge": challenge
        }
    except Exception as e:
        print(f"Dynamic challenge error: {e}")
        # Return a high-quality fallback immediately
        return {
            "success": True,
            "challenge": get_random_fallback(data.subject, data.challenge_type),
            "is_fallback": True
        }


@router.get("/{student_id}/stats")
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
@router.get("/{student_id}")
async def get_profile(student_id: str):
    """Get full student profile"""
    students_db = get_students_db()
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    return students_db[student_id]
