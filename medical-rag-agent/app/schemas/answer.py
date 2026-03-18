from pydantic import BaseModel, Field
from typing import Any


class Citation(BaseModel):
    chunk_id: str
    score: float
    excerpt: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AskResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    citations: list[Citation]
    run_id: str
    trace_id: str
    status: str
