from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user_id
from app.core.retrieval import search_chunks

router = APIRouter()


@router.post("/search/")
def semantic_search(
    query: str,
    top_k: int = 3,
    user_id: int = Depends(get_current_user_id)
):
    results = search_chunks(user_id=user_id, query_text=query, top_k=top_k)

    return {
        "query": query,
        "results": [
            {
                "score": r["score"],
                "text": r["text"],
                "filename": r["filename"],
                "page_number": r["page_number"],
                "chunk_id": r["chunk_id"],
                "document_id": r["document_id"],
            }
            for r in results
        ],
    }
