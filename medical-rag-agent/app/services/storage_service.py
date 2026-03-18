from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

BASE_DIR = Path(os.getenv("MEDICAL_RAG_DATA_DIR", "/tmp/medical-rag-agent-data"))
UPLOAD_DIR = BASE_DIR / "uploads"
DOC_DIR = BASE_DIR / "documents"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DOC_DIR.mkdir(parents=True, exist_ok=True)


class StorageService:
    def create_document(self, filename: str, file_bytes: bytes) -> tuple[str, Path]:
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        doc_path = UPLOAD_DIR / f"{document_id}.pdf"
        doc_path.write_bytes(file_bytes)
        meta = {
            "document_id": document_id,
            "filename": filename,
            "status": "uploaded",
        }
        self.save_metadata(document_id, meta)
        return document_id, doc_path

    def document_dir(self, document_id: str) -> Path:
        path = DOC_DIR / document_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_metadata(self, document_id: str, metadata: dict[str, Any]) -> None:
        path = self.document_dir(document_id) / "metadata.json"
        path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def load_metadata(self, document_id: str) -> dict[str, Any]:
        path = self.document_dir(document_id) / "metadata.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save_text(self, document_id: str, text: str) -> Path:
        path = self.document_dir(document_id) / "parsed_text.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def save_chunks(self, document_id: str, chunks: list[dict[str, Any]]) -> Path:
        path = self.document_dir(document_id) / "chunks.json"
        path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
        return path

    def load_chunks(self, document_id: str) -> list[dict[str, Any]]:
        path = self.document_dir(document_id) / "chunks.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))
