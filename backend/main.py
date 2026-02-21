"""
VidyaSetu AI - Backend API
FastAPI server with Groq LLM, ChromaDB RAG, and multi-agent system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="VidyaSetu AI Backend",
    version="2.0.0",
    description="Production-ready AI educational chatbot with Groq LLM, RAG, and multi-agent system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    try:
        from routers import auth, profile, chat, ingest, feedback, generate, stt, tts

        app.include_router(auth.router,     prefix="/api",          tags=["Authentication"])
        app.include_router(profile.router,  prefix="/api/profile",  tags=["Profile & Games"])
        app.include_router(chat.router,     prefix="/api/chat",     tags=["Chat & AI"])
        app.include_router(ingest.router,   prefix="/api/textbook", tags=["Textbook Upload"])
        app.include_router(feedback.router, prefix="/api",          tags=["Feedback & Analytics"])
        app.include_router(generate.router, prefix="/api",          tags=["Content Generation"])
        app.include_router(stt.router,      prefix="/api/stt",      tags=["Speech-to-Text"])
        app.include_router(tts.router,      prefix="/api/tts",      tags=["Text-to-Speech"])

        print("✅ All routers loaded successfully")

        # Warn clearly if Groq key is missing at startup
        if not os.getenv("GROQ_API_KEY"):
            print("⚠️  WARNING: GROQ_API_KEY not set — chat will not work!")
        else:
            print("✅ GROQ_API_KEY detected")

    except Exception as e:
        print(f"❌ ERROR DURING ROUTER LOAD: {e}")
        import traceback
        traceback.print_exc()


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "VidyaSetu AI",
        "version": "2.0.0",
        "features": [
            "Groq LLM (llama-3.3-70b + llama-3.1-8b)",
            "ChromaDB RAG for textbook Q&A",
            "Multi-agent system (Explainer → Simplifier → Encourager)",
            "PDF text extraction with PyMuPDF",
            "SSE streaming chat",
            "PowerPoint generation",
            "YouTube video search"
        ],
        "docs": "/docs",
        "endpoints": {
            "auth":         "/api/login",
            "chat":         "/api/chat/stream",
            "upload":       "/api/textbook/upload",
            "generate_ppt": "/api/generate/ppt",
            "video_search": "/api/video/search"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    # BUG FIX: was checking the raw API key string as env var name instead of GROQ_API_KEY
    groq_configured    = bool(os.getenv("GROQ_API_KEY"))
    youtube_configured = bool(os.getenv("YOUTUBE_API_KEY"))
    chroma_path        = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    chroma_ready       = os.path.exists(chroma_path)

    return {
        "status": "healthy",
        "components": {
            "llm_provider": "groq",
            "groq_llm":     "configured" if groq_configured  else "❌ not_configured — add GROQ_API_KEY to .env",
            "chromadb":     "ready"       if chroma_ready     else "will be created on first upload",
            "youtube_api":  "configured" if youtube_configured else "optional — not configured",
        },
        "warnings": [
            w for w in [
                "GROQ_API_KEY not set — add to .env" if not groq_configured    else None,
                "YOUTUBE_API_KEY not set — video search disabled" if not youtube_configured else None,
            ] if w
        ]
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    print("\n" + "=" * 60)
    print("🦉 VidyaSetu AI Backend — Groq Mode")
    print("=" * 60)
    print(f"🚀 Server: http://{host}:{port}")
    print(f"📚 Docs:   http://{host}:{port}/docs")
    print(f"🔧 Health: http://{host}:{port}/health")
    print("=" * 60 + "\n")

    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  WARNING: GROQ_API_KEY not set in .env — chat will fail!\n")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )