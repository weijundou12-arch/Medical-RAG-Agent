from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from app.tools.parse_pdf import parse_pdf
from app.tools.chunk_document import chunk_document
from app.tools.embed_chunks import embed_chunks
from app.tools.retrieve_context import retrieve_context
from app.tools.generate_grounded_answer import generate_grounded_answer


@dataclass
class ToolContract:
    name: str
    goal: str
    must_not_do: str
    func: Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self.tools = {
            "parse_pdf": ToolContract(
                name="parse_pdf",
                goal="Extract text from uploaded PDF",
                must_not_do="Must not modify original file or fabricate content",
                func=parse_pdf,
            ),
            "chunk_document": ToolContract(
                name="chunk_document",
                goal="Split document text into retrieval chunks",
                must_not_do="Must not drop all text silently",
                func=chunk_document,
            ),
            "embed_chunks": ToolContract(
                name="embed_chunks",
                goal="Create deterministic embeddings for chunks",
                must_not_do="Must not call remote embedding APIs in offline mode",
                func=embed_chunks,
            ),
            "retrieve_context": ToolContract(
                name="retrieve_context",
                goal="Retrieve top relevant chunks for a question",
                must_not_do="Must not retrieve from a different document",
                func=retrieve_context,
            ),
            "generate_grounded_answer": ToolContract(
                name="generate_grounded_answer",
                goal="Generate an answer anchored to retrieved evidence",
                must_not_do="Must not answer beyond available evidence",
                func=generate_grounded_answer,
            ),
        }

    def get(self, name: str) -> ToolContract:
        return self.tools[name]
