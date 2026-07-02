import json

from fastapi import APIRouter, Depends
from app.database import SessionLocal
from app.core.dependencies import get_current_user_id
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


# 1️⃣ Create a conversation
@router.post("/")
def create_conversation(
    title: str = "New Chat",
    user_id: int = Depends(get_current_user_id)
):
    db = SessionLocal()

    convo = Conversation(user_id=user_id, title=title)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    db.close()

    return {
        "conversation_id": convo.id,
        "title": convo.title
    }


# 2️⃣ List conversations (sidebar)
@router.get("/")
def list_conversations(
    user_id: int = Depends(get_current_user_id)
):
    db = SessionLocal()

    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )

    db.close()

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at
        }
        for c in conversations
    ]


# 3️⃣ Get messages of a conversation
@router.get("/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
    user_id: int = Depends(get_current_user_id)
):
    db = SessionLocal()

    messages = (
        db.query(Message)
        .join(Conversation)
        .filter(
            Message.conversation_id == conversation_id,
            Conversation.user_id == user_id
        )
        .order_by(Message.created_at)
        .all()
    )

    db.close()

    return [
        {
            "sender": m.sender,
            "content": m.content,
            "sources": json.loads(m.sources) if m.sources else [],
            "created_at": m.created_at
        }
        for m in messages
    ]
