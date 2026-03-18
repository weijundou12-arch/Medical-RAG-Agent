from __future__ import annotations

import re
from typing import Any

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with", "is", "are", "was", "were",
    "what", "which", "how", "when", "where", "why", "does", "do", "did", "can", "could", "should",
}


def _keywords(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z0-9]+", text.lower()) if t not in STOPWORDS and len(t) > 2}


def generate_grounded_answer(question: str, retrieved: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    if not retrieved:
        return (
            "I could not find supporting evidence in the indexed PDF for this question.",
            [],
        )

    question_terms = _keywords(question)
    citations: list[dict[str, Any]] = []
    ranked_sentences: list[tuple[float, str, dict[str, Any]]] = []

    for hit in retrieved:
        payload = hit["payload"]
        text = payload["text"]
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            sentence = sentence.strip()
            if not sentence:
                continue
            overlap = len(question_terms.intersection(_keywords(sentence)))
            ranked_sentences.append((hit["score"] + overlap * 0.05, sentence, payload))
        citations.append(
            {
                "chunk_id": payload["chunk_id"],
                "score": round(float(hit["score"]), 4),
                "excerpt": text[:280],
                "metadata": payload.get("metadata", {}),
            }
        )

    ranked_sentences.sort(key=lambda x: x[0], reverse=True)
    best_sentences = [sentence for _, sentence, _ in ranked_sentences[:3]]
    answer = " ".join(best_sentences).strip()
    if not answer:
        answer = "Relevant sections were retrieved, but no concise sentence-level answer could be formed from the PDF."
    return answer, citations[:5]
