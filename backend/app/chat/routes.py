from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencies import get_current_user_id
from app.database import SessionLocal
from app.core.qa_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    document_id: int
    question: str
    conversation_id: Optional[int] = None


@router.post("/ask")
def ask_question(
    payload: ChatRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Single-document question answering with source references (filename, page, chunk id)."""
    db = SessionLocal()
    try:
        return answer_question(
            db=db,
            user_id=user_id,
            query=payload.question,
            top_k=5,
            document_id=payload.document_id,
            conversation_id=payload.conversation_id,
        )
    finally:
        db.close()
