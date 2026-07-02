# API Documentation

Base URL (local dev): `http://127.0.0.1:8000`

All endpoints except `/auth/signup` and `/auth/login` require a JWT bearer token:

```
Authorization: Bearer <access_token>
```

Interactive Swagger docs are also available at `http://127.0.0.1:8000/docs` while the
backend is running.

---

## Auth

### POST `/auth/signup`
Register a new user. Only `@gmail.com` addresses are accepted (existing behavior).

**Body**
```json
{ "name": "Jane Doe", "email": "jane@gmail.com", "password": "secret123" }
```

**Response `200`**
```json
{ "message": "User registered successfully", "user_id": 1 }
```

### POST `/auth/login`
`application/x-www-form-urlencoded` (OAuth2 password flow): `username` (email) + `password`.

**Response `200`**
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

### POST `/auth/refresh`
Body/query: `refresh_token`. Rotates and returns a new access + refresh token pair.

### POST `/auth/logout`
Body/query: `refresh_token`. Revokes the given refresh token.

---

## Documents

### POST `/documents`
Upload a PDF. Extracts text per page, chunks it (1000 chars, 200 overlap, chunk
boundaries never cross a page), embeds each chunk locally (SentenceTransformer), and
stores:
- chunk text + page number in PostgreSQL (`document_chunks`)
- chunk embedding + metadata in ChromaDB

**Form-data**: `file` (PDF)

**Response `200`**
```json
{ "message": "Document uploaded successfully", "document_id": 26, "chunks_created": 17 }
```

### GET `/documents`
List all documents uploaded by the current user (multi-document support).

**Response `200`**
```json
[
  { "id": 26, "filename": "AI Fundamentals Glossary.pdf", "uploaded_at": "2026-07-02T05:16:57.938757" }
]
```

### GET `/documents/{document_id}/chunks`
Debug/inspection endpoint: lists a document's chunks with page numbers and a text preview.

**Response `200`**
```json
{
  "document_id": 26,
  "total_chunks": 17,
  "chunks": [
    { "chunk_index": 0, "page_number": 1, "text_preview": "..." }
  ]
}
```

---

## Question Answering

Both endpoints below share the same retrieval + answer-generation + chat-history logic
(`app/core/qa_service.py`). Matches below a similarity score of `0.15` are discarded; if
nothing passes, the answer is `"No relevant information found."` and `sources` is empty.

### POST `/rag/answer`
Multi-document Q&A — searches across **all** of the current user's uploaded documents.

**Body**
```json
{ "query": "What is machine learning?", "conversation_id": null, "top_k": 7 }
```
- `conversation_id` (optional): continue an existing conversation. Omit/`null` to start a new one.
- `top_k` (optional, default `7`): number of chunks to retrieve.

**Response `200`**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence...",
  "sources": [
    { "filename": "AI Fundamentals Glossary.pdf", "page_number": 1, "chunk_id": "26_1", "document_id": 26, "score": 0.6281 }
  ],
  "conversation_id": 1,
  "chunks_used": 7
}
```

### POST `/chat/ask`
Single-document Q&A — scoped to one `document_id`.

**Body**
```json
{ "document_id": 26, "question": "What is deep learning?", "conversation_id": null }
```

**Response `200`**: same shape as `/rag/answer`.

---

## Semantic Search

### POST `/search/?query=...&top_k=3`
Raw semantic search across the user's chunks (no LLM call) — useful for debugging retrieval.

**Response `200`**
```json
{
  "query": "cyber security",
  "results": [
    {
      "score": 0.725,
      "text": "...",
      "filename": "CYBER SECURITY (R18A0521).pdf",
      "page_number": 5,
      "chunk_id": "27_7",
      "document_id": 27
    }
  ]
}
```

---

## Chat History

### POST `/conversations/?title=...`
Create a new empty conversation. (Usually not needed directly — `/rag/answer` and
`/chat/ask` auto-create a conversation when `conversation_id` is omitted.)

**Response `200`**
```json
{ "conversation_id": 1, "title": "New Chat" }
```

### GET `/conversations/`
List the current user's conversations, most recent first.

**Response `200`**
```json
[ { "id": 1, "title": "What is machine learning?", "created_at": "2026-07-02T10:47:16Z" } ]
```

### GET `/conversations/{conversation_id}/messages`
Full message history for a conversation, oldest first. Assistant messages include the
`sources` used to answer.

**Response `200`**
```json
[
  { "sender": "user", "content": "What is machine learning?", "sources": [], "created_at": "..." },
  { "sender": "assistant", "content": "...", "sources": [ { "filename": "...", "page_number": 1, "chunk_id": "26_1", "document_id": 26, "score": 0.63 } ], "created_at": "..." }
]
```

---

## Misc

### GET `/`
Health check. `{ "status": "RAG backend running" }`

### GET `/me`
Returns the authenticated user id. `{ "message": "You are authenticated", "user_id": 1 }`
