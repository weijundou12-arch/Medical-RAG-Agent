# Medical RAG Agent

**Medical RAG Agent** is a FastAPI-based single-agent retrieval-augmented generation service for medical PDFs.
It supports PDF upload, background ingestion, chunking, deterministic embeddings, retrieval, evidence-grounded answering, structured API schemas, logs, traces, and Dockerized deployment.

## Features

- Upload medical PDFs through a FastAPI endpoint
- Parse and chunk document text in a background workflow
- Reuse cached documents by file hash
- Store indexed chunks in a vector-service abstraction (`QdrantService`)
- Ask evidence-grounded questions against a specific document
- Return structured answers with citations and trace IDs
- Track workflow state, retries, failures, and artifacts
- Containerized with Docker and `docker-compose`
- Includes tests with `pytest`

## Project Structure

```text
medical-rag-agent/
├─ app/
│  ├─ main.py
│  ├─ schemas/
│  │  ├─ upload.py
│  │  ├─ ask.py
│  │  └─ answer.py
│  ├─ api/
│  │  ├─ routes_upload.py
│  │  ├─ routes_ask.py
│  │  └─ routes_health.py
│  ├─ agent/
│  │  ├─ orchestrator.py
│  │  ├─ state.py
│  │  └─ tool_registry.py
│  ├─ tools/
│  │  ├─ parse_pdf.py
│  │  ├─ chunk_document.py
│  │  ├─ embed_chunks.py
│  │  ├─ retrieve_context.py
│  │  └─ generate_grounded_answer.py
│  ├─ services/
│  │  ├─ cache_service.py
│  │  ├─ dependencies.py
│  │  ├─ qdrant_service.py
│  │  └─ storage_service.py
│  └─ observability/
│     ├─ logging.py
│     └─ tracing.py
├─ worker/
│  ├─ celery_app.py
│  └─ tasks.py
├─ tests/
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

## How It Works

### 1. Upload
`POST /upload` accepts a PDF file, computes its hash, checks cache reuse, persists the upload, and starts background ingestion.

### 2. Background Ingestion
The single-agent orchestrator runs a linear workflow:
1. `parse_pdf`
2. `chunk_document`
3. `embed_chunks`
4. `qdrant_service.upsert_chunks`

Each step updates explicit agent state and writes artifacts to the document workspace.

### 3. Ask
`POST /ask` retrieves the indexed chunks for the document, ranks them with deterministic embeddings, and generates an answer grounded in retrieved evidence.

## API

### Health
```bash
curl http://localhost:8000/health
```

### Upload
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@sample.pdf"
```

### Ask
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_xxxxxxxxxxxx",
    "question": "What does the paper say about hypertension treatment?",
    "top_k": 5
  }'
```

## Local Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
pytest -q
```

## Docker

```bash
docker compose up --build
```

This starts:
- FastAPI API service
- Celery worker
- Redis
- Qdrant

## Design Notes

- **Single-agent orchestration**: one orchestrator manages document ingestion and QA
- **Explicit state**: run status, step, retry count, last error, artifacts
- **Failure recovery**: ingestion retries up to 2 times before marking failed
- **OpenClaw-style tools**: each tool has a clear goal and failure boundary in the registry
- **Evidence grounding**: answers are generated only from retrieved chunks and returned with citations

## Limitations

- The default embedding path is deterministic and local, not model-based
- `QdrantService` is implemented as a lightweight in-memory fallback abstraction for easy local runs
- Answer generation is extractive and evidence-focused, not a general LLM synthesizer

## Suggested Next Steps

- Replace local embeddings with a medical embedding model
- Use a real Qdrant collection via `qdrant-client`
- Add authentication and per-user document ownership
- Add richer PDF layout parsing and table extraction
- Add citation page mapping and answer confidence calibration
