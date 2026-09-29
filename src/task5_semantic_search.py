"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if not query.strip() or top_k <= 0:
        return []

    query_vectors = embed_texts([query])
    if not query_vectors:
        return []
    query_vector = query_vectors[0]

    collection = get_collection()
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    results = []
    if (
        response
        and "ids" in response
        and response["ids"]
        and response["ids"][0]
    ):
        ids = response["ids"][0]
        docs = (
            response["documents"][0]
            if "documents" in response and response["documents"]
            else [""] * len(ids)
        )
        metas = (
            response["metadatas"][0]
            if "metadatas" in response and response["metadatas"]
            else [{}] * len(ids)
        )
        dists = (
            response["distances"][0]
            if "distances" in response and response["distances"]
            else [1.0] * len(ids)
        )

        for item_id, content, meta, distance in zip(ids, docs, metas, dists):
            metadata = dict(meta) if meta else {}
            if "url" not in metadata or metadata["url"] == "":
                metadata["url"] = None
            if "chunk_index" in metadata and not isinstance(
                metadata["chunk_index"], int
            ):
                try:
                    metadata["chunk_index"] = int(metadata["chunk_index"])
                except (ValueError, TypeError):
                    pass

            score = max(0.0, 1.0 - float(distance))
            results.append({
                "id": item_id,
                "content": content,
                "score": score,
                "metadata": metadata,
                "retrieval_method": "dense",
            })

    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)
