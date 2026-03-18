from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from app.schemas.upload import UploadResponse
from app.observability.tracing import new_trace_id, get_trace_id
from app.observability.logging import get_logger
from app.services.dependencies import get_cache_service, get_storage_service, get_orchestrator
from app.services.cache_service import CacheService
from app.services.storage_service import StorageService
from app.agent.orchestrator import Orchestrator

router = APIRouter(prefix="/upload", tags=["upload"])
logger = get_logger(__name__)


@router.post("", response_model=UploadResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    cache_service: CacheService = Depends(get_cache_service),
    storage_service: StorageService = Depends(get_storage_service),
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> UploadResponse:
    new_trace_id()
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    file_hash = cache_service.file_sha256(file_bytes)
    cached_document_id = cache_service.get_document_by_hash(file_hash)
    if cached_document_id:
        logger.info("Cache hit for %s -> %s", file.filename, cached_document_id)
        return UploadResponse(
            document_id=cached_document_id,
            filename=file.filename,
            status="cached",
            message="Existing indexed document reused from cache",
            trace_id=get_trace_id(),
        )

    document_id, file_path = storage_service.create_document(file.filename, file_bytes)
    cache_service.store_document_hash(file_hash, document_id)
    background_tasks.add_task(orchestrator.ingest_document, document_id, str(file_path))
    logger.info("Accepted upload %s as %s", file.filename, document_id)
    return UploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="accepted",
        message="Upload accepted and background ingestion started",
        trace_id=get_trace_id(),
    )
