from functools import lru_cache
from app.services.storage_service import StorageService
from app.services.qdrant_service import QdrantService
from app.services.cache_service import CacheService
from app.agent.orchestrator import Orchestrator


@lru_cache
def get_storage_service() -> StorageService:
    return StorageService()


@lru_cache
def get_qdrant_service() -> QdrantService:
    return QdrantService()


@lru_cache
def get_cache_service() -> CacheService:
    return CacheService()


@lru_cache
def get_orchestrator() -> Orchestrator:
    return Orchestrator(storage_service=get_storage_service(), qdrant_service=get_qdrant_service())
