import os
from functools import lru_cache

import chromadb

CHROMA_DIR = os.getenv("CHROMA_DIR", os.path.join(os.getcwd(), "chroma_db"))


@lru_cache(maxsize=1)
def get_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


@lru_cache(maxsize=1)
def get_collection():
    client = get_client()
    return client.get_or_create_collection(
        name="document_chunks",
        metadata={"hnsw:space": "cosine"},
    )


def chunk_id(document_id: int, chunk_index: int) -> str:
    return f"{document_id}_{chunk_index}"


def add_chunk(document_id: int, chunk_index: int, embedding: list, text: str, metadata: dict):
    collection = get_collection()
    collection.add(
        ids=[chunk_id(document_id, chunk_index)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata],
    )


def delete_document_chunks(document_id: int):
    collection = get_collection()
    collection.delete(where={"document_id": document_id})


def query(embedding: list, top_k: int, where: dict):
    collection = get_collection()
    return collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where,
    )
