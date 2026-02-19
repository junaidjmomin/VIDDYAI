"""
Textbook Ingestion Router — VidyaSetu AI
Handles PDF upload, text extraction, and ChromaDB embedding

CHANGES from original:
  - extract_text_from_pdf now returns (text, page_chunks) tuple
  - page_chunks passed to chunk_and_embed for citation metadata
  - Cleaner error messages
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
import uuid
from datetime import datetime
from core.ingestion import extract_text_from_pdf, chunk_and_embed, get_collection_stats
from routers.auth import get_students_db

router = APIRouter()

from core.database import db

textbooks_cache = {}

UPLOAD_DIR    = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_textbook(
    file:       UploadFile = File(...),
    student_id: str        = Form(...),
    subject:    str        = Form(...),
    grade:      int        = Form(...),
):
    students_db = get_students_db()
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    textbook_id = str(uuid.uuid4())
    tmp_path    = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        print(f"[Upload] Extracting text from: {file.filename}")
        # FIX: extract_text_from_pdf now returns (full_text, page_chunks)
        full_text, page_chunks = extract_text_from_pdf(tmp_path)

        if not full_text or len(full_text.strip()) < 100:
            raise ValueError("PDF appears empty or text extraction failed. "
                             "Make sure it's a text-based PDF (not a scanned image).")

        print(f"[Upload] Chunking & embedding for {student_id}/{subject}")
        # FIX: pass page_chunks so chunk_and_embed can store page numbers
        chunks_count = chunk_and_embed(
            text=full_text,
            student_id=student_id,
            subject=subject,
            grade=grade,
            textbook_id=textbook_id,
            page_chunks=page_chunks,  # NEW
        )

        permanent_path = os.path.join(UPLOAD_DIR, f"{textbook_id}.pdf")
        with open(permanent_path, "wb") as f:
            f.write(file_content)

    except Exception as e:
        print(f"[Upload] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    metadata = {
        "textbook_id":   textbook_id,
        "student_id":    student_id,
        "subject":       subject,
        "grade":         grade,
        "filename":      file.filename,
        "file_size":     len(file_content),
        "chunks_indexed": chunks_count,
        "status":        "ready",
        "uploaded_at":   datetime.now().isoformat(),
        "file_path":     permanent_path,
    }
    textbooks_cache[textbook_id] = metadata
    db.save_textbook(metadata)

    profile = students_db[student_id]
    profile["textbook_uploaded"] = True
    profile["textbook_id"]       = textbook_id
    profile["xp"]               += 10
    profile["level"]             = (profile["xp"] // 50) + 1
    db.save_student(profile)

    return {
        "success":        True,
        "textbook_id":    textbook_id,
        "chunks_indexed": chunks_count,
        "status":         "ready",
        "message":        f"✅ {file.filename} processed! {chunks_count} knowledge chunks indexed.",
        "xp_earned":      10,
        "total_xp":       profile["xp"],
    }


@router.get("/status/{textbook_id}")
async def get_textbook_status(textbook_id: str):
    if textbook_id not in textbooks_cache:
        metadata = db.get_textbook(textbook_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Textbook not found")
        textbooks_cache[textbook_id] = metadata
    m = textbooks_cache[textbook_id]
    return {
        "success":        True,
        "textbook_id":    textbook_id,
        "status":         m["status"],
        "chunks_indexed": m["chunks_indexed"],
        "subject":        m["subject"],
        "grade":          m["grade"],
        "uploaded_at":    m["uploaded_at"],
    }


@router.get("/student/{student_id}")
async def get_student_textbooks(student_id: str):
    students_db = get_students_db()
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    books = db.get_textbooks(student_id)
    return {"success": True, "student_id": student_id, "textbooks": books, "count": len(books)}


@router.delete("/{textbook_id}")
async def delete_textbook(textbook_id: str, student_id: str):
    students_db = get_students_db()
    if textbook_id not in textbooks_cache:
        metadata = db.get_textbook(textbook_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Textbook not found")
        textbooks_cache[textbook_id] = metadata
    m = textbooks_cache[textbook_id]
    if m["student_id"] != student_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    from core.ingestion import delete_collection
    deleted = delete_collection(student_id, m["subject"])

    if os.path.exists(m.get("file_path", "")):
        os.remove(m["file_path"])

    textbooks_cache.pop(textbook_id, None)
    db.delete_textbook(textbook_id)

    profile = students_db[student_id]
    profile["textbook_uploaded"] = False
    profile.pop("textbook_id", None)
    db.save_student(profile)

    return {"success": True, "message": "Textbook deleted", "chroma_deleted": deleted}