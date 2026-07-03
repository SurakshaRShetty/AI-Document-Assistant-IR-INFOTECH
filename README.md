# AI Document Chat System
- 
Upload PDF documents, ask questions about them, and get answers grounded in the source
text — with citations (filename, page number, chunk id) and persisted chat history.

Built for the IR Infotech assessment on top of an existing RAG chatbot codebase.
See [architecture.md](./architecture.md) for a diagram of how the pieces fit together,
and [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for the full endpoint reference.

## Stack

| Layer            | Tech                                              |
|-------------------|----------------------------------------------------|
| Backend            | FastAPI (Python)                                   |
| Frontend           | React + Vite                                       |
| Relational DB      | PostgreSQL (users, documents, chat history)        |
| Vector DB          | ChromaDB (persistent, local — chunk embeddings)    |
| Embeddings         | SentenceTransformer `all-MiniLM-L6-v2` (local)     |
| LLM                | Groq (`llama-3.1-8b-instant`)                      |
| Auth               | JWT access + refresh tokens                        |

## Assignment Features

- PDF Upload API
- PDF Text Extraction
- Document Chunking
- SentenceTransformer Embeddings
- ChromaDB Vector Database
- Retrieval-Augmented Generation (RAG)
- Question Answering with Source References
- Chat History API
- Multi-document Support
- JWT Authentication

  
## Features

- PDF upload with text extraction and page-aware chunking
- Local embedding generation (no external embedding API required)
- ChromaDB vector storage + semantic search
- Question answering with source references (filename, page number, chunk id)
- Chat history (conversations + messages), auto-created per Q&A turn or reused via `conversation_id`
- Multi-document support (`/rag/answer` searches across all of a user's documents)
- JWT authentication (signup/login/refresh/logout)

## Prerequisites

- Python 3.11+ (tested on 3.13)
- Node.js 18+
- PostgreSQL running locally (or reachable via `DATABASE_URL`)

## 1. Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create/edit `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/rag_chatbot
JWT_SECRET_KEY=change-me-in-production
```

Create the `rag_chatbot` database if it doesn't already exist (any Postgres client works):

```sql
CREATE DATABASE rag_chatbot;
```

Tables and column migrations run **automatically** on backend startup (see
`app/migrations.py`, invoked from `app/main.py`'s startup event) — no manual migration
step is required for a fresh database.

**If you're upgrading an existing database** that already has chunks with embeddings
stored in the old Postgres `ARRAY(Float)` column, run the one-time backfill to copy them
into ChromaDB so previously-uploaded documents remain searchable:

```bash
python -m app.backfill_chroma
```

(Safe to re-run — it skips chunks already present in ChromaDB.)

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

ChromaDB persists to `backend/chroma_db/` (created automatically, gitignored-recommended).

## 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173 (Vite will pick another port automatically if 5173 is busy —
  check the terminal output)

The frontend expects the backend at `http://127.0.0.1:8000` (see `frontend/src/api/axios.js`).

## 3. Using the app

1. Sign up with a Gmail address, then log in.
2. Upload a PDF on the Upload page.
3. Ask questions on the Chat page — answers include a **Sources** list showing the
   originating filename, page number, and chunk id for each citation used.

## Running both together (quick reference)

```bash
# Terminal 1 — backend
cd backend
venv\Scripts\activate        # or: source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

## Project structure

```
backend/
  app/
    auth/            # signup, login, refresh, logout
    documents/        # PDF upload, page-aware text extraction, chunking
    chat/              # single-document Q&A (/chat/ask)
    rag/                # multi-document Q&A (/rag/answer)
    search/            # raw semantic search (/search/)
    conversations/    # chat history API
    core/
      local_embeddings.py   # SentenceTransformer embeddings
      vector_store.py       # ChromaDB client wrapper
      retrieval.py           # shared semantic search over ChromaDB
      qa_service.py          # shared answer + source-citation + history logic
      dependencies.py       # JWT auth dependency
      security.py             # password hashing, token creation
    llm/groq_client.py    # Groq LLM call
    models/                    # SQLAlchemy models
    migrations.py            # additive, idempotent column migrations
    backfill_chroma.py     # one-time Postgres -> ChromaDB embedding backfill
  uploads/                     # uploaded PDF files
  chroma_db/                  # ChromaDB persistent storage (created at runtime)
frontend/
  src/
    pages/                      # Login, Signup, Upload, Chat
    components/               # Header, PrivateRoute
    api/axios.js               # API client with JWT interceptor
```
## Tech Stack

| Technology | Purpose |
|------------|---------|
| React (Vite) | Builds the frontend user interface |
| FastAPI | Develops REST APIs and backend services |
| PostgreSQL | Stores users, document metadata, and chat history |
| ChromaDB | Stores document embeddings and performs semantic search |
| SentenceTransformer (all-MiniLM-L6-v2) | Generates vector embeddings for document chunks |
| Groq (Llama 3.1 8B Instant) | Generates answers from retrieved document context |
| JWT Authentication | Secures user authentication and API access |
| PyPDF | Extracts text from uploaded PDF documents |

---

## Architecture

The application follows a **Retrieval-Augmented Generation (RAG)** architecture.

The **React frontend** provides the user interface where users can register, log in, upload PDF documents, and ask questions.

The **FastAPI backend** handles authentication, PDF processing, document chunking, embedding generation, semantic retrieval, and communication with the Large Language Model.

When a PDF is uploaded, the backend extracts the text page by page, splits it into smaller chunks, generates embeddings using **SentenceTransformer**, and stores those embeddings in **ChromaDB**. Document metadata, user information, and chat history are stored in **PostgreSQL**.

When a user submits a question, the backend generates an embedding for the query and performs semantic search in **ChromaDB** to retrieve the most relevant document chunks. These retrieved chunks are then provided to the **Groq LLM**, which generates the final answer. The response is returned to the frontend along with **source references** including the filename, page number, and chunk ID. Each conversation is also stored in PostgreSQL for chat history.

---
## Application Workflow 
                USER
                  │
                  ▼
          Login / Signup
                  │
                  ▼
          Upload PDF Document
                  │
                  ▼
        Extract Text from PDF
                  │
                  ▼
      Split into Smaller Chunks
                  │
                  ▼
 Generate Embeddings (SentenceTransformer)
                  │
                  ▼
      Store Embeddings in ChromaDB
                  │
                  ▼
 Store Metadata & Chat History
      in PostgreSQL Database
                  │
                  ▼
         User Asks Question
                  │
                  ▼
 Generate Query Embedding
                  │
                  ▼
 Retrieve Relevant Chunks
      from ChromaDB
                  │
                  ▼
  Send Context + Question to Groq LLM
                  │
                  ▼
      Generate Final Answer
                  │
                  ▼
 Display Answer with
 Filename + Page Number + Chunk ID

 
## Notes

- Embeddings run locally via SentenceTransformer — no external embedding API key needed.
- The `document_chunks.embedding` Postgres column is kept for backward compatibility but
  is no longer written to; vectors live in ChromaDB going forward.
