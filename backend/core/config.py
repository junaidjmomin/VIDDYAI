import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

    # Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_HEAVY = os.getenv("GROQ_MODEL_HEAVY", "llama-3.3-70b-versatile")
    GROQ_MODEL_FAST = os.getenv("GROQ_MODEL_FAST", "llama-3.1-8b-instant")

    # Embeddings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Paths
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    @classmethod
    def get_heavy_llm(cls):
        if cls.LLM_PROVIDER == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(
                api_key=cls.GROQ_API_KEY,
                model=cls.GROQ_MODEL_HEAVY,
                temperature=0.7,
            )
        else:
            # Fallback to OpenAI if ever needed
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    @classmethod
    def get_fast_llm(cls):
        if cls.LLM_PROVIDER == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(
                api_key=cls.GROQ_API_KEY,
                model=cls.GROQ_MODEL_FAST,
                temperature=0.7,
            )
        else:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
