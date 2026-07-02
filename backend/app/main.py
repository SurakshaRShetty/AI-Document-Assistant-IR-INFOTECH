from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.documents.routes import router as documents_router
from app.chat.routes import router as chat_router
from app.search.routes import router as search_router
from app.rag.routes import router as rag_router
from app.conversations.routes import router as conversation_router

from app.core.dependencies import get_current_user_id
from app.database import Base, engine
from app.models import *
from app.migrations import run_migrations

app = FastAPI(title="RAG Chatbot Backend")


@app.on_event("startup")
def run_startup_tasks():
    # Creates any missing tables, then applies additive column migrations.
    # Safe to run on every boot.
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)

app.add_middleware(
    CORSMiddleware,
    # Vite picks 5173 by default and falls back to 5174+ if that port is busy.
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ INCLUDE ROUTERS (NO PREFIX HERE)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(search_router)
app.include_router(rag_router)
app.include_router(conversation_router)

@app.get("/")
def root():
    return {"status": "RAG backend running"}

@app.get("/me")
def get_me(user_id: int = Depends(get_current_user_id)):
    return {"message": "You are authenticated", "user_id": user_id}
