import os
from typing import Optional

# Optional imports — allow backend to run even if some optional packages are not installed
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except Exception:
    chromadb = None
    CHROMADB_AVAILABLE = False

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    TEXT_SPLITTER_AVAILABLE = True
except Exception:
    RecursiveCharacterTextSplitter = None
    TEXT_SPLITTER_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from core.config import Config

# Lazy-initialized components (avoid slow model loading at import time)
_embedding_model: Optional[object] = None
_chroma_client: Optional[object] = None


def _get_embedding_model():
    """Lazy-load SentenceTransformer model on first use."""
    global _embedding_model
    if _embedding_model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
        print("Loading embedding model (first use)...")
        _embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
    return _embedding_model


def _get_chroma_client():
    """Lazy-load ChromaDB client on first use."""
    global _chroma_client
    if _chroma_client is None and CHROMADB_AVAILABLE:
        _chroma_client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
    return _chroma_client


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_embedding_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def embed_query(query: str) -> list[float]:
    model = _get_embedding_model()
    return model.encode([query])[0].tolist()


def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text


def chunk_and_embed(text: str, student_id: str, subject: str, grade: int, textbook_id: str) -> int:
    # Use LangChain text splitter (required)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_text(text)

    # Sanitize collection name for ChromaDB (lowercase, alphanumeric, underscores/hyphens only)
    sanitized_subject = subject.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
    collection_name = f"student_{student_id}_{sanitized_subject}"
    
    # Ensure length doesn't exceed 63
    if len(collection_name) > 63:
        collection_name = collection_name[:63]

    # Drop old collection if re-uploading
    client = _get_chroma_client()
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Batch embed — sentence-transformers handles batching internally
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_embeddings = embed_texts(batch)
        collection.add(
            documents=batch,
            embeddings=batch_embeddings,
            ids=[f"{textbook_id}_{i+j}" for j in range(len(batch))],
            metadatas=[{
                "student_id": student_id,
                "subject": subject,
                "grade": grade,
                "chunk_index": i + j
            } for j in range(len(batch))]
        )

    return len(chunks)


def get_collection(student_id: str, subject: str):
    sanitized_subject = subject.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
    collection_name = f"student_{student_id}_{sanitized_subject}"
    if len(collection_name) > 63:
        collection_name = collection_name[:63]
    return _get_chroma_client().get_collection(collection_name)


def delete_collection(student_id: str, subject: str) -> bool:
    """Delete a student's textbook collection

    Returns True if deleted, False otherwise.
    """
    sanitized_subject = subject.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
    collection_name = f"student_{student_id}_{sanitized_subject}"
    if len(collection_name) > 63:
        collection_name = collection_name[:63]
    try:
        _get_chroma_client().delete_collection(collection_name)
        return True
    except Exception:
        return False


def get_collection_stats(student_id: str, subject: str) -> dict:
    """Return basic stats for a student's collection."""
    try:
        collection = get_collection(student_id, subject)
        count = collection.count()
        metadata = getattr(collection, "metadata", {})
        return {"exists": True, "chunk_count": count, "metadata": metadata}
    except Exception:
        return {"exists": False, "chunk_count": 0, "metadata": {}}

