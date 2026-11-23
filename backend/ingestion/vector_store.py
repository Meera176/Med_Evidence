import os
import chromadb
from chromadb.config import Settings

_CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_store")
_client = chromadb.PersistentClient(path=_CHROMA_PATH, settings=Settings(anonymized_telemetry=False))


def get_collection(name: str = "medevidence"):
    return _client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def store_chunks(chunks: list[dict], collection_name: str = "medevidence"):
    collection = get_collection(collection_name)
    collection.add(
        ids=[f"{chunks[i]['source']}_{i}" for i in range(len(chunks))],
        embeddings=[c["embedding"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "page": c["page"]} for c in chunks],
    )


def clear_collection(collection_name: str = "medevidence"):
    try:
        _client.delete_collection(collection_name)
    except Exception:
        pass
    _client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})


def search(query_vector: list[float], top_k: int = 5, collection_name: str = "medevidence") -> list[dict]:
    collection = get_collection(collection_name)
    count = collection.count()
    if count == 0:
        return []
    n = min(top_k, count)
    results = collection.query(query_embeddings=[query_vector], n_results=n)
    return [
        {
            "text": doc,
            "source": meta["source"],
            "page": meta["page"],
        }
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]
