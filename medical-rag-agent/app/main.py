from fastapi import FastAPI
from app.api.routes_upload import router as upload_router
from app.api.routes_ask import router as ask_router
from app.api.routes_health import router as health_router
from app.observability.logging import configure_logging

configure_logging()

app = FastAPI(title="Medical RAG Agent", version="0.1.0")
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(ask_router)
