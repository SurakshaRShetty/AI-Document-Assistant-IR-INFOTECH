import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.core.dependencies import get_current_user_id
from app.documents.pdf_utils import extract_pages_from_pdf
from app.documents.chunk_utils import chunk_pages
from app.core.local_embeddings import get_embedding
from app.core import vector_store

router = APIRouter()
UPLOAD_DIR = "uploads"


# ---------------------------
# 1️⃣ UPLOAD DOCUMENT
# ---------------------------
@router.post("/documents")
def upload_document(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract text per page and chunk while keeping page numbers
    pages = extract_pages_from_pdf(file_path)
    chunks = chunk_pages(pages)

    if not chunks:
        raise HTTPException(status_code=400, detail="No text found in PDF")

    db: Session = SessionLocal()

    try:
        # Save document
        document = Document(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        document_id = document.id

        # Save chunks (Postgres keeps metadata, ChromaDB keeps the vectors)
        for chunk in chunks:
            embedding = get_embedding(chunk["text"])

            # 🔥 GUARANTEE FLAT VECTOR
            if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                embedding = embedding[0]

            db.add(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk["chunk_index"],
                    page_number=chunk["page_number"],
                    text=chunk["text"],
                )
            )

            vector_store.add_chunk(
                document_id=document_id,
                chunk_index=chunk["chunk_index"],
                embedding=embedding,
                text=chunk["text"],
                metadata={
                    "user_id": user_id,
                    "document_id": document_id,
                    "filename": file.filename,
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                },
            )

        db.commit()

        return {
            "message": "Document uploaded successfully",
            "document_id": document_id,
            "chunks_created": len(chunks)
        }

    finally:
        db.close()


# ---------------------------
# 2️⃣ LIST DOCUMENTS (multi-document support)
# ---------------------------
@router.get("/documents")
def list_documents(
    user_id: int = Depends(get_current_user_id)
):
    db: Session = SessionLocal()

    try:
        documents = (
            db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.uploaded_at.desc())
            .all()
        )

        return [
            {
                "id": d.id,
                "filename": d.filename,
                "uploaded_at": d.uploaded_at,
            }
            for d in documents
        ]

    finally:
        db.close()


# ---------------------------
# 3️⃣ READ DOCUMENT CHUNKS
# ---------------------------
@router.get("/documents/{document_id}/chunks")
def get_document_chunks(
    document_id: int,
    user_id: int = Depends(get_current_user_id)
):
    db: Session = SessionLocal()

    try:
        chunks = (
            db.query(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id
            )
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

        return {
            "document_id": document_id,
            "total_chunks": len(chunks),
            "chunks": [
                {
                    "chunk_index": c.chunk_index,
                    "page_number": c.page_number,
                    "text_preview": c.text[:300]
                }
                for c in chunks
            ]
        }

    finally:
        db.close()
