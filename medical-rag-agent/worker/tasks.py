from worker.celery_app import celery_app
from app.services.dependencies import get_orchestrator


@celery_app.task(name="medical_rag_agent.ingest_document")
def ingest_document_task(document_id: str, file_path: str):
    orchestrator = get_orchestrator()
    state = orchestrator.ingest_document(document_id=document_id, file_path=file_path)
    return {
        "document_id": document_id,
        "run_id": state.run_id,
        "status": state.status,
        "last_error": state.last_error,
    }
