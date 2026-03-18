from __future__ import annotations

import os

try:
    from celery import Celery

    celery_app = Celery(
        "medical_rag_agent",
        broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
        backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1"),
    )
except Exception:  # pragma: no cover
    class _DummyCelery:
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    celery_app = _DummyCelery()
