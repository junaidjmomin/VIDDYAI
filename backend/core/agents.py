"""
VidyaSetu AI — Config
Groq as primary LLM provider
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── LLM Provider ──────────────────────────────────────────────────────────
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" is primary

    # ── Groq (PRIMARY) ────────────────────────────────────────────────────────
    GROQ_API_KEY       = os.getenv("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", "")
    GROQ_MODEL_HEAVY   = os.getenv("GROQ_MODEL_HEAVY", "llama-3.3-70b-versatile")  # Explainer
    GROQ_MODEL_FAST    = os.getenv("GROQ_MODEL_FAST",  "llama-3.1-8b-instant")     # Simplifier + Encourager

    # ── Embeddings ────────────────────────────────────────────────────────────
    # all-MiniLM-L6-v2 is fast and good enough for textbook RAG
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # ── ChromaDB ──────────────────────────────────────────────────────────────
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # ── RAG tuning ────────────────────────────────────────────────────────────
    # Chunk size 800 chars with 150 overlap gives complete sentences + context
    CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
    # How many chunks to pull per query (top-k)
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "6"))
    # Minimum cosine similarity score to include a chunk (0–1, lower = more permissive)
    RAG_MIN_SCORE = float(os.getenv("RAG_MIN_SCORE", "0.30"))

    # ─────────────────────────────────────────────────────────────────────────
    @classmethod
    def is_llm_configured(cls) -> bool:
        return bool(cls.GROQ_API_KEY) and "your_" not in cls.GROQ_API_KEY.lower()

    @classmethod
    def get_heavy_llm(cls):
        """High-quality model for the Explainer agent (accurate, slower)."""
        return cls._build_groq(cls.GROQ_MODEL_HEAVY, temperature=0.3)

    @classmethod
    def get_fast_llm(cls):
        """Fast model for Simplifier + Encourager agents (quick, cheaper)."""
        return cls._build_groq(cls.GROQ_MODEL_FAST, temperature=0.5)

    # ── Private builder ───────────────────────────────────────────────────────
    @classmethod
    def _build_groq(cls, model: str, temperature: float):
        try:
            from langchain_groq import ChatGroq
        except ImportError as e:
            raise RuntimeError(
                "Missing package: pip install langchain-groq"
            ) from e

        return ChatGroq(
            api_key=cls.GROQ_API_KEY,
            model=model,
            temperature=temperature,
        )