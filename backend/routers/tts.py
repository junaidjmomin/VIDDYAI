"""
Text-to-Speech router using Groq Speech API.
Endpoint: POST /api/tts/speak
Accepts: { "text": "..." }
Returns: Audio stream (WAV)
"""

import os
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import Response
from groq import AsyncGroq

router = APIRouter()

def get_groq_client() -> AsyncGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured. Add it to your .env file."
        )
    return AsyncGroq(api_key=api_key)

@router.post("/speak")
async def generate_speech(payload: dict = Body(...)):
    """
    Converts text to speech using Groq's Orpheus TTS model.
    Model: canopylabs/orpheus-v1-english
    Voices: autumn, diana, hannah, austin, daniel, troy
    """
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    client = get_groq_client()

    try:
        response = await client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice="hannah",
            input=text,
            response_format="wav"
        )
        audio_bytes = await response.read()
        return Response(content=audio_bytes, media_type="audio/wav")

    except Exception as e:
        error_msg = str(e)
        if "model_terms" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail=(
                    "You must accept the Orpheus model terms before using TTS. "
                    "Go to https://console.groq.com/docs/model/canopylabs/orpheus-v1-english "
                    "and accept the terms, then try again."
                )
            )
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {error_msg}")
