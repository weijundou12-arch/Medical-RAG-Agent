from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def minimal_pdf_bytes() -> bytes:
    return b"%PDF-1.1\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 144]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n4 0 obj<</Length 90>>stream\nBT /F1 12 Tf 20 100 Td (Diabetes management includes diet exercise and glucose monitoring.) Tj ET\nendstream\nendobj\n5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000062 00000 n \n0000000117 00000 n \n0000000243 00000 n \n0000000383 00000 n \ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n453\n%%EOF"


def test_upload_and_ask_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("MEDICAL_RAG_DATA_DIR", str(tmp_path))
    files = {"file": ("demo.pdf", minimal_pdf_bytes(), "application/pdf")}
    upload_resp = client.post("/upload", files=files)
    assert upload_resp.status_code == 200
    document_id = upload_resp.json()["document_id"]

    ask_resp = client.post(
        "/ask",
        json={
            "document_id": document_id,
            "question": "What is included in diabetes management?",
            "top_k": 3,
        },
    )
    assert ask_resp.status_code == 200
    data = ask_resp.json()
    assert data["document_id"] == document_id
    assert data["citations"]


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
