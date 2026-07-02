"""
One-time backfill: copies embeddings already stored in the Postgres
document_chunks.embedding column (from before the ChromaDB migration) into
ChromaDB, so documents uploaded before this change remain searchable.

Safe to re-run: existing IDs are skipped.
"""
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text

from app.database import SessionLocal, engine, Base
from app.models import *  # noqa: F401,F403
from app.migrations import run_migrations
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.core import vector_store


def backfill():
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)

    # Pre-existing chunks (before page tracking existed) don't have a real
    # page number. Default to 1 rather than leaving it null.
    with engine.begin() as conn:
        conn.execute(text(
            "UPDATE document_chunks SET page_number = 1 WHERE page_number IS NULL"
        ))

    db = SessionLocal()
    collection = vector_store.get_collection()

    try:
        existing_ids = set(collection.get()["ids"])

        rows = (
            db.query(DocumentChunk, Document)
            .join(Document, Document.id == DocumentChunk.document_id)
            .filter(DocumentChunk.embedding.isnot(None))
            .all()
        )

        migrated = 0
        skipped_no_embedding = 0

        for chunk, document in rows:
            cid = vector_store.chunk_id(chunk.document_id, chunk.chunk_index)
            if cid in existing_ids:
                continue

            embedding = chunk.embedding
            if not embedding:
                skipped_no_embedding += 1
                continue

            page_number = chunk.page_number or 1

            vector_store.add_chunk(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                embedding=embedding,
                text=chunk.text or "",
                metadata={
                    "user_id": document.user_id,
                    "document_id": chunk.document_id,
                    "filename": document.filename,
                    "page_number": page_number,
                    "chunk_index": chunk.chunk_index,
                },
            )
            migrated += 1

        print(f"Backfilled {migrated} chunk(s) into ChromaDB "
              f"({skipped_no_embedding} skipped, no embedding).")

    finally:
        db.close()


if __name__ == "__main__":
    backfill()
