from core.ingestion import get_collection, embed_query


def retrieve_context(query: str, student_id: str, subject: str, k: int = 5) -> str:
    try:
        collection = get_collection(student_id, subject)
    except Exception:
        return ""

    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
    )

    if not results["documents"] or not results["documents"][0]:
        return ""

    return "\n\n---\n\n".join(results["documents"][0])

