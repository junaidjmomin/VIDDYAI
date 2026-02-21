"""
Speech-to-Text router using Groq Whisper API (whisper-large-v3).
Groq's Whisper is free on the generous free tier and extremely fast.
Endpoint: POST /api/stt/transcribe
Accepts: multipart/form-data with an audio file (webm/wav/mp4 etc.)
Returns: { "transcript": "..." }
"""

import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
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


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Accepts an audio file and returns the Whisper transcription via Groq.
    Supports: webm, wav, mp3, mp4, m4a, ogg, flac (max 25MB).
    Model: whisper-large-v3
    """
    MAX_SIZE = 25 * 1024 * 1024
    contents = await audio.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="Audio file too large. Max 25MB.")

    content_type = audio.content_type or "audio/webm"
    ext_map = {
        "audio/webm":  ".webm",
        "audio/wav":   ".wav",
        "audio/x-wav": ".wav",
        "audio/mp4":   ".mp4",
        "audio/mpeg":  ".mp3",
        "audio/ogg":   ".ogg",
        "audio/flac":  ".flac",
        "audio/m4a":   ".m4a",
    }
    ext = ext_map.get(content_type, ".webm")

    client = get_groq_client()

    # Write to a temp file — Groq Whisper needs a real file object
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            response = await client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=(f"audio{ext}", f, content_type),
                language="en",
                response_format="text"
            )
        transcript = response if isinstance(response, str) else response.text
        return {"transcript": transcript.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
