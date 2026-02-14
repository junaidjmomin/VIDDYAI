# VidyaSetu AI Backend - Production Ready

FastAPI backend with **real LLM integration**, ChromaDB RAG, and multi-agent system.

## ⚡ Quick Start

### Installation

```bash
# 1. Create virtual environment (recommended)
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install ALL dependencies (including LangChain, ChromaDB, etc.)
pip install -r requirements.txt
```

### Configuration

**CRITICAL**: Create `.env` file with your OpenAI API key:

```bash
# Copy template
cp .env.example .env

# Edit .env and add your API key:
# O🏗️ Architecture

### Core Modules (NEW!)

- **`core/ingestion.py`** - PDF extraction (PyMuPDF) + ChromaDB embedding
- **`core/rag.py`** - Vector search retriever for textbook context
- **`core/prompt_builder.py`** - Adaptive system prompts (grade, learning style, confidence)
- **`core/agents.py`** - 3-agent LangChain pipeline:
  - **Explainer Agent**: Creates factual explanation from textbook
  - **Simplifier Agent**: Converts to grade-level language + Indian examples
  - **Encourager Agent**: Adds motivation and memory tips

### API Routers

- **`routers/auth.py`** - Student login/registration
- **`routers/profile.py`** - IQ/EQ games and profile building
- **`routers/chat.py`** - **Real SSE streaming** with LangChain agents
- **`routers/ingest.py`** - **Real PDF processing** with ChromaDB indexing
- **`routers/feedback.py`** - Satisfaction tracking
- **`routers/generate.py`** - **Real PowerPoint** generation + YouTube search

## 📡 API Endpoints

### Authentication
- `POST /api/login` - Student registration
- `GET /api/profile/{student_id}` - Get profile

### Profile & Games
- `POST /api/profile/games/submit` - Submit game results
- `GET /api/profile/{student_id}/stats` - Get statistics

### Textbook Management (ChromaDB RAG)
- `POST /api/textbook/upload` - **Upload PDF → extract → embed in ChromaDB**
- `GET /api/textbook/status/{textbook_id}` - Processing status
- `GET /api/textbook/student/{student_id}` - All student textbooks

### Chat (LangChain Multi-Agent)
- `GET /api/chat/stream` - **SSE streaming with 3-agent pipeline**
- `POST /api/chat/message` - Non-streaming chat
- `GET /api/chat/history/{student_id}` - Chat history

### Analytics
- `GET /api/satisfaction/{student_id}` - Satisfaction chart data
- `🔥 What Changed from Mock → Production

| Feature | Before (Mock) | Now (Production) |
|---------|---------------|------------------|
| **LLM** | Simulated responses | OpenAI GPT-4o-mini via LangChain |
| **RAG** | Static text | ChromaDB with text-embedding-3-small |
| **PDF Processing** | Fake metadata | PyMuPDF extraction + chunking |
| **Agents** | Mock delays | Real LangChain chains (3 agents) |
| *✅ Production Checklist (What's Done)

- [x] OpenAI LLM integration (GPT-4o-mini)
- [x] ChromaDB RAG with embeddings
- [x] PyMuPDF PDF text extraction
- [x] LangChain multi-agent pipeline
- [x] SSE streaming chat
- [x] PowerPoint generation (python-pptx)
- [x] YouTube API search
- [x] Adaptive prompt engineering
- [x] Grade-appropriate chunking

## 🚧 Still TODO for Production

- [ ] Replace in-memory storage with PostgreSQL/MongoDB
- [ ] Add authentication middleware (JWT tokens)
- [ ] Rate limiting (by student_id and IP)
- [ ] Redis for session management
- [ ] Error monitoring (Sentry)
- [ ] Logging (structured JSON logs)
- [ ] Cost tracking (OpenAI API usage per student)
- [ ] Backup/restore for ChromaDB
- [ ] PDF OCR support (for scanned textbooks)
- [ ] Multi-language support (Hindi, Tamil, etc.)

## 🧪 Testing

### Test with curl

```bash
# 1. Login
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"name": "Rahul", "grade": 4, "subject": "Science"}'

# Save student_id from response

# 2. Upload textbook
curl -X POST http://localhost:8000/api/textbook/upload \
  -F "file=@science_grade4.pdf" \
  -F "student_id=YOUR_STUDENT_ID" \
  -F "subject=Science" \
  -F "grade=4"

# 3. Ask a question (SSE stream)
curl "http://localhost:8000/api/chat/stream?query=What%20is%20photosynthesis&student_id=YOUR_STUDENT_ID"
```

### Test PDFs

Use any CBSE textbook PDF. Examples:
- NCERT Science Grade 4
- NCERT English Grade 3
- Any text-based PDF (not scanned images)

## 💰 Cost Estimates

**OpenAI API costs** (approximate):
- Embedding (3-small): $0.00002 per 1K tokens
- Chat (gpt-4o-mini): $0.15 per 1M input tokens
  
**For 100 students**:
- Textbook processing (200 pages each): ~$30
- Monthly chat (10 questions/student): ~$50
- **Total**: ~$80/month

## 🔧 Troubleshooting

### "Module not found: langchain"
```bash
pip install -r requirements.txt
```

### "OPENAI_API_KEY not set"
Add your OpenAI API key to `.env` file:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### ChromaDB errors
```bash
# Delete and recreate
rm -rf chroma_db
# Restart server
```

### PDF extraction returns empty text
- Ensure PDF is text-based (not scanned images)
- Check file size (max 50MB)
- Try a different PDF

## 📚 Dependencies

All dependencies are in `requirements.txt`:
- `fastapi` - Web framework
- `langchain` - LLM orchestration
- `langchain-openai` - OpenAI integration
- `chromadb` - Vector database
- `pymupdf` - PDF text extraction
- `python-pptx` - PowerPoint generation
- `google-api-python-client` - YouTube search

## 🌍 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key |
| `YOUTUBE_API_KEY` | ❌ | - | YouTube Data API key |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | LLM model |
| `EMBEDDING_MODEL` | ❌ | `text-embedding-3-small` | Embedding model |
| `CHROMA_DB_PATH` | ❌ | `./chroma_db` | ChromaDB storage |
| `API_PORT` | ❌ | `8000` | Server port |
Student fills form → POST /api/login → Profile created with UUID
↓
Plays IQ/EQ games → POST /api/profile/games/submit → Scores stored
↓
System calculates: learning_style, confidence_band, motivation
```

### 2. Textbook Upload (RAG Pipeline)
```
Upload PDF → POST /api/textbook/upload
↓
PyMuPDF extracts text
↓
RecursiveCharacterTextSplitter chunks text (grade-appropriate sizes)
↓
OpenAI embeddings (text-embedding-3-small)
↓
ChromaDB stores vectors (collection: student_{id}_{subject})
```

### 3. AI Chat (3-Agent Council)
```
Student asks question → GET /api/chat/stream
↓
Retriever: ChromaDB vector search (top-5 chunks)
↓
Explainer Agent: Creates factual explanation from context
↓
Simplifier Agent: Converts to grade-level + adds Indian examples
↓
Encourager Agent: Wraps with motivation + memory tips
↓
SSE streams each step back to frontend
```
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
