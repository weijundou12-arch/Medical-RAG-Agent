from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Lock

BASE_DIR = Path(os.getenv("MEDICAL_RAG_DATA_DIR", "/tmp/medical-rag-agent-data"))
CACHE_FILE = BASE_DIR / "cache" / "document_cache.json"
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
_LOCK = Lock()


class CacheService:
    def __init__(self) -> None:
        if not CACHE_FILE.exists():
            CACHE_FILE.write_text("{}", encoding="utf-8")

    def _load(self) -> dict:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        CACHE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def file_sha256(self, file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def get_document_by_hash(self, file_hash: str) -> str | None:
        with _LOCK:
            return self._load().get(file_hash)

    def store_document_hash(self, file_hash: str, document_id: str) -> None:
        with _LOCK:
            data = self._load()
            data[file_hash] = document_id
            self._save(data)
