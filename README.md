
  # VidyaSetu AI - Educational Chatbot

An AI-powered educational chatbot built for CBSE students (Grades 1-5) featuring profile-based learning games, textbook upload & RAG, and multi-agent AI chat system.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.9+
- Git

### Installation & Running

**1. Install Frontend Dependencies**
```powershell
npm install
# or
pnpm install
```

**2. Install Backend Dependencies**
```powershell
cd backend
pip install -r requirements.txt
cd ..
```

**3. Configure Environment**
```powershell
# Frontend - Create .env file
Copy-Item .env.example .env

# Backend - Create .env file (optional for now)
cd backend
Copy-Item .env.example .env
cd ..
```

**4. Start Both Servers**

Open **two separate terminals**:

**Terminal 1 - Backend:**
```powershell
cd backend
python main.py
```
Backend will run on `http://localhost:8000`

**Terminal 2 - Frontend:**
```powershell
npm run dev
```
Frontend will run on `http://localhost:5173`

### **Alternative: Run Everything at Once**

Windows PowerShell:
```powershell
# Install concurrently
npm install -g concurrently

# Run both servers
concurrently "cd backend && python main.py" "npm run dev"
```

---

## 🎮 Features

### ✅ Implemented

1. **Student Login/Profile**
   - Name, grade (1-5), and subject selection
   - Profile creation with unique student ID
   - XP tracking system

2. **Profile Games**
   - Pattern Recognition game
   - Memory game
   - Game results submitted to backend
   - IQ/EQ score tracking
   - Learning style detection (visual/social/kinesthetic)

3. **Textbook Upload**
   - PDF file upload with drag & drop
   - Progress tracking
   - File validation (50MB limit, PDF only)
   - Backend storage and indexing

4. **AI Chat with SSE Streaming**
   - Real-time streaming responses
   - Multi-agent system simulation (Explainer, Simplifier, Encourager)
   - Agent step visualization
   - Thumbs up/down feedback logging
   - Safety verification badge

5. **Theme Toggle**
   - Light mode with high contrast colors
   - Dark mode (default) with cosmic theme
   - Smooth transitions
   - Persistent theme preference

### 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login` | POST | Student login/registration |
| `/api/profile/{student_id}` | GET | Get student profile |
| `/api/profile/games/submit` | POST | Submit game results |
| `/api/textbook/upload` | POST | Upload textbook PDF |
| `/api/textbook/status/{id}` | GET | Check upload status |
| `/api/chat/stream` | GET | SSE streaming chat |
| `/api/chat/history/{student_id}` | GET | Get chat history |
| `/api/feedback` | POST | Log user feedback |
| `/api/satisfaction/{student_id}` | GET | Get satisfaction chart data |
| `/api/generate/ppt` | POST | Generate PPT summary |
| `/api/video/search` | GET | Search educational videos |

---

## 🎨 Theme Colors

### Dark Mode (Default)
- Background: `#0A0E1A` (Deep space blue)
- Cards: `#111827` (Slate)
- Primary: `#8B5CF6` (Purple)
- Accents: High contrast colors for readability

### Light Mode
- Background: `#FFFFFF` (Pure white)
- Cards: `#F8FAFC` (Light gray)
- Primary: `#8B5CF6` (Purple)
- High contrast text and borders

Toggle theme using the sun/moon button in the top-right corner.

---

## 📁 Project Structure

```
edu-chatbot/
├── backend/
│   ├── main.py              # FastAPI backend
│   ├── requirements.txt     # Python dependencies
│   └── uploads/             # Uploaded textbooks (created on first upload)
├── src/
│   ├── api/
│   │   └── client.ts        # API client for frontend
│   ├── store/
│   │   └── useAppStore.ts   # Zustand state management
│   ├── app/
│   │   ├── App.tsx          # Main app with all screens
│   │   └── components/
│   │       ├── ThemeToggle.tsx
│   │       ├── StarBackground.tsx
│   │       ├── ViddyAvatar.tsx
│   │       └── UIComponents.tsx
│   └── styles/
│       ├── index.css
│       ├── theme.css        # Theme variables
│       └── tailwind.css
├── package.json
├── vite.config.ts
└── README.md
```

---

## 🧪 Testing the Flow

1. **Welcome Screen**: Enter name, select grade & subject → Click "Begin Your Journey!"
2. **Game Screen**: Play pattern & memory games (first option is always correct for demo)
3. **Upload Screen**: Upload a PDF textbook (or click anywhere to simulate upload)
4. **Chat Screen**: Ask questions and see streaming AI responses

---

## 🚧 For Production

The current implementation uses mock data and in-memory storage. For production:

1. **Database**: Replace in-memory storage with PostgreSQL/MongoDB
2. **RAG Pipeline**: Integrate ChromaDB + LangChain for actual textbook Q&A
3. **LLM**: Add OpenAI/Anthropic API or local model (Ollama)
4. **PDF Processing**: Implement actual PDF text extraction
5. **YouTube API**: Add real video search integration
6. **PPT Generation**: Implement python-pptx for presentation creation
7. **Authentication**: Add JWT tokens and secure sessions
8. **File Storage**: Use AWS S3 or cloud storage for uploads
9. **Deployment**: Deploy to Railway (backend) + Vercel (frontend)

---

## 📝 Environment Variables

**Frontend (.env)**
```
VITE_API_URL=http://localhost:8000
```

**Backend (.env)** *(optional for demo)*
```
OPENAI_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
```

---

## 🎯 Hackathon Demo Tips

1. Start both servers before presenting
2. Test the full flow once before demo
3. Have a sample PDF ready to upload
4. Prepare 2-3 interesting questions to ask Viddy
5. Show the theme toggle for visual impact
6. Highlight the agent steps feature (click "See how Viddy thought")
7. Demonstrate feedback buttons

---

## 🛠️ Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS 4
- Zustand (state management)
- Motion (animations)
- Recharts (charts)
- shadcn/ui components

**Backend:**
- FastAPI
- Python 3.9+
- Uvicorn (ASGI server)
- SSE (Server-Sent Events) for streaming

---

## 📄 License

This project was built for the VidyaSetu AI hackathon.

## 🙏 Acknowledgments

- Figma Make for initial UI generation
- shadcn/ui for beautiful components
- FastAPI for the incredible backend framework