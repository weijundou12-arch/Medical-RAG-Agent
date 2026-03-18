from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid
from app.observability.tracing import get_trace_id


@dataclass
class AgentState:
    document_id: str | None = None
    question: str | None = None
    run_id: str = field(default_factory=lambda: f"run_{uuid.uuid4().hex[:8]}")
    trace_id: str = field(default_factory=get_trace_id)
    status: str = "pending"
    step: str = "created"
    retries: int = 0
    last_error: str | None = None
    artifacts: dict[str, Any] = field(default_factory=dict)

    def set_step(self, step: str, status: str = "running") -> None:
        self.step = step
        self.status = status

    def fail(self, error: str) -> None:
        self.last_error = error
        self.status = "failed"

    def complete(self) -> None:
        self.status = "completed"
