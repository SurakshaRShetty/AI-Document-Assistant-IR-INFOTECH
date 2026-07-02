# app/embeddings.py

from sentence_transformers import SentenceTransformer

# Load model ONCE
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    """
    Returns a 1D embedding vector of size 384
    """
    embedding = model.encode(text)

    # VERY IMPORTANT: flatten to 1D list
    return embedding.tolist()
