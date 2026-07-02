from typing import Optional

from app.core.local_embeddings import get_embedding
from app.core import vector_store


def _flatten(embedding):
    if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
        return embedding[0]
    return embedding


def search_chunks(
    user_id: int,
    query_text: str,
    top_k: int = 5,
    document_id: Optional[int] = None,
):
    """
    Semantic search over ChromaDB, scoped to a user (and optionally a single document).
    Returns a list of dicts with text, score and source reference info
    (filename, page_number, chunk_id).
    """
    embedding = _flatten(get_embedding(query_text))

    if document_id is None:
        where = {"user_id": user_id}
    else:
        where = {"$and": [{"user_id": user_id}, {"document_id": document_id}]}

    results = vector_store.query(embedding, top_k, where)

    ids = (results.get("ids") or [[]])[0]
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    matches = []
    for chunk_id, text, meta, distance in zip(ids, documents, metadatas, distances):
        matches.append({
            "chunk_id": chunk_id,
            "text": text,
            "score": 1 - distance,
            "document_id": meta.get("document_id"),
            "filename": meta.get("filename"),
            "page_number": meta.get("page_number"),
            "chunk_index": meta.get("chunk_index"),
        })

    return matches
