from __future__ import annotations

from pathlib import Path
from app.agent.state import AgentState
from app.agent.tool_registry import ToolRegistry
from app.observability.logging import get_logger
from app.observability.tracing import span, get_trace_id
from app.services.storage_service import StorageService
from app.services.qdrant_service import QdrantService
from app.schemas.answer import AskResponse, Citation

logger = get_logger(__name__)


class Orchestrator:
    def __init__(self, storage_service: StorageService, qdrant_service: QdrantService) -> None:
        self.registry = ToolRegistry()
        self.storage = storage_service
        self.qdrant = qdrant_service

    def ingest_document(self, document_id: str, file_path: str | Path, max_retries: int = 2) -> AgentState:
        state = AgentState(document_id=document_id)
        for attempt in range(max_retries + 1):
            state.retries = attempt
            try:
                with span("orchestrator.ingest_document"):
                    state.set_step("parse_pdf")
                    text = self.registry.get("parse_pdf").func(file_path)
                    if not text.strip():
                        raise ValueError("No extractable text found in PDF")
                    text_path = self.storage.save_text(document_id, text)

                    state.set_step("chunk_document")
                    chunks = self.registry.get("chunk_document").func(text)
                    if not chunks:
                        raise ValueError("No chunks produced from parsed document")
                    chunks_path = self.storage.save_chunks(document_id, chunks)

                    state.set_step("embed_chunks")
                    vectors = self.registry.get("embed_chunks").func(chunks)
                    payloads = chunks
                    self.qdrant.upsert_chunks(document_id=document_id, vectors=vectors, payloads=payloads)

                    metadata = self.storage.load_metadata(document_id)
                    metadata.update(
                        {
                            "status": "indexed",
                            "trace_id": get_trace_id(),
                            "text_path": str(text_path),
                            "chunks_path": str(chunks_path),
                            "chunk_count": len(chunks),
                        }
                    )
                    self.storage.save_metadata(document_id, metadata)
                    state.artifacts.update({"text_path": str(text_path), "chunks_path": str(chunks_path)})
                    state.complete()
                    logger.info("Indexed document %s with %s chunks", document_id, len(chunks))
                    return state
            except Exception as exc:
                logger.exception("Ingestion failed for %s on attempt %s", document_id, attempt)
                state.fail(str(exc))
                if attempt >= max_retries:
                    metadata = self.storage.load_metadata(document_id)
                    metadata.update({"status": "failed", "error": str(exc), "trace_id": get_trace_id()})
                    self.storage.save_metadata(document_id, metadata)
                    return state
        return state

    def answer_question(self, document_id: str, question: str, top_k: int = 5) -> AskResponse:
        state = AgentState(document_id=document_id, question=question)
        with span("orchestrator.answer_question"):
            state.set_step("retrieve_context")
            retrieved = self.registry.get("retrieve_context").func(
                document_id=document_id,
                question=question,
                qdrant_service=self.qdrant,
                top_k=top_k,
            )

            state.set_step("generate_grounded_answer")
            answer_text, citations_data = self.registry.get("generate_grounded_answer").func(question, retrieved)
            state.complete()
            return AskResponse(
                document_id=document_id,
                question=question,
                answer=answer_text,
                citations=[Citation(**item) for item in citations_data],
                run_id=state.run_id,
                trace_id=state.trace_id,
                status=state.status,
            )
