from __future__ import annotations

from app.tools.embed_chunks import embed_text


def retrieve_context(document_id: str, question: str, qdrant_service, top_k: int = 5) -> list[dict]:
    query_vector = embed_text(question)
    return qdrant_service.search(document_id=document_id, query_vector=query_vector, top_k=top_k)
