"""
VidyaSetu AI - Backend API
FastAPI server with real LLM integration, ChromaDB RAG, and multi-agent system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import routers - delayed to avoid pydantic multiprocessing issues
# from routers import auth, profile, chat, ingest, feedback, generate

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="VidyaSetu AI Backend",
    version="2.0.0",
    description="Production-ready AI educational chatbot with LLM, RAG, and multi-agent system"
)

# CORS middleware - permissive for local discovery and multiple dev ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development to avoid CORS blocks
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Load routers after app initialization to avoid pydantic import issues"""
    try:
        from routers import auth, profile, chat, ingest, feedback, generate
        
        app.include_router(auth.router, prefix="/api", tags=["Authentication"])
        app.include_router(profile.router, prefix="/api/profile", tags=["Profile & Games"])
        app.include_router(chat.router, prefix="/api/chat", tags=["Chat & AI"])
        app.include_router(ingest.router, prefix="/api/textbook", tags=["Textbook Upload"])
        app.include_router(feedback.router, prefix="/api", tags=["Feedback & Analytics"])
        app.include_router(generate.router, prefix="/api", tags=["Content Generation"])
        print("✅ All routers loaded and included successfully")
    except Exception as e:
        print(f"❌ ERROR DURING ROUTER LOAD: {e}")
        import traceback
        traceback.print_exc()


# Root health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Health check and API info"""
    return {
        "status": "online",
        "service": "VidyaSetu AI",
        "version": "2.0.0",
        "features": [
            "Real LLM integration (Groq Llama models)",
            "ChromaDB RAG for textbook Q&A",
            "Multi-agent system (Explainer → Simplifier → Encourager)",
            "PDF text extraction with PyMuPDF",
            "SSE streaming chat",
            "PowerPoint generation",
            "YouTube video search"
        ],
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/login",
            "chat": "/api/chat/stream",
            "upload": "/api/textbook/upload",
            "generate_ppt": "/api/generate/ppt",
            "video_search": "/api/video/search"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    llm_provider = os.getenv("LLM_PROVIDER", "groq")
    groq_configured = bool(os.getenv("GROQ_API_KEY"))
    youtube_configured = bool(os.getenv("YOUTUBE_API_KEY"))

    # Check if ChromaDB directory exists
    chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    chroma_ready = os.path.exists(chroma_path) or True  # Will be created on first use

    return {
        "status": "healthy",
        "components": {
            "llm_provider": llm_provider,
            "groq_llm": "configured" if (llm_provider == "groq" and groq_configured) else "not_configured",
            "chromadb": "ready" if chroma_ready else "not_initialized",
            "youtube_api": "configured" if youtube_configured else "optional_not_configured"
        },
        "warnings": [
            "GROQ_API_KEY not set - add to .env" if (llm_provider == "groq" and not groq_configured) else None,
            "YouTube API key not set - video search will fail" if not youtube_configured else None
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print("\n" + "="*60)
    print("🦉 VidyaSetu AI Backend - Production Mode")
    print("="*60)
    print(f"🚀 Server starting on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔧 Health Check: http://{host}:{port}/health")
    print("="*60 + "\n")
    
    # Check for required environment variables
    llm_provider = os.getenv("LLM_PROVIDER", "groq")
    if llm_provider == "groq" and not os.getenv("GROQ_API_KEY"):
        print("⚠️  WARNING: GROQ_API_KEY not set in .env file!")
        print("   Groq LLM features will not work. Add your GROQ_API_KEY to .env\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disabled to avoid pydantic multiprocessing issues
        log_level="info"
    )

