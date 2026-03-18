from app.tools.chunk_document import chunk_document
from app.tools.embed_chunks import embed_text
from app.tools.generate_grounded_answer import generate_grounded_answer


def test_chunk_document_produces_chunks():
    text = "This is a medical guideline paragraph. " * 80
    chunks = chunk_document(text, chunk_size=30, overlap=5)
    assert len(chunks) >= 2
    assert chunks[0]["chunk_id"].startswith("chunk_")


def test_embed_text_dimension():
    vec = embed_text("Heart failure treatment and risk stratification")
    assert len(vec) == 128
    assert abs(sum(x * x for x in vec) - 1.0) < 1e-6


def test_generate_grounded_answer_returns_citations():
    retrieved = [
        {
            "score": 0.95,
            "payload": {
                "chunk_id": "chunk_0001",
                "text": "Aspirin is recommended for secondary prevention after myocardial infarction.",
                "metadata": {"page": 1},
            },
        }
    ]
    answer, citations = generate_grounded_answer("What is recommended after myocardial infarction?", retrieved)
    assert "myocardial infarction" in answer.lower()
    assert citations[0]["chunk_id"] == "chunk_0001"
