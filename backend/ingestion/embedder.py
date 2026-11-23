from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(chunks: list[dict]) -> list[dict]:
    texts = [c["text"] for c in chunks]
    vectors = _model.encode(texts, show_progress_bar=True)
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector.tolist()
    return chunks


def embed_query(query: str) -> list[float]:
    return _model.encode(query).tolist()
