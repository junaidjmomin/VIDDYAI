"""
Textbook Ingestion Router
Handles PDF upload, text extraction, and ChromaDB embedding
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

# In-memory textbook metadata storage
textbooks_db = {}

# Upload directory
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Max file size (50MB)
MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024


class TextbookStatus(BaseModel):
    textbook_id: str
    status: str  # 'processing', 'ready', 'failed'
    chunks_indexed: int
    message: str


@router.post("/api/textbook/upload")
async def upload_textbook(
    file: UploadFile = File(...),
    student_id: str = Form(...),
    subject: str = Form(...),
    grade: int = Form(...)
):
    """
    Upload and process a textbook PDF
    
    Steps:
    1. Validate PDF file
    2. Save temporarily
    3. Extract text with PyMuPDF
    4. Chunk text
    5. Embed chunks in ChromaDB
    6. Return processing status
    """
    students_db = get_students_db()
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique textbook ID
    textbook_id = str(uuid.uuid4())
    
    # Save to temp file for processing
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        # Extract text from PDF
        print(f"Extracting text from PDF: {file.filename}")
        text = extract_text_from_pdf(tmp_path)
        
        if not text or len(text.strip()) < 100:
            raise ValueError("PDF appears empty or text extraction failed")
        
        # Chunk and embed in ChromaDB
        print(f"Chunking and embedding for student {student_id}, {subject}")
        chunks_count = chunk_and_embed(text, student_id, subject, grade, textbook_id)
        
        # Save permanent copy (optional - for re-processing later)
        permanent_path = os.path.join(UPLOAD_DIR, f"{textbook_id}.pdf")
        with open(permanent_path, "wb") as f:
            f.write(file_content)
        
    except Exception as e:
        print(f"Upload processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    # Store metadata
    textbook_metadata = {
        "textbook_id": textbook_id,
        "student_id": student_id,
        "subject": subject,
        "grade": grade,
        "filename": file.filename,
        "file_size": len(file_content),
        "chunks_indexed": chunks_count,
        "status": "ready",
        "uploaded_at": datetime.now().isoformat(),
        "file_path": permanent_path
    }
    
    textbooks_db[textbook_id] = textbook_metadata
    
    # Update student profile
    profile = students_db[student_id]
    profile["textbook_uploaded"] = True
    profile["textbook_id"] = textbook_id
    profile["xp"] += 10  # Reward for uploading textbook
    profile["level"] = (profile["xp"] // 50) + 1
    
    return {
        "success": True,
        "textbook_id": textbook_id,
        "chunks_indexed": chunks_count,
        "status": "ready",
        "message": f"Your {subject} textbook is ready! {chunks_count} knowledge chunks indexed. 🎉",
        "xp_earned": 10,
        "total_xp": profile["xp"]
    }


@router.get("/api/textbook/status/{textbook_id}")
async def get_textbook_status(textbook_id: str):
    """
    Check processing status of an uploaded textbook
    """
    if textbook_id not in textbooks_db:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    metadata = textbooks_db[textbook_id]
    
    return {
        "success": True,
        "textbook_id": textbook_id,
        "status": metadata["status"],
        "chunks_indexed": metadata["chunks_indexed"],
        "subject": metadata["subject"],
        "grade": metadata["grade"],
        "uploaded_at": metadata["uploaded_at"]
    }


@router.get("/api/textbook/student/{student_id}")
async def get_student_textbooks(student_id: str):
    """
    Get all textbooks for a student
    """
    students_db = get_students_db()
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Find all textbooks for this student
    student_textbooks = [
        metadata for metadata in textbooks_db.values()
        if metadata["student_id"] == student_id
    ]
    
    return {
        "success": True,
        "student_id": student_id,
        "textbooks": student_textbooks,
        "count": len(student_textbooks)
    }


@router.delete("/api/textbook/{textbook_id}")
async def delete_textbook(textbook_id: str, student_id: str):
    """
    Delete a textbook and its ChromaDB collection
    """
    students_db = get_students_db()
    
    if textbook_id not in textbooks_db:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    metadata = textbooks_db[textbook_id]
    
    # Verify ownership
    if metadata["student_id"] != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this textbook")
    
    # Delete from ChromaDB
    from core.ingestion import delete_collection
    deleted = delete_collection(student_id, metadata["subject"])
    
    # Delete file
    if os.path.exists(metadata["file_path"]):
        os.remove(metadata["file_path"])
    
    # Remove metadata
    del textbooks_db[textbook_id]
    
    # Update student profile
    profile = students_db[student_id]
    profile["textbook_uploaded"] = False
    if "textbook_id" in profile:
        del profile["textbook_id"]
    
    return {
        "success": True,
        "message": "Textbook deleted",
        "chroma_deleted": deleted
    }
