# AI Document Chat System

An AI-powered Document Assistant built using **Retrieval-Augmented Generation (RAG)** that allows users to upload PDF documents, ask questions in natural language, and receive accurate answers with source references.

---

# Objective

The objective of this project is to build an AI-powered document assistant capable of understanding PDF documents and answering user queries using Retrieval-Augmented Generation (RAG). The system retrieves relevant document content, generates contextual answers using a Large Language Model, and provides source references including the filename, page number, and chunk ID.

---

# Tech Stack

| Technology | Purpose |
|------------|---------|
| React (Vite) | Frontend user interface |
| FastAPI | Backend REST APIs |
| PostgreSQL | Stores users, document metadata, and chat history |
| ChromaDB | Stores document embeddings and performs semantic search |
| SentenceTransformer (all-MiniLM-L6-v2) | Generates embeddings for document chunks |
| Groq (Llama 3.1 8B Instant) | Generates answers from retrieved document context |
| JWT Authentication | Secures user authentication |
| PyPDF | Extracts text from uploaded PDF documents |

---

# Assignment Requirements

## Implemented

- ✅ PDF Upload API
- ✅ PDF Text Extraction
- ✅ Document Chunking
- ✅ Embedding Generation
- ✅ ChromaDB Integration
- ✅ Question Answering with Source References
- ✅ Chat History API

## Bonus Features

- ✅ Multi-document Support
- ✅ JWT Authentication

---

# Features

- User Signup & Login
- Secure JWT Authentication
- Upload PDF Documents
- Automatic PDF Text Extraction
- Page-wise Document Chunking
- Local Embedding Generation using SentenceTransformer
- ChromaDB Vector Database Integration
- Retrieval-Augmented Generation (RAG)
- Question Answering with Source References
- Filename, Page Number & Chunk ID Display
- Multi-document Semantic Search
- Chat History Storage
- PostgreSQL Metadata Storage

---

# Architecture

The application follows a **Retrieval-Augmented Generation (RAG)** architecture.

The **React frontend** provides an intuitive user interface where users can register, log in, upload PDF documents, and ask questions.

The frontend communicates with the **FastAPI backend**, which handles authentication, PDF processing, document chunking, embedding generation, semantic retrieval, and communication with the Large Language Model.

When a PDF is uploaded:

- Text is extracted page by page.
- The extracted text is split into smaller chunks.
- SentenceTransformer generates embeddings for each chunk.
- Embeddings are stored in **ChromaDB**.
- Document metadata and chat history are stored in **PostgreSQL**.

When a user asks a question:

- The query is converted into an embedding.
- ChromaDB retrieves the most relevant document chunks.
- Retrieved context is sent to the Groq LLM.
- The generated answer is returned along with:
  - Filename
  - Page Number
  - Chunk ID

All conversations are stored in PostgreSQL for future retrieval.

---

# Application Workflow

```text
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
Retrieve Relevant Chunks from ChromaDB
                      │
                      ▼
 Send Context + Question to Groq LLM
                      │
                      ▼
        Generate Final Answer
                      │
                      ▼
 Display Answer with Filename,
 Page Number & Chunk ID
```

---

# Project Structure

```text
backend/
│
├── app/
│   ├── auth/
│   ├── chat/
│   ├── conversations/
│   ├── documents/
│   ├── rag/
│   ├── search/
│   ├── models/
│   ├── llm/
│   ├── core/
│   ├── migrations.py
│   ├── database.py
│   └── main.py
│
├── uploads/
├── chroma_db/
└── requirements.txt

frontend/
│
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── App.jsx
│   └── main.jsx
│
├── package.json
└── vite.config.js
```

---

# Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file inside the backend folder.

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_chatbot
JWT_SECRET_KEY=your_secret_key
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend URL

```
http://127.0.0.1:8000
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend URL

```
http://localhost:5173
```

---

# Using the Application

1. Register/Login
2. Upload a PDF document
3. Wait for document processing
4. Ask questions related to the uploaded document
5. View answers with:
   - Filename
   - Page Number
   - Chunk ID

---

# API Documentation

The project provides REST APIs for:

- Authentication
- PDF Upload
- Document Listing
- Semantic Search
- Question Answering
- Chat History

Detailed endpoint documentation is available in:

```
API_DOCUMENTATION.md
```

---

# Notes

- Embeddings are generated locally using SentenceTransformer.
- ChromaDB is used for semantic vector search.
- PostgreSQL stores users, documents, metadata, and chat history.
- Groq Llama 3.1 is used for answer generation.
- Source references improve answer transparency and explainability.

---

# Author

**Suraksha Shetty**

AI/ML Intern Assessment Submission

IR Infotech
