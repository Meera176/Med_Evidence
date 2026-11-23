from ingestion.embedder import embed_query
from ingestion.vector_store import search


def hybrid_search(query: str, top_k: int = 5) -> list[dict]:
    query_vector = embed_query(query)
    results = search(query_vector, top_k=top_k * 3)  # fetch more, then keyword filter

    keywords = query.lower().split()
    filtered = [
        c for c in results
        if any(kw in c["text"].lower() for kw in keywords)
    ]

    # fall back to full results if no keyword matches
    return (filtered if filtered else results)[:top_k]
