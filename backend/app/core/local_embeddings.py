from sentence_transformers import SentenceTransformer
from functools import lru_cache

# Lazy-load model (prevents app startup crash)
@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str):
    model = get_model()
    embedding = model.encode(text)
    return embedding.tolist()
