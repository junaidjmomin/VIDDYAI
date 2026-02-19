"""
VidyaSetu AI — RAG Retrieval Module

KEY FIXES over original:
  1. Metadata filtering by student_id + subject (was fetching from wrong collections)
  2. Distance/score threshold — poor matches are discarded (prevents irrelevant context)
  3. Re-ranking by relevance score before returning chunks
  4. Returns rich context with page citations, not just raw text
  5. Graceful fallback when no textbook is uploaded
"""

from typing import Optional
from core.ingestion import get_collection, embed_query
from core.config import Config


# ── Data classes (plain dicts for JSON compatibility) ─────────────────────────
def _make_chunk(text: str, page: int, score: float, chunk_index: int) -> dict:
    return {
        "text":        text,
        "page":        page,
        "score":       round(score, 4),
        "chunk_index": chunk_index,
    }


# ── Core retrieval ────────────────────────────────────────────────────────────
def retrieve_chunks(
    query:      str,
    student_id: str,
    subject:    str,
    k:          int  = None,
    min_score:  float = None,
) -> list[dict]:
    """
    Retrieve the most relevant chunks for a query from the student's textbook.

    FIX 1 — Metadata WHERE filter:
        ChromaDB `where` clause pins retrieval to the exact student+subject.
        Without this, if multiple students' collections share a client, chunks
        from the wrong student can leak through.

    FIX 2 — Score filtering:
        ChromaDB returns cosine distance (0 = identical, 1 = orthogonal).
        We convert to similarity (1 - distance) and drop chunks below
        Config.RAG_MIN_SCORE. This stops irrelevant paragraphs reaching Gemini.

    FIX 3 — Re-ranking:
        Results are sorted by similarity score descending so the most relevant
        chunk is always presented first in the context window.

    Returns list of chunk dicts with keys: text, page, score, chunk_index
    """
    k         = k         or Config.RAG_TOP_K
    min_score = min_score or Config.RAG_MIN_SCORE

    try:
        collection = get_collection(student_id, subject)
    except Exception as e:
        print(f"[RAG] Collection not found for {student_id}/{subject}: {e}")
        return []

    total_docs = collection.count()
    if total_docs == 0:
        print(f"[RAG] Collection is empty for {student_id}/{subject}")
        return []

    n_results = min(k, total_docs)
    query_emb = embed_query(query)

    try:
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=n_results,
            # FIX 1: metadata filter — only return chunks from this student+subject
            where={
                "$and": [
                    {"student_id": {"$eq": student_id}},
                    {"subject":    {"$eq": subject}},
                ]
            },
            include=["documents", "distances", "metadatas"],
        )
    except Exception as e:
        print(f"[RAG] Query error: {e}")
        return []

    docs      = results.get("documents",  [[]])[0]
    distances = results.get("distances",  [[]])[0]
    metadatas = results.get("metadatas",  [[]])[0]

    if not docs:
        return []

    # FIX 2 + 3: Convert distances → similarity, filter, then sort
    chunks = []
    for doc, dist, meta in zip(docs, distances, metadatas):
        similarity = 1.0 - dist  # cosine distance → similarity
        if similarity < min_score:
            print(f"[RAG] Dropping chunk (score={similarity:.3f} < threshold={min_score})")
            continue
        chunks.append(_make_chunk(
            text        = doc,
            page        = meta.get("page", 0),
            score       = similarity,
            chunk_index = meta.get("chunk_index", -1),
        ))

    # Sort best first
    chunks.sort(key=lambda c: c["score"], reverse=True)

    print(f"[RAG] Retrieved {len(chunks)}/{n_results} chunks above threshold "
          f"(min_score={min_score}) for query: '{query[:60]}…'")
    return chunks


# ── Context builder (for prompt injection) ───────────────────────────────────
def retrieve_context(
    query:      str,
    student_id: str,
    subject:    str,
    k:          int   = None,
    min_score:  float = None,
) -> tuple[str, list[dict]]:
    """
    High-level helper used by agents.py.

    Returns:
        context_text : formatted string ready to inject into the Gemini prompt
        chunks       : raw chunk list (for citation metadata)

    Context format example:
        [Source: Page 12, Relevance: 0.87]
        Plants make food using sunlight through photosynthesis…

        ---

        [Source: Page 14, Relevance: 0.81]
        Chlorophyll is the green pigment that absorbs sunlight…
    """
    chunks = retrieve_chunks(query, student_id, subject, k=k, min_score=min_score)

    if not chunks:
        return "", []

    parts = []
    for c in chunks:
        page_label = f"Page {c['page']}" if c["page"] > 0 else "Textbook"
        parts.append(
            f"[Source: {page_label} | Relevance: {c['score']:.2f}]\n{c['text']}"
        )

    context_text = "\n\n---\n\n".join(parts)
    return context_text, chunks


# ── Citation formatter ────────────────────────────────────────────────────────
def format_citations(chunks: list[dict]) -> str:
    """
    Build a short citation string from retrieved chunks.
    E.g.: "📖 Sources: Pages 12, 14, 15"
    """
    if not chunks:
        return ""
    pages = sorted({c["page"] for c in chunks if c["page"] > 0})
    if not pages:
        return "📖 Source: Your textbook"
    page_str = ", ".join(str(p) for p in pages)
    return f"📖 Source: Your textbook (Page{'s' if len(pages) > 1 else ''} {page_str})"