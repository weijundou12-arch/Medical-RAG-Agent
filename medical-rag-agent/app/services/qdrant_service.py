from __future__ import annotations

import math
import os
from collections import defaultdict
from typing import Any


class QdrantService:
    """Lightweight in-memory fallback with the same role as a vector store service."""

    def __init__(self) -> None:
        self._collections: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.qdrant_url = os.getenv("QDRANT_URL")

    def upsert_chunks(self, document_id: str, vectors: list[list[float]], payloads: list[dict[str, Any]]) -> None:
        self._collections[document_id] = [
            {"vector": vector, "payload": payload}
            for vector, payload in zip(vectors, payloads, strict=False)
        ]

    def search(self, document_id: str, query_vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        hits: list[dict[str, Any]] = []
        for item in self._collections.get(document_id, []):
            score = self._cosine(query_vector, item["vector"])
            hits.append({"score": score, "payload": item["payload"]})
        hits.sort(key=lambda x: x["score"], reverse=True)
        return hits[:top_k]

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=False))
        norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
        norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
        return dot / (norm_a * norm_b)
