from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.database import SessionLocal
from app.core.dependencies import get_current_user_id
from app.core.qa_service import answer_question

router = APIRouter(prefix="/rag", tags=["RAG"])


# ✅ REQUEST SCHEMA
class RagRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None
    top_k: int = 7


@router.post("/answer")
def rag_answer(
    payload: RagRequest,                # ✅ JSON BODY
    user_id: int = Depends(get_current_user_id)
):
    """Multi-document question answering with source references (filename, page, chunk id)."""
    db = SessionLocal()
    try:
        return answer_question(
            db=db,
            user_id=user_id,
            query=payload.query,
            top_k=payload.top_k,
            conversation_id=payload.conversation_id,
        )
    finally:
        db.close()
