"""
VidyaSetu AI — Ingestion Pipeline
PDF extraction → smart chunking → embedding → ChromaDB storage

KEY FIXES over original:
  1. Chunk size raised to 800 chars (was 300 — too small, lost sentence context)
  2. Page numbers stored in metadata → enables citations
  3. Chunks filtered for minimum length to skip headers/noise
  4. Embedding model lazy-loaded once and reused (was re-created each call)
"""

import os
from typing import Optional

# ── Optional imports — app starts even without them ──────────────────────────
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    fitz = None
    FITZ_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    TEXT_SPLITTER_AVAILABLE = True
except ImportError:
    RecursiveCharacterTextSplitter = None
    TEXT_SPLITTER_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from core.config import Config

# ── Singletons — initialised once, reused everywhere ─────────────────────────
_embedding_model: Optional[object] = None
_chroma_client:   Optional[object] = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")
        print(f"[Ingestion] Loading embedding model '{Config.EMBEDDING_MODEL}' (one-time)…")
        _embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
    return _embedding_model


def _get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("chromadb not installed. Run: pip install chromadb")
        _chroma_client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
    return _chroma_client


# ── Embedding helpers ─────────────────────────────────────────────────────────
def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_embedding_model()
    return model.encode(texts, show_progress_bar=False, batch_size=64).tolist()


def embed_query(query: str) -> list[float]:
    model = _get_embedding_model()
    return model.encode([query], show_progress_bar=False)[0].tolist()


# ── PDF extraction with page tracking ────────────────────────────────────────
def extract_text_from_pdf(file_path: str) -> tuple[str, list[dict]]:
    """
    Extract text from PDF, return:
      - full_text: concatenated text (for compatibility)
      - page_chunks: list of {"text": ..., "page": N}

    FIX: We now track which page each block of text came from so we can
         include page citations in answers.
    """
    if not FITZ_AVAILABLE:
        raise RuntimeError("PyMuPDF not installed. Run: pip install pymupdf")

    doc = fitz.open(file_path)
    full_text = ""
    page_chunks = []

    for page_num, page in enumerate(doc, start=1):
        page_text = page.get_text("text")  # plain text mode
        if page_text.strip():
            full_text += page_text
            page_chunks.append({
                "text": page_text,
                "page": page_num
            })

    doc.close()
    return full_text, page_chunks


# ── Collection name helper ────────────────────────────────────────────────────
def _collection_name(student_id: str, subject: str) -> str:
    sanitized = subject.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
    name = f"vs_{student_id[:8]}_{sanitized}"  # vs = VidyaSetu prefix
    return name[:63]  # ChromaDB limit


# ── Main ingestion function ───────────────────────────────────────────────────
def chunk_and_embed(
    text: str,
    student_id: str,
    subject: str,
    grade: int,
    textbook_id: str,
    page_chunks: list[dict] = None,  # NEW: pass page-aware chunks for citations
) -> int:
    """
    Chunk, embed, and store textbook content in ChromaDB.

    FIX 1 — Chunk size:  800 chars with 150 overlap (was 300/50).
             Larger chunks keep complete sentences, reducing fragmented retrieval.

    FIX 2 — Page metadata: Each chunk stores the source page number, enabling
             citation of textbook pages in answers.

    FIX 3 — Noise filtering: Chunks shorter than 100 chars (headers, page numbers,
             blank lines) are skipped.

    Returns: number of chunks indexed
    """
    if not TEXT_SPLITTER_AVAILABLE:
        raise RuntimeError("langchain-text-splitters not installed. Run: pip install langchain-text-splitters")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,      # 800 (was 300)
        chunk_overlap=Config.CHUNK_OVERLAP, # 150 (was 50)
        separators=["\n\n", "\n", ". ", "! ", "? ", " "],
        length_function=len,
        is_separator_regex=False,
    )

    # ── Build chunks with page numbers ───────────────────────────────────────
    chunks_with_meta = []

    if page_chunks:
        # Page-aware path: chunk each page separately to preserve page numbers
        for page_info in page_chunks:
            page_text = page_info["text"]
            page_num  = page_info["page"]
            if len(page_text.strip()) < 50:
                continue
            for chunk in splitter.split_text(page_text):
                if len(chunk.strip()) >= 100:  # skip noise
                    chunks_with_meta.append({
                        "text": chunk.strip(),
                        "page": page_num
                    })
    else:
        # Fallback: no page info
        for chunk in splitter.split_text(text):
            if len(chunk.strip()) >= 100:
                chunks_with_meta.append({"text": chunk.strip(), "page": 0})

    if not chunks_with_meta:
        raise ValueError("No usable text chunks extracted from PDF")

    # ── Create/replace ChromaDB collection ───────────────────────────────────
    client = _get_chroma_client()
    col_name = _collection_name(student_id, subject)

    try:
        client.delete_collection(col_name)
        print(f"[Ingestion] Replaced existing collection '{col_name}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=col_name,
        metadata={
            "hnsw:space": "cosine",  # cosine similarity for semantic search
            "student_id": student_id,
            "subject": subject,
            "grade": str(grade),
            "textbook_id": textbook_id,
        }
    )

    # ── Batch embed and store ─────────────────────────────────────────────────
    texts      = [c["text"] for c in chunks_with_meta]
    pages      = [c["page"] for c in chunks_with_meta]
    batch_size = 64

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_pages = pages[i : i + batch_size]
        batch_embs  = embed_texts(batch_texts)

        collection.add(
            documents=batch_texts,
            embeddings=batch_embs,
            ids=[f"{textbook_id}_{i + j}" for j in range(len(batch_texts))],
            metadatas=[{
                "student_id":   student_id,
                "subject":      subject,
                "grade":        grade,
                "page":         batch_pages[j],
                "chunk_index":  i + j,
                "textbook_id":  textbook_id,
            } for j in range(len(batch_texts))],
        )
        print(f"[Ingestion] Embedded batch {i // batch_size + 1} ({len(batch_texts)} chunks)")

    total = len(texts)
    print(f"[Ingestion] ✅ Done — {total} chunks indexed for {student_id}/{subject}")
    return total


# ── Collection access helpers ─────────────────────────────────────────────────
def get_collection(student_id: str, subject: str):
    name = _collection_name(student_id, subject)
    return _get_chroma_client().get_collection(name)


def delete_collection(student_id: str, subject: str) -> bool:
    name = _collection_name(student_id, subject)
    try:
        _get_chroma_client().delete_collection(name)
        return True
    except Exception:
        return False


def get_collection_stats(student_id: str, subject: str) -> dict:
    try:
        col   = get_collection(student_id, subject)
        count = col.count()
        return {"exists": True, "chunk_count": count, "metadata": col.metadata}
    except Exception:
        return {"exists": False, "chunk_count": 0, "metadata": {}}