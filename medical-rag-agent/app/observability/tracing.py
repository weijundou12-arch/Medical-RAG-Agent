from __future__ import annotations

import uuid
from contextvars import ContextVar
from contextlib import contextmanager
from time import perf_counter

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    _provider = TracerProvider()
    _provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(_provider)
    tracer = trace.get_tracer("medical-rag-agent")
except Exception:  # pragma: no cover - optional dependency behavior
    tracer = None


def new_trace_id() -> str:
    trace_id = uuid.uuid4().hex[:16]
    trace_id_var.set(trace_id)
    return trace_id


def get_trace_id() -> str:
    current = trace_id_var.get()
    if not current:
        current = new_trace_id()
    return current


@contextmanager
def span(name: str):
    start = perf_counter()
    if tracer:
        with tracer.start_as_current_span(name):
            yield {"name": name, "trace_id": get_trace_id(), "elapsed_ms": lambda: int((perf_counter() - start) * 1000)}
    else:
        yield {"name": name, "trace_id": get_trace_id(), "elapsed_ms": lambda: int((perf_counter() - start) * 1000)}
