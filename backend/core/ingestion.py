"""
PDF Ingestion & ChromaDB Embedding Pipeline
Extracts text from PDF, chunks it, and stores in vector database
"""

import fitz  # PyMuPDF
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from typing import Tuple

load_dotenv()

# Initialize ChromaDB (persists to disk, survives restarts)
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Initialize OpenAI embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using PyMuPDF
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Concatenated text from all pages
    """
    doc = fitz.open(file_path)
    full_text = ""
    
    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        # Add page marker for better context preservation
        full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
    
    doc.close()
    return full_text.strip()


def chunk_and_embed(
    text: str, 
    student_id: str, 
    subject: str, 
    grade: int, 
    textbook_id: str
) -> int:
    """
    Split text into chunks and embed them in ChromaDB
    
    Args:
        text: Full extracted text from PDF
        student_id: Unique student identifier
        subject: Subject name (Math, Science, etc.)
        grade: Student's grade level (1-5)
        textbook_id: Unique textbook identifier
        
    Returns:
        Number of chunks created and embedded
    """
    # Chunk size adjusted for grade level
    # Lower grades = smaller chunks for focused retrieval
    chunk_sizes = {
        1: 200,
        2: 250,
        3: 300,
        4: 350,
        5: 400
    }
    chunk_size = chunk_sizes.get(grade, 300)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", "! ", "? ", " "],
        length_function=len,
    )
    
    chunks = splitter.split_text(text)
    
    if not chunks:
        return 0
    
    # One ChromaDB collection per student+subject
    # This ensures student A's Science book doesn't mix with student B's
    collection_name = f"student_{student_id}_{subject.lower().replace(' ', '_')}"
    
    # Delete old collection if re-uploading (new textbook replaces old)
    try:
        existing = chroma_client.get_collection(collection_name)
        chroma_client.delete_collection(collection_name)
        print(f"Deleted old collection: {collection_name}")
    except Exception:
        pass  # Collection doesn't exist yet
    
    # Create fresh collection
    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"student_id": student_id, "subject": subject, "grade": grade}
    )
    
    # Embed in batches to avoid rate limits and memory issues
    batch_size = 50
    total_chunks = len(chunks)
    
    for i in range(0, total_chunks, batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_embeddings = embeddings.embed_documents(batch_chunks)
        
        # Generate unique IDs and metadata for this batch
        batch_ids = [f"{textbook_id}_chunk_{i+j}" for j in range(len(batch_chunks))]
        batch_metadatas = [{
            "student_id": student_id,
            "subject": subject,
            "grade": grade,
            "chunk_index": i + j,
            "textbook_id": textbook_id,
            "total_chunks": total_chunks
        } for j in range(len(batch_chunks))]
        
        collection.add(
            documents=batch_chunks,
            embeddings=batch_embeddings,
            ids=batch_ids,
            metadatas=batch_metadatas
        )
        
        print(f"Embedded batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}")
    
    return total_chunks


def get_collection(student_id: str, subject: str):
    """
    Retrieve a student's subject-specific ChromaDB collection
    
    Args:
        student_id: Unique student identifier
        subject: Subject name
        
    Returns:
        ChromaDB collection object
        
    Raises:
        ValueError: If collection doesn't exist (no textbook uploaded)
    """
    collection_name = f"student_{student_id}_{subject.lower().replace(' ', '_')}"
    
    try:
        return chroma_client.get_collection(collection_name)
    except Exception as e:
        raise ValueError(f"No textbook found for student {student_id} in {subject}") from e


def delete_collection(student_id: str, subject: str) -> bool:
    """
    Delete a student's textbook collection
    
    Args:
        student_id: Unique student identifier
        subject: Subject name
        
    Returns:
        True if deleted, False if didn't exist
    """
    collection_name = f"student_{student_id}_{subject.lower().replace(' ', '_')}"
    
    try:
        chroma_client.delete_collection(collection_name)
        return True
    except Exception:
        return False


def get_collection_stats(student_id: str, subject: str) -> dict:
    """
    Get statistics about a textbook collection
    
    Args:
        student_id: Unique student identifier
        subject: Subject name
        
    Returns:
        Dictionary with count, metadata
    """
    try:
        collection = get_collection(student_id, subject)
        count = collection.count()
        metadata = collection.metadata
        
        return {
            "exists": True,
            "chunk_count": count,
            "metadata": metadata
        }
    except ValueError:
        return {
            "exists": False,
            "chunk_count": 0,
            "metadata": {}
        }
