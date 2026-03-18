from __future__ import annotations

import hashlib
import math
import re

VECTOR_DIM = 128


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def embed_text(text: str) -> list[float]:
    vec = [0.0] * VECTOR_DIM
    for token in _tokenize(text):
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        idx = h % VECTOR_DIM
        vec[idx] += 1.0
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def embed_chunks(chunks: list[dict]) -> list[list[float]]:
    return [embed_text(chunk["text"]) for chunk in chunks]
