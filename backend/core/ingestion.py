import fitz  # PyMuPDF
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from core.config import Config
import os

# Load once at startup — cached in memory after first load (~50MB, takes 5s)
embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)

chroma_client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return embedding_model.encode(texts, show_progress_bar=False).tolist()


def embed_query(query: str) -> list[float]:
    return embedding_model.encode([query])[0].tolist()


def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text


def chunk_and_embed(text: str, student_id: str, subject: str, grade: int, textbook_id: str) -> int:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_text(text)

    collection_name = f"student_{student_id}_{subject.lower()}"

    # Drop old collection if re-uploading
    try:
        chroma_client.delete_collection(collection_name)
    except:
        pass

    collection = chroma_client.create_collection(
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
    collection_name = f"student_{student_id}_{subject.lower()}"
    return chroma_client.get_collection(collection_name)

