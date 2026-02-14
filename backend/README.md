# VidyaSetu AI - Backend

FastAPI backend for the VidyaSetu AI educational chatbot.

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Server

```bash
# Development mode (auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/login` - Student login/registration

### Profile & Games
- `POST /api/profile/games/submit` - Submit game results
- `GET /api/profile/{student_id}` - Get student profile

### Textbook Management
- `POST /api/textbook/upload` - Upload textbook PDF
- `GET /api/textbook/status/{textbook_id}` - Check processing status

### Chat
- `GET /api/chat/stream` - Streaming chat with SSE
- `GET /api/chat/history/{student_id}` - Get chat history

### Analytics
- `GET /api/satisfaction/{student_id}` - Get satisfaction chart data
- `POST /api/feedback` - Log user feedback

### Content Generation
- `POST /api/generate/ppt` - Generate PowerPoint summary
- `GET /api/video/search` - Search educational videos

## Architecture

The backend uses:
- **FastAPI** for high-performance async API
- **SSE (Server-Sent Events)** for streaming chat responses
- **Multi-agent system** simulation (Explainer, Simplifier, Encourager)
- In-memory storage (replace with PostgreSQL/MongoDB for production)

## For Production

1. Replace in-memory storage with proper database
2. Add ChromaDB for RAG functionality
3. Integrate actual LLM (OpenAI, Anthropic, or local model)
4. Add YouTube API for video search
5. Implement PDF processing with LangChain
6. Add Redis for caching and session management
7. Set up proper authentication and authorization
