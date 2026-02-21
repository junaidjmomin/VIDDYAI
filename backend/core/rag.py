"""
VidyaSetu AI — STRICT RAG Retrieval Module

ANTI-HALLUCINATION VERSION

Key Guarantees:
✔ Retrieval locked to student + subject
✔ Weak chunks removed
✔ Returns NONE when no grounded evidence exists
✔ Limits context size
✔ Forces evidence-based answering
"""

from typing import Optional, Tuple, List
from core.ingestion import get_collection, embed_query
from core.config import Config


# ─────────────────────────────────────────────────────────
# Helper: chunk builder
# ─────────────────────────────────────────────────────────
def _make_chunk(text: str, page: int, score: float, chunk_index: int) -> dict:
    return {
        "text": text,
        "page": page,
        "score": round(score, 4),
        "chunk_index": chunk_index,
    }


# ─────────────────────────────────────────────────────────
# Core Retrieval
# ─────────────────────────────────────────────────────────
def retrieve_chunks(
    query: str,
    student_id: str,
    subject: str,
    k: int = None,
    min_score: float = None,
) -> List[dict]:

    k = k or Config.RAG_TOP_K
    min_score = min_score or Config.RAG_MIN_SCORE

    # Load collection
    try:
        collection = get_collection(student_id, subject)
    except Exception as e:
        print(f"[RAG] ❌ Collection missing: {student_id}/{subject}")
        return []

    total_docs = collection.count()
    if total_docs == 0:
        print(f"[RAG] ❌ Empty collection")
        return []

    query_emb = embed_query(query)
    n_results = min(k, total_docs)

    try:
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=n_results,
            where={
                "$and": [
                    {"student_id": {"$eq": student_id}},
                    {"subject": {"$eq": subject}},
                ]
            },
            include=["documents", "distances", "metadatas"],
        )
    except Exception as e:
        print(f"[RAG] ❌ Query failed:", e)
        return []

    docs = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not docs:
        return []

    chunks = []

    # Convert cosine distance → similarity
    for doc, dist, meta in zip(docs, distances, metadatas):
        similarity = 1.0 - dist

        # STRICT FILTER
        if similarity < min_score:
            print(
                f"[RAG] Dropping chunk "
                f"(score={similarity:.3f} < threshold={min_score})"
            )
            continue

        chunks.append(
            _make_chunk(
                text=doc,
                page=meta.get("page", 0),
                score=similarity,
                chunk_index=meta.get("chunk_index", -1),
            )
        )

    # Sort best → worst
    chunks.sort(key=lambda c: c["score"], reverse=True)

    # 🔥 LIMIT CONTEXT SIZE (anti hallucination)
    chunks = chunks[:3]

    print(
        f"[RAG] ✅ Retrieved {len(chunks)} grounded chunks "
        f"for query: '{query[:60]}…'"
    )

    return chunks


# ─────────────────────────────────────────────────────────
# Context Builder (STRICT MODE)
# ─────────────────────────────────────────────────────────
def retrieve_context(
    query: str,
    student_id: str,
    subject: str,
    k: int = None,
    min_score: float = None,
) -> Tuple[Optional[str], List[dict]]:

    chunks = retrieve_chunks(
        query,
        student_id,
        subject,
        k=k,
        min_score=min_score,
    )

    # 🚨 CRITICAL FIX
    # NO CONTEXT → NO ANSWER
    if not chunks:
        print("[RAG] ❌ No grounded context found")
        return None, []

    parts = []

    for c in chunks:
        page_label = (
            f"Page {c['page']}" if c["page"] > 0 else "Textbook"
        )

        parts.append(
            f"[Source: {page_label} | Relevance: {c['score']:.2f}]\n"
            f"{c['text']}"
        )

    context_text = "\n\n---\n\n".join(parts)

    return context_text, chunks


# ─────────────────────────────────────────────────────────
# Citation Formatter
# ─────────────────────────────────────────────────────────
def format_citations(chunks: List[dict]) -> str:

    if not chunks:
        return ""

    pages = sorted({c["page"] for c in chunks if c["page"] > 0})

    if not pages:
        return "📖 Source: Your textbook"

    page_str = ", ".join(str(p) for p in pages)

    return (
        f"📖 Source: Your textbook "
        f"(Page{'s' if len(pages) > 1 else ''} {page_str})"
    )