"""
RAG (Retrieval-Augmented Generation) Module
Retrieves relevant context from ChromaDB for answering questions
"""

from langchain_openai import OpenAIEmbeddings
from core.ingestion import get_collection
import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)


def retrieve_context(query: str, student_id: str, subject: str, k: int = 5) -> str:
    """
    Retrieve relevant text chunks from the student's textbook
    
    Args:
        query: Student's question
        student_id: Unique student identifier
        subject: Subject name
        k: Number of chunks to retrieve (default: 5)
        
    Returns:
        Combined context string from top-k relevant chunks
        Returns empty string if no textbook found
    """
    try:
        collection = get_collection(student_id, subject)
    except ValueError:
        # No textbook uploaded yet
        print(f"No textbook found for student {student_id} in {subject}")
        return ""
    
    # Get total number of chunks in collection
    total_chunks = collection.count()
    
    if total_chunks == 0:
        return ""
    
    # Don't retrieve more chunks than exist
    k = min(k, total_chunks)
    
    # Embed the query
    query_embedding = embeddings.embed_query(query)
    
    # Query ChromaDB for most similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    # Check if results exist
    if not results["documents"] or not results["documents"][0]:
        return ""
    
    # Extract chunks and format with separators
    chunks = results["documents"][0]
    distances = results["distances"][0] if "distances" in results and results["distances"] else []
    
    # Filter out very dissimilar chunks (distance > 1.0 means not very relevant)
    filtered_chunks = []
    for i, chunk in enumerate(chunks):
        if i < len(distances) and distances[i] < 1.2:  # Similarity threshold
            filtered_chunks.append(chunk)
        else:
            # Still include if we have very few results
            if len(filtered_chunks) < 2:
                filtered_chunks.append(chunk)
    
    # Join chunks with clear separators
    context = "\n\n---\n\n".join(filtered_chunks if filtered_chunks else chunks[:3])
    
    return context


def retrieve_context_with_metadata(
    query: str, 
    student_id: str, 
    subject: str, 
    k: int = 5
) -> dict:
    """
    Retrieve context with additional metadata (for debugging/UI display)
    
    Args:
        query: Student's question
        student_id: Unique student identifier
        subject: Subject name
        k: Number of chunks to retrieve
        
    Returns:
        Dictionary with context, chunk_count, relevance_scores
    """
    try:
        collection = get_collection(student_id, subject)
    except ValueError:
        return {
            "context": "",
            "chunks": [],
            "chunk_count": 0,
            "has_textbook": False
        }
    
    total_chunks = collection.count()
    k = min(k, total_chunks)
    
    if total_chunks == 0:
        return {
            "context": "",
            "chunks": [],
            "chunk_count": 0,
            "has_textbook": False
        }
    
    query_embedding = embeddings.embed_query(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    
    if not results["documents"] or not results["documents"][0]:
        return {
            "context": "",
            "chunks": [],
            "chunk_count": 0,
            "has_textbook": True
        }
    
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0] if "metadatas" in results else []
    distances = results["distances"][0] if "distances" in results else []
    
    # Build structured chunk info
    chunk_info = []
    for i, chunk in enumerate(chunks):
        chunk_info.append({
            "text": chunk,
            "chunk_index": metadatas[i].get("chunk_index", i) if i < len(metadatas) else i,
            "relevance_score": round(1 - (distances[i] / 2), 3) if i < len(distances) else 0,
            "distance": distances[i] if i < len(distances) else 0
        })
    
    context = "\n\n---\n\n".join(chunks)
    
    return {
        "context": context,
        "chunks": chunk_info,
        "chunk_count": len(chunks),
        "has_textbook": True,
        "total_chunks_in_db": total_chunks
    }
