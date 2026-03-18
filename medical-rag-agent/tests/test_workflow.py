from pathlib import Path
from app.agent.orchestrator import Orchestrator
from app.services.storage_service import StorageService
from app.services.qdrant_service import QdrantService


def minimal_pdf_bytes() -> bytes:
    return b"%PDF-1.1\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 144]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n4 0 obj<</Length 82>>stream\nBT /F1 12 Tf 20 100 Td (Hypertension treatment includes lifestyle change and medication.) Tj ET\nendstream\nendobj\n5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000062 00000 n \n0000000117 00000 n \n0000000243 00000 n \n0000000375 00000 n \ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n445\n%%EOF"


def test_orchestrator_ingest_and_answer(tmp_path, monkeypatch):
    monkeypatch.setenv("MEDICAL_RAG_DATA_DIR", str(tmp_path))
    storage = StorageService()
    qdrant = QdrantService()
    orchestrator = Orchestrator(storage_service=storage, qdrant_service=qdrant)

    doc_id, path = storage.create_document("sample.pdf", minimal_pdf_bytes())
    state = orchestrator.ingest_document(doc_id, str(path))
    assert state.status == "completed"

    response = orchestrator.answer_question(doc_id, "What does the document say about hypertension treatment?")
    assert response.status == "completed"
    assert response.citations
