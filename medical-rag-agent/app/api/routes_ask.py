from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ask import AskRequest
from app.schemas.answer import AskResponse
from app.services.dependencies import get_orchestrator, get_storage_service
from app.agent.orchestrator import Orchestrator
from app.services.storage_service import StorageService
from app.observability.tracing import new_trace_id

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("", response_model=AskResponse)
def ask_question(
    payload: AskRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
    storage_service: StorageService = Depends(get_storage_service),
) -> AskResponse:
    new_trace_id()
    metadata = storage_service.load_metadata(payload.document_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    if metadata.get("status") != "indexed":
        raise HTTPException(status_code=409, detail=f"Document is not ready for QA. status={metadata.get('status')}")
    return orchestrator.answer_question(payload.document_id, payload.question, payload.top_k)
