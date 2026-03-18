from __future__ import annotations

import re
from typing import Any


def chunk_document(text: str, chunk_size: int = 120, overlap: int = 30) -> list[dict[str, Any]]:
    words = text.split()
    chunks: list[dict[str, Any]] = []
    start = 0
    index = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_text = " ".join(words[start:end]).strip()
        if chunk_text:
            chunks.append(
                {
                    "chunk_id": f"chunk_{index:04d}",
                    "text": chunk_text,
                    "metadata": {
                        "start_word": start,
                        "end_word": end,
                        "sentence_count": max(1, len(re.split(r"[.!?]+", chunk_text)) - 1),
                    },
                }
            )
            index += 1
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks
