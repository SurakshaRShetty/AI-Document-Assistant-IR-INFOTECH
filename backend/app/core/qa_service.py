import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.core.retrieval import search_chunks
from app.llm.groq_client import generate_answer

MIN_SCORE = 0.15


def answer_question(
    db: Session,
    user_id: int,
    query: str,
    top_k: int = 5,
    document_id: Optional[int] = None,
    conversation_id: Optional[int] = None,
):
    """
    Shared by /rag/answer (multi-document) and /chat/ask (single document):
    retrieves relevant chunks from ChromaDB, generates an answer with source
    references (filename, page number, chunk id), and logs both turns to
    chat history.
    """
    matches = search_chunks(user_id, query, top_k=top_k, document_id=document_id)
    matches = [m for m in matches if m["score"] >= MIN_SCORE]

    if not matches:
        answer = "No relevant information found."
        sources = []
    else:
        context = "\n\n".join(
            f"[Source: {m['filename']}, page {m['page_number']}]\n{m['text']}"
            for m in matches
        )
        answer = generate_answer(query, context)
        sources = [
            {
                "filename": m["filename"],
                "page_number": m["page_number"],
                "chunk_id": m["chunk_id"],
                "document_id": m["document_id"],
                "score": round(m["score"], 4),
            }
            for m in matches
        ]

    conversation = None
    if conversation_id is not None:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )

    if conversation is None:
        conversation = Conversation(user_id=user_id, title=query[:60])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    db.add(Message(conversation_id=conversation.id, sender="user", content=query))
    db.add(Message(
        conversation_id=conversation.id,
        sender="assistant",
        content=answer,
        sources=json.dumps(sources),
    ))
    db.commit()

    return {
        "answer": answer,
        "sources": sources,
        "conversation_id": conversation.id,
        "chunks_used": len(matches),
    }
